"""
SPRS scoring engine aligned with the DoW NIST SP 800-171 Assessment Methodology.

Per-control weights follow the standard 5 / 3 / 1 subtractor model. Controls
3.5.3 (MFA) and 3.13.11 (FIPS-validated cryptography) use variable deductions
(5 or 3 points) instead of catalog weights — they are not penalized twice.
"""

from typing import Any, Dict, List, Optional

from annex_weights import annex_weight, is_sprs_scorable
from controls import CMMC_FRAMEWORK

BASE_SCORE = 110
MIN_SCORE = -203

# DoW variable-weight controls (methodology section on partial implementation).
VARIABLE_WEIGHT_CONTROLS = {
    "IA.L2-3.5.3": "mfa",
    "SC.L2-3.13.11": "fips",
}

GAP_STATUSES = frozenset(
    {"NOT MET", "NOT STARTED", "PLANNED", "IN PROGRESS", "PARTIALLY MET"}
)
EXCLUDED_STATUSES = frozenset({"MET", "INHERITED", "NOT APPLICABLE"})


def variable_deduction(control_id: str, status: str) -> int:
    """Return DoW deduction for MFA/FIPS controls, or 0 if satisfied."""
    if status in EXCLUDED_STATUSES:
        return 0
    if status == "PARTIALLY MET":
        return 3
    if status in GAP_STATUSES:
        return 5
    return 0


def control_deduction(control_id: str, status: str, catalog_weight: int) -> int:
    """Return points to subtract for a single control."""
    if not is_sprs_scorable(control_id):
        return 0
    if status in EXCLUDED_STATUSES:
        return 0
    if control_id in VARIABLE_WEIGHT_CONTROLS:
        return variable_deduction(control_id, status)
    if status in GAP_STATUSES:
        return annex_weight(control_id)
    return 0


def effective_status(ans: Dict[str, Any]) -> str:
    """Normalize a control answer to its scoring status.

    - Unanswered / missing answers score as NOT STARTED (never silently met).
    - N/A without a written justification scores as NOT MET (unjustified N/A
      is treated as unimplemented, matching C3PAO practice).
    """
    if not ans:
        return "NOT STARTED"
    status = ans.get("status", "NOT STARTED")
    if status == "NOT APPLICABLE" and not (ans.get("justification") or "").strip():
        return "NOT MET"
    return status


def calculate_detailed_sprs(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    framework: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Compute SPRS score and breakdown for scoped controls.

    Returns final_score (floored at MIN_SCORE), penalty counts, gap lists,
    per-category deduction totals, and the unanswered count (unanswered
    controls are scored as NOT STARTED — never silently skipped).
    """
    catalog = framework or CMMC_FRAMEWORK
    score = BASE_SCORE
    penalties = {"5pt": 0, "3pt": 0, "1pt": 0}
    critical_gaps: List[str] = []
    moderate_gaps: List[str] = []
    low_gaps: List[str] = []
    variable_details: Dict[str, int] = {}
    unanswered: List[str] = []

    for cid in scoped_controls:
        if cid not in catalog:
            continue

        ans = answers.get(cid)
        if ans is None:
            unanswered.append(cid)
        status = effective_status(ans)
        weight = annex_weight(cid)
        deduction = control_deduction(cid, status, weight)

        if deduction == 0:
            continue

        score -= deduction

        if cid in VARIABLE_WEIGHT_CONTROLS:
            variable_details[cid] = deduction
            if deduction == 5:
                penalties["5pt"] += 1
                critical_gaps.append(cid)
            else:
                penalties["3pt"] += 1
                moderate_gaps.append(cid)
        elif deduction == 5:
            penalties["5pt"] += 1
            critical_gaps.append(cid)
        elif deduction == 3:
            penalties["3pt"] += 1
            moderate_gaps.append(cid)
        elif deduction == 1:
            penalties["1pt"] += 1
            low_gaps.append(cid)

    mfa_deduction = variable_details.get("IA.L2-3.5.3", 0)
    fips_deduction = variable_details.get("SC.L2-3.13.11", 0)

    return {
        "final_score": max(MIN_SCORE, score),
        "penalties": penalties,
        "critical_gaps": critical_gaps,
        "moderate_gaps": moderate_gaps,
        "low_gaps": low_gaps,
        "mfa_deduction": mfa_deduction,
        "fips_deduction": fips_deduction,
        "unanswered_count": len(unanswered),
        "unanswered_ids": unanswered,
        "answered_count": len(scoped_controls) - len(unanswered),
        "breakdown": {
            "base": BASE_SCORE,
            "5pt_deductions": penalties["5pt"] * 5,
            "3pt_deductions": penalties["3pt"] * 3,
            "1pt_deductions": penalties["1pt"] * 1,
            "mfa_variable": mfa_deduction,
            "fips_variable": fips_deduction,
            "total_gaps_count": len(critical_gaps) + len(moderate_gaps) + len(low_gaps),
        },
    }


def sprs_weight_label(control_id: str) -> str:
    """Display hint for variable-weight controls in the UI."""
    if control_id in VARIABLE_WEIGHT_CONTROLS:
        return "5 or 3 (DoW variable)"
    weight = annex_weight(control_id)
    return str(weight)
