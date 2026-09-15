"""Load helpers without Streamlit."""

from typing import Any, Dict, Optional

from catalog_migration import migrate_answers
from controls import CMMC_FRAMEWORK
from org_profile import merge_control_answer


def answers_from_saved(saved_answers: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    migrated = migrate_answers(saved_answers or {})
    return {cid: merge_control_answer(migrated.get(cid)) for cid in CMMC_FRAMEWORK}
