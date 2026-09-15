"""Link incidents to readiness assessment — flag controls with active incidents."""

from __future__ import annotations

from typing import Any, Dict


def get_active_incidents_by_control() -> Dict[str, int]:
    """Return a dict mapping control_id to count of active (non-closed) incidents."""
    try:
        from incidents.store import list_incidents
    except ImportError:
        return {}

    active_statuses = {"triage", "investigation", "containment", "root_cause_analysis", "remediation"}
    result: Dict[str, int] = {}
    try:
        items, _ = list_incidents()  # returns (items, total)
    except Exception:
        return {}

    for inc in items:
        if inc.get("status", "") in active_statuses:
            cid = inc.get("control_id", "")
            if cid:
                result[cid] = result.get(cid, 0) + 1
    return result
