"""Analytics payloads for platform API (no Streamlit)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from assessment_helpers import (
    calculate_readiness_percentage,
    generate_poam_entries,
    resolve_control_dependencies,
)
from controls import CMMC_FRAMEWORK
from family_progress import _family_rows
from sprs_engine import BASE_SCORE, calculate_detailed_sprs, control_deduction
from annex_weights import annex_weight


def build_analytics(answers: Dict[str, Any], scoped_controls: List[str]) -> Dict[str, Any]:
    detailed = calculate_detailed_sprs(answers, scoped_controls)
    met = sum(1 for cid in scoped_controls if answers.get(cid, {}).get("status") == "MET")
    assessed = sum(1 for cid in scoped_controls if answers.get(cid, {}).get("status") != "NOT STARTED")

    family_readiness: Dict[str, float] = {}
    for cid in scoped_controls:
        fam = CMMC_FRAMEWORK[cid]["family"]
        score = {"MET": 100, "PARTIALLY MET": 50, "IN PROGRESS": 25, "PLANNED": 10}.get(
            answers.get(cid, {}).get("status", "NOT STARTED"), 0
        )
        family_readiness.setdefault(fam, []).append(score)
    family_avg = {f: round(sum(v) / len(v), 1) for f, v in family_readiness.items()}

    poam_df = generate_poam_entries(answers, scoped_controls)
    severity_counts: Dict[str, int] = {}
    if not poam_df.empty:
        severity_counts = poam_df["Risk Severity"].value_counts().to_dict()

    families = _family_rows(answers, scoped_controls)
    return {
        "sprs": {
            "final_score": detailed["final_score"],
            "met": met,
            "assessed": assessed,
            "total": len(scoped_controls),
            "open_gaps": detailed["breakdown"]["total_gaps_count"],
            "penalties": detailed["penalties"],
            "breakdown": detailed["breakdown"],
            "critical_gaps": detailed["critical_gaps"][:20],
            "moderate_gaps": detailed["moderate_gaps"][:20],
            "low_gaps": detailed["low_gaps"][:20],
        },
        "family_progress": families,
        "family_readiness_pct": family_avg,
        "poam_by_severity": severity_counts,
    }


def build_remediation(answers: Dict[str, Any], scoped_controls: List[str], sprs_history: List[Dict]) -> Dict[str, Any]:
    poam_df = generate_poam_entries(answers, scoped_controls)
    detailed = calculate_detailed_sprs(answers, scoped_controls)

    try:
        total_cost = sum(
            float(answers[cid].get("estimated_cost", 0) or 0)
            for cid in scoped_controls
            if answers.get(cid, {}).get("status") not in ("MET", "NOT APPLICABLE", "INHERITED")
        )
    except (ValueError, TypeError):
        total_cost = 0.0

    unowned = 0
    schedule: List[Dict[str, str]] = []
    gaps_by_family: Dict[str, int] = {}

    if not poam_df.empty:
        unowned = int(poam_df[poam_df["Owner"].isin(["", "TBD"])].shape[0])
        for _, row in poam_df.iterrows():
            cid = row["Control ID"]
            fam = CMMC_FRAMEWORK.get(cid, {}).get("family", "Unknown")
            gaps_by_family[fam] = gaps_by_family.get(fam, 0) + 1
            target = str(row.get("Target Date", "") or "")
            overdue = False
            due_soon = False
            if target:
                try:
                    due = pd.to_datetime(target)
                    overdue = due < pd.Timestamp.now()
                    due_soon = not overdue and due < pd.Timestamp.now() + pd.Timedelta(days=30)
                except Exception:
                    pass
            schedule.append(
                {
                    "control_id": cid,
                    "severity": row["Risk Severity"],
                    "owner": row["Owner"] or "TBD",
                    "target_date": target or "Undetermined",
                    "remediation_steps": row["Remediation Steps"],
                    "status": row["Current Status"],
                    "overdue": overdue,
                    "due_soon": due_soon,
                }
            )

    projections: List[Dict[str, Any]] = []
    cum = detailed["final_score"]
    for cid in scoped_controls:
        status = answers.get(cid, {}).get("status", "NOT STARTED")
        if status in ("MET", "NOT APPLICABLE", "INHERITED"):
            continue
        recovery = control_deduction(cid, status, annex_weight(cid))
        if recovery <= 0:
            continue
        cum = min(BASE_SCORE, cum + recovery)
        projections.append(
            {
                "control_id": cid,
                "weight": recovery,
                "target_date": answers.get(cid, {}).get("target_date", "") or "Undetermined",
                "cumulative_score": cum,
            }
        )

    history = [
        {"timestamp": h.get("timestamp", ""), "score": h.get("score", 0)}
        for h in (sprs_history or [])
    ]

    return {
        "total_cost": total_cost,
        "unowned_gaps": unowned,
        "open_items": len(poam_df),
        "critical_count": int((poam_df["Risk Severity"] == "Critical").sum()) if not poam_df.empty else 0,
        "readiness_pct": calculate_readiness_percentage(answers, scoped_controls),
        "sprs_score": detailed["final_score"],
        "gaps_by_family": [{"family": k, "count": v} for k, v in sorted(gaps_by_family.items(), key=lambda x: -x[1])],
        "schedule": schedule,
        "burndown": projections,
        "sprs_history": history,
        "target_score": BASE_SCORE,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def control_meta(answers: Dict[str, Any], scoped_controls: List[str], control_id: str) -> Dict[str, Any]:
    from app_config import VALIDATION_RULES
    from risk_levels import combined_risk_level
    from sprs_engine import sprs_weight_label

    ans = answers.get(control_id, {})
    deps = resolve_control_dependencies(control_id)
    at_risk = [c for c in deps if answers.get(c, {}).get("status") != "MET"]
    rules = VALIDATION_RULES.get(control_id)
    status = ans.get("status", "NOT STARTED")
    closed = status in ("MET", "NOT APPLICABLE", "INHERITED")
    return {
        "dependencies": deps,
        "dependencies_at_risk": at_risk,
        "sprs_weight_label": sprs_weight_label(control_id),
        "at_risk_points": None if closed else sprs_weight_label(control_id),
        "validation_rules": rules,
        "risk_level": combined_risk_level(ans.get("likelihood", "Medium"), ans.get("impact", "Medium")),
    }
