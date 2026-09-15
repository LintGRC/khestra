"""Pre-export readiness checks for SSP and POA&M generation."""

from typing import Any, Dict, List

from controls import CMMC_FRAMEWORK

PROFILE_FIELDS = {
    "system_description": "System description",
    "architecture_summary": "Architecture summary",
    "boundary_description": "System boundary",
    "system_owner": "System owner",
    "iso_name": "Information security officer",
}


def evaluate_report_readiness(
    answers: Dict[str, Any],
    org_profile: Dict[str, str],
    scoped_controls: List[str],
) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    org_name = (org_profile.get("org_name") or "").strip()
    if not org_name or org_name.lower() in ("your organization", "organization"):
        blockers.append("Set organization name in System Profile.")

    for field, label in PROFILE_FIELDS.items():
        if not (org_profile.get(field) or "").strip():
            warnings.append(f"Missing {label} — SSP will include a placeholder.")

    scoped = [cid for cid in scoped_controls if cid in answers]
    met_or_na = {"MET", "NOT APPLICABLE", "INHERITED"}
    missing_narrative = []
    open_gaps = []
    needs_narrative: List[str] = []

    for cid in scoped:
        ans = answers[cid]
        status = ans.get("status", "NOT STARTED")
        narrative = (
            ans.get("implementation_narrative", "").strip()
            or ans.get("assessor_notes", "").strip()
        )
        if status in met_or_na:
            needs_narrative.append(cid)
            if not narrative:
                missing_narrative.append(cid)
        if status not in met_or_na:
            open_gaps.append(cid)

    if missing_narrative:
        warnings.append(
            f"{len(missing_narrative)} MET/INHERITED/NA controls lack an implementation narrative."
        )

    assessed = sum(1 for cid in scoped if answers[cid].get("status") != "NOT STARTED")
    if assessed == 0:
        blockers.append("No controls have been assessed yet.")

    profile_filled = sum(1 for f in PROFILE_FIELDS if (org_profile.get(f) or "").strip())
    profile_score = round(profile_filled / len(PROFILE_FIELDS) * 100)
    if needs_narrative:
        narrative_filled = len(needs_narrative) - len(missing_narrative)
        narrative_score = round(100 * narrative_filled / len(needs_narrative))
    else:
        narrative_score = 0
    assessment_score = round(assessed / len(scoped) * 100) if scoped else 0

    overall = round((profile_score * 0.25) + (narrative_score * 0.45) + (assessment_score * 0.30))

    return {
        "score": overall,
        "profile_score": profile_score,
        "narrative_score": narrative_score,
        "assessment_score": assessment_score,
        "blockers": blockers,
        "warnings": warnings,
        "missing_narrative_count": len(missing_narrative),
        "missing_narrative_sample": missing_narrative[:8],
        "open_gap_count": len(open_gaps),
        "scoped_control_count": len(scoped),
        "export_allowed": len(blockers) == 0,
    }
