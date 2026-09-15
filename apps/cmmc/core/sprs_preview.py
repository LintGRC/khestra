"""Preview SPRS score impact when a control status changes."""

from copy import deepcopy
from typing import Any, Dict, List

from sprs_engine import calculate_detailed_sprs


def preview_sprs_score(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    control_id: str,
    new_status: str,
) -> int:
    """SPRS final score if control_id were set to new_status."""
    trial = deepcopy(answers)
    if control_id not in trial:
        trial[control_id] = {"status": new_status}
    else:
        trial[control_id] = {**trial[control_id], "status": new_status}
    return calculate_detailed_sprs(trial, scoped_controls)["final_score"]


def format_sprs_delta(current: int, projected: int) -> str:
    delta = projected - current
    if delta > 0:
        return f"+{delta}"
    return str(delta)
