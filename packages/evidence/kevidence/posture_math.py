"""Shared posture rollup math (open side, `docs/OPEN_CORE_CONTRACT.md` §A6).

One rollup engine, two feeds: the closed `build_framework_posture` and the
open manual-posture path both call these helpers. Never fork the rollup.
"""

from __future__ import annotations

from typing import List


def rollup_statuses(statuses: List[str]) -> str:
    """Roll up check statuses to one badge: fail > error > warn > partial > pass > uncollected."""
    if not statuses:
        return "uncollected"
    if any(s == "fail" for s in statuses):
        return "fail"
    if any(s == "error" for s in statuses):
        return "error"
    if any(s == "warn" for s in statuses):
        return "warn"
    if any(s == "pass" for s in statuses) and any(s != "pass" for s in statuses):
        return "partial"
    if all(s == "pass" for s in statuses):
        return "pass"
    return "uncollected"
