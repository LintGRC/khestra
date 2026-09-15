"""Pre-C3PAO self-readiness metrics and checklist."""

from typing import Any, Dict, List

from controls import CMMC_FRAMEWORK
from evidence_coverage import compute_evidence_coverage
from poam_eligibility import poam_eligibility
from report_readiness import evaluate_report_readiness
from sprs_engine import calculate_detailed_sprs, effective_status

# Heuristic thresholds for self-assessment before scheduling C3PAO
MIN_SPRS_SELF_READY = 80
MAX_OPEN_CRITICAL = 0
MIN_REPORT_READINESS = 70
MIN_EVIDENCE_COVERAGE = 30  # percent of MET controls with at least one evidence or examine ref

# Official 32 CFR 170.21 conditional-status threshold
CONDITIONAL_SPRS = 88


def build_control_ledger(
    answers: Dict[str, Any],
    scoped_controls: List[str],
) -> List[Dict[str, Any]]:
    """One row per scoped control: weight, status, deduction, evidence, POA&M eligibility."""
    from evidence_coverage import _has_evidence_or_examine
    from poam_eligibility import unmet_controls
    from sprs_engine import control_deduction

    unmet = set(unmet_controls(answers, scoped_controls))
    rows: List[Dict[str, Any]] = []
    for cid in scoped_controls:
        if cid not in CMMC_FRAMEWORK:
            continue
        ans = answers.get(cid)
        status = effective_status(ans) if ans else "NOT STARTED"
        weight = CMMC_FRAMEWORK[cid]["weight"]
        deduction = control_deduction(cid, status, weight)
        rows.append(
            {
                "control_id": cid,
                "family": CMMC_FRAMEWORK[cid]["family"],
                "name": CMMC_FRAMEWORK[cid]["name"],
                "weight": weight,
                "status": status,
                "answered": ans is not None,
                "deduction": deduction,
                "has_evidence": bool(ans and _has_evidence_or_examine(ans)),
                "assessment_ready": status == "MET" and bool(ans and _has_evidence_or_examine(ans)),
                "poam_eligible": cid in unmet,
            }
        )
    rows.sort(key=lambda r: (-r["weight"], r["control_id"]))
    return rows


def simulate_sprs(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    changes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """What-if: apply status changes to a copy of answers and recompute SPRS."""
    from copy import deepcopy

    sim = deepcopy(answers)
    applied: List[str] = []
    for ch in changes:
        cid = ch.get("control_id")
        new_status = ch.get("status")
        if not cid or not new_status:
            continue
        if cid not in CMMC_FRAMEWORK:
            continue
        ans = sim.setdefault(cid, {})
        ans["status"] = new_status
        applied.append(cid)

    current = calculate_detailed_sprs(answers, scoped_controls)
    projected = calculate_detailed_sprs(sim, scoped_controls)
    return {
        "current_score": current["final_score"],
        "projected_score": projected["final_score"],
        "delta": projected["final_score"] - current["final_score"],
        "applied_changes": applied,
        "projected_detail": projected,
    }


def _narrative(ans: dict) -> str:
    return (
        ans.get("implementation_narrative", "").strip()
        or ans.get("assessor_notes", "").strip()
    )


def evaluate_pre_c3pao_readiness(
    answers: Dict[str, Any],
    org_profile: Dict[str, str],
    asset_scope: Dict[str, Any],
    scoped_controls: List[str],
) -> Dict[str, Any]:
    report = evaluate_report_readiness(answers, org_profile, scoped_controls)
    sprs = calculate_detailed_sprs(answers, scoped_controls)
    evidence = compute_evidence_coverage(answers, scoped_controls)
    eligibility = poam_eligibility(answers, scoped_controls)
    scoped = [c for c in scoped_controls if c in answers]

    met_controls = [c for c in scoped if answers[c].get("status") == "MET"]
    open_critical = [
        c
        for c in scoped
        if answers[c].get("status") not in ("MET", "NOT APPLICABLE", "INHERITED")
        and CMMC_FRAMEWORK[c]["weight"] >= 5
    ]
    open_five_pt = [
        c for c in open_critical if c not in ("IA.L2-3.5.3", "SC.L2-3.13.11")
    ]
    # include variable-weight MFA/FIPS in critical open list via sprs critical_gaps

    evidence_met = 0
    for cid in met_controls:
        ans = answers[cid]
        if ans.get("evidence") or ans.get("examine", "").strip():
            evidence_met += 1
    evidence_pct = round((evidence_met / len(met_controls)) * 100, 1) if met_controls else 0

    assessed_pct = report["assessment_score"]
    sprs_score = sprs["final_score"]

    critical_done = len(open_critical) == 0
    critical_detail = (
        "All 5-point controls are MET, N/A, or inherited"
        if critical_done
        else f"{len(open_critical)} five-point control(s) still open — each can cost up to 5 SPRS points"
    )

    checklist = [
        {
            "item": "Organization profile complete",
            "done": report["profile_score"] >= 80,
            "detail": f"{report['profile_score']}% profile fields filled",
        },
        {
            "item": "All scoped controls assessed",
            "done": assessed_pct >= 95,
            "detail": f"{assessed_pct}% reviewed",
        },
        {
            "item": "5-point critical controls closed",
            "done": critical_done,
            "detail": critical_detail,
            "control_ids": open_critical[:12],
            "blocks_self_ready": True,
        },
        {
            "item": "SPRS score at or above target",
            "done": sprs_score >= MIN_SPRS_SELF_READY,
            "detail": f"Score {sprs_score}/110 (target ≥ {MIN_SPRS_SELF_READY})",
            "note": (
                "Score can meet target while 5-point gaps remain open"
                if sprs_score >= MIN_SPRS_SELF_READY and not critical_done
                else None
            ),
        },
        {
            "item": "Implementation narratives for MET controls",
            "done": report["narrative_score"] >= 85,
            "detail": f"{report['narrative_score']}% narrative coverage",
        },
        {
            "item": "Evidence / examine references on MET controls",
            "done": evidence_pct >= MIN_EVIDENCE_COVERAGE,
            "detail": f"{evidence_pct}% of MET controls have evidence or examine refs",
        },
        {
            "item": "SSP export readiness",
            "done": report["score"] >= MIN_REPORT_READINESS,
            "detail": f"Report readiness {report['score']}%",
        },
    ]

    done_count = sum(1 for c in checklist if c["done"])
    self_ready = (
        sprs_score >= MIN_SPRS_SELF_READY
        and len(open_critical) == 0
        and report["score"] >= MIN_REPORT_READINESS
        and done_count >= 5
    )

    remediation_priority = sorted(
        [
            c
            for c in scoped
            if answers[c].get("status") not in ("MET", "NOT APPLICABLE", "INHERITED")
        ],
        key=lambda cid: (-CMMC_FRAMEWORK[cid]["weight"], cid),
    )

    assessed_count = sum(1 for c in scoped if answers[c].get("status") != "NOT STARTED")

    return {
        **report,
        "sprs_score": sprs_score,
        "sprs_detail": sprs,
        "evidence_coverage_pct": evidence_pct,
        "assessment_ready_count": evidence["assessment_ready_count"],
        "assessment_ready_controls": [c for c, r in evidence["assessment_ready"].items() if r],
        "poam_eligibility": eligibility,
        "conditional_sprs": CONDITIONAL_SPRS,
        "unanswered_count": sprs["unanswered_count"],
        "unanswered_ids": sprs["unanswered_ids"],
        "open_critical_count": len(open_critical),
        "open_critical_ids": open_critical[:15],
        "checklist": checklist,
        "checklist_done": done_count,
        "checklist_total": len(checklist),
        "self_ready": self_ready,
        "remediation_priority": remediation_priority[:20],
        "controls_assessed": assessed_count,
        "controls_total": len(scoped),
    }
