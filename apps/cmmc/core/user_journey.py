"""
User journey — where they are, what's next, and progress through the assessment.

Designed for SME users with no dedicated compliance staff: one obvious next step at a time.
"""

from typing import Any, Dict, List, Optional

from controls import CMMC_FRAMEWORK
from report_readiness import evaluate_report_readiness
from sprs_engine import calculate_detailed_sprs


JOURNEY_STEPS = [
    {
        "id": "profile",
        "label": "Describe your org",
        "view": "System Profile",
        "hint": "Add org name, system description, architecture, and key roles. This text flows into your SSP.",
        "min_profile_pct": 60,
    },
    {
        "id": "scope",
        "label": "Confirm scope",
        "view": "System Profile",
        "hint": "On **Organization**, set **CUI Assets** to 100% if you handle CUI, then click **Apply scope**.",
    },
    {
        "id": "assess",
        "label": "Review controls",
        "view": "Assessment",
        "hint": "Set status for each control. Start with 5-point gaps shown on the dashboard.",
        "min_assessed_pct": 90,
    },
    {
        "id": "narratives",
        "label": "Write narratives",
        "view": "Assessment",
        "hint": "MET controls need a short narrative for SSP export. Use catalog guidance on each control card — one control at a time.",
        "min_narrative_pct": 70,
    },
    {
        "id": "evidence",
        "label": "Link evidence",
        "view": "Assessment",
        "hint": "Attach policies, configs, or tickets per control. Files stay on this machine only.",
        "optional": True,
    },
    {
        "id": "export",
        "label": "Export SSP/POA&M",
        "view": "Report Center",
        "hint": "Generate Word and CSV drafts. Review every page before audit or SPRS submission.",
        "min_report_pct": 50,
    },
    {
        "id": "sprs",
        "label": "Prepare SPRS",
        "view": "Pre-C3PAO Readiness",
        "hint": "Copy the SPRS Entry Summary into PIEE manually when your organization is ready.",
        "optional": True,
    },
]


def _is_demo_org(org_profile: Dict[str, str]) -> bool:
    name = (org_profile.get("org_name") or "").lower()
    return "apex defense" in name or "demo" in name


def _scope_step_done(asset_scope: Dict[str, Any], scope_confirmed: bool = False) -> bool:
    return bool(scope_confirmed)


def compute_user_journey(
    answers: Dict[str, Any],
    org_profile: Dict[str, str],
    asset_scope: Dict[str, Any],
    scoped_controls: List[str],
    scope_confirmed: bool = False,
) -> Dict[str, Any]:
    report = evaluate_report_readiness(answers, org_profile, scoped_controls)
    sprs = calculate_detailed_sprs(answers, scoped_controls)
    scoped = [c for c in scoped_controls if c in answers]

    met = [c for c in scoped if answers[c].get("status") == "MET"]
    with_evidence = sum(
        1
        for c in met
        if answers[c].get("evidence") or (answers[c].get("examine") or "").strip()
    )
    evidence_pct = round(100 * with_evidence / len(met)) if met else 0

    org_ok = report["profile_score"] >= 60 and not (
        (org_profile.get("org_name") or "").strip().lower() in ("", "your organization")
    )
    scope_ok = _scope_step_done(asset_scope, scope_confirmed)
    assess_ok = report["assessment_score"] >= 90
    narrative_ok = report["narrative_score"] >= 70
    export_ok = report["score"] >= 50 and not report["blockers"]
    sprs_ok = sprs["final_score"] >= 70 and assess_ok

    step_done = {
        "profile": org_ok,
        "scope": scope_ok,
        "assess": assess_ok,
        "narratives": narrative_ok,
        "evidence": evidence_pct >= 25 if met else False,
        "export": export_ok,
        "sprs": sprs_ok,
    }

    steps_out = []
    for step in JOURNEY_STEPS:
        done = step_done.get(step["id"], False)
        steps_out.append({**step, "done": done})

    required = [s for s in steps_out if not s.get("optional")]
    required_done = sum(1 for s in required if s["done"])
    progress_pct = round(100 * required_done / len(required)) if required else 0

    next_step: Optional[Dict[str, Any]] = None
    for s in steps_out:
        if not s["done"] and not s.get("optional"):
            next_step = s
            break
    if not next_step:
        for s in steps_out:
            if not s["done"]:
                next_step = s
                break

    open_critical = len(sprs.get("critical_gaps") or [])

    return {
        "steps": steps_out,
        "progress_pct": progress_pct,
        "next_step": next_step,
        "report": report,
        "sprs_score": sprs["final_score"],
        "open_critical": open_critical,
        "is_new_user": report["assessment_score"] < 5 and not _is_demo_org(org_profile),
        "metrics": {
            "profile_pct": report["profile_score"],
            "assessed_pct": report["assessment_score"],
            "narrative_pct": report["narrative_score"],
            "report_pct": report["score"],
            "evidence_pct": evidence_pct,
        },
    }


def next_controls_to_review(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    limit: Optional[int] = 5,
) -> List[str]:
    """Controls to tackle next: open 5-point first, then other gaps, then not started."""
    from annex_weights import annex_weight

    open_gaps = []
    not_started = []
    for cid in scoped_controls:
        status = answers.get(cid, {}).get("status", "NOT STARTED")
        if status in ("MET", "NOT APPLICABLE", "INHERITED"):
            continue
        w = annex_weight(cid)
        if status == "NOT STARTED":
            not_started.append((cid, w))
        else:
            open_gaps.append((cid, w))
    open_gaps.sort(key=lambda x: (-x[1], x[0]))
    not_started.sort(key=lambda x: (-x[1], x[0]))
    ordered = [c for c, _ in open_gaps] + [c for c, _ in not_started]
    if limit is None:
        return ordered
    return ordered[:limit]
