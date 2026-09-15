"""POA&M eligibility per 32 CFR 170.21 (CMMC Level 2 conditional status).

Conditional status rules implemented:
- SPRS score >= 88 (0.8 x 110)
- Every unmet requirement must carry a <= 1-point deduction
- §170.21(a)(2)(iii) hard-blocks: AC.L2-3.1.20, AC.L2-3.1.22, CA.L2-3.12.4,
  PE.L2-3.10.3, PE.L2-3.10.4, PE.L2-3.10.5 may never ride a POA&M
- SC.L2-3.13.11 (FIPS-validated cryptography) exception: may ride a POA&M at
  3 points when encryption is employed but not FIPS-validated (PARTIALLY MET)
- MFA (IA.L2-3.5.3) at any gap blocks eligibility
- Unjustified N/A is scored as unmet (see sprs_engine)
- 180-day closeout window for self-assessment POA&Ms
"""

from __future__ import annotations

from typing import Any, Dict, List

from annex_weights import annex_weight
from official_170 import POAM_FORBIDDEN_LEVEL2  # noqa: E402  (§170.21(a)(2)(iii))
from sprs_engine import (
    calculate_detailed_sprs,
    GAP_STATUSES,
    VARIABLE_WEIGHT_CONTROLS,
)

CONDITIONAL_SCORE = 88
POAM_CLOSEOUT_DAYS = 180
FIPS_POAM_EXCEPTION = "SC.L2-3.13.11"

MET_STATUSES = frozenset({"MET", "INHERITED"})


def unmet_controls(answers: Dict[str, Any], scoped_controls: List[str]) -> List[str]:
    """Scoped controls that would incur an SPRS deduction (incl. unjustified N/A)."""
    out: List[str] = []
    for cid in scoped_controls:
        ans = answers.get(cid, {})
        status = ans.get("status", "NOT STARTED")
        if status in MET_STATUSES:
            continue
        if status == "NOT APPLICABLE":
            if not (ans.get("justification") or "").strip():
                out.append(cid)
            continue
        if status in GAP_STATUSES or status == "PARTIALLY MET":
            out.append(cid)
    return out


def poam_eligibility(
    answers: Dict[str, Any],
    scoped_controls: List[str],
) -> Dict[str, Any]:
    """Determine 170.21 conditional-status eligibility for the gap set."""
    sprs = calculate_detailed_sprs(answers, scoped_controls)
    score = sprs["final_score"]
    unmet = unmet_controls(answers, scoped_controls)

    eligible_ids: List[str] = []
    blocking_ids: List[str] = []
    for cid in unmet:
        status = (answers.get(cid) or {}).get("status", "NOT STARTED")
        # §170.21(a)(2)(iii): six requirements may NEVER be placed on a Level 2
        # POA&M, regardless of point value or partial-met status.
        if cid in POAM_FORBIDDEN_LEVEL2:
            blocking_ids.append(cid)
            continue
        if cid == FIPS_POAM_EXCEPTION and status == "PARTIALLY MET":
            eligible_ids.append(cid)
            continue
        if cid in VARIABLE_WEIGHT_CONTROLS:
            blocking_ids.append(cid)
            continue
        if annex_weight(cid) <= 1:
            eligible_ids.append(cid)
        else:
            blocking_ids.append(cid)

    score_ok = score >= CONDITIONAL_SCORE
    eligible = score_ok and not blocking_ids

    if eligible:
        reason = (
            f"Conditional status available: SPRS {score} >= {CONDITIONAL_SCORE} "
            "with only POA&M-eligible gaps (FIPS 3-point exception applied where relevant)"
        )
    elif not score_ok:
        reason = f"SPRS {score} is below the {CONDITIONAL_SCORE} conditional-status threshold"
    else:
        reason = (
            f"{len(blocking_ids)} requirement(s) not POA&M-eligible at current status: "
            + ", ".join(blocking_ids[:8])
        )

    return {
        "eligible": eligible,
        "score": score,
        "threshold": CONDITIONAL_SCORE,
        "eligible_ids": eligible_ids,
        "blocking_ids": blocking_ids,
        "unmet_count": len(unmet),
        "closeout_days": POAM_CLOSEOUT_DAYS,
        "reason": reason,
    }
