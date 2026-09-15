"""Assessment navigation helpers — no Streamlit."""

from typing import Any, Dict, List, Optional

from controls import CMMC_FRAMEWORK
from user_journey import next_controls_to_review


def find_next_incomplete(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    family: Optional[str] = None,
) -> Optional[str]:
    pool = scoped_controls
    if family:
        pool = [c for c in scoped_controls if CMMC_FRAMEWORK[c]["family"] == family]
    if not pool:
        return None
    picks = next_controls_to_review(answers, pool, limit=1)
    if picks:
        return picks[0]
    for cid in pool:
        if answers.get(cid, {}).get("status") == "NOT STARTED":
            return cid
    for cid in pool:
        status = answers.get(cid, {}).get("status", "NOT STARTED")
        narrative = (answers.get(cid, {}) or {}).get("implementation_narrative", "").strip()
        if status == "MET" and not narrative:
            return cid
    return None


def priority_controls(answers: Dict[str, Any], scoped_controls: List[str], limit: int = 8) -> List[str]:
    return next_controls_to_review(answers, scoped_controls, limit=limit)
