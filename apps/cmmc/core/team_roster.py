"""Team roster and assignment helpers for in-app collaboration."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

KEY_PERSONNEL_FIELDS = (
    "system_owner",
    "iso_name",
    "sysadmin_name",
    "network_admin_name",
    "auditor_name",
)

_CLOSED_STATUSES = frozenset({"NOT APPLICABLE", "INHERITED"})


def parse_team_roster(org_profile: Dict[str, str]) -> List[str]:
    """Unique team names from key personnel fields plus optional team_roster lines."""
    seen: set[str] = set()
    members: List[str] = []

    def add(name: str) -> None:
        n = (name or "").strip()
        if not n:
            return
        key = n.lower()
        if key in seen:
            return
        seen.add(key)
        members.append(n)

    for field in KEY_PERSONNEL_FIELDS:
        add(org_profile.get(field, ""))

    raw = org_profile.get("team_roster", "") or ""
    for line in raw.replace(",", "\n").split("\n"):
        add(line)

    return members


def names_match(a: str, b: str) -> bool:
    return (a or "").strip().lower() == (b or "").strip().lower()


def has_implementation_narrative(ans: Dict[str, Any]) -> bool:
    return bool((ans.get("implementation_narrative") or "").strip())


def assignment_open(ans: Dict[str, Any]) -> bool:
    """True when assigned work on this control is not fully done."""
    status = (ans.get("status") or "NOT STARTED").strip().upper()
    if status in _CLOSED_STATUSES:
        return False
    if status == "MET":
        return not has_implementation_narrative(ans)
    return True


def target_date_overdue(target_date: str, status: str) -> bool:
    if status in ("MET", "NOT APPLICABLE", "INHERITED"):
        return False
    raw = (target_date or "").strip()
    if not raw:
        return False
    try:
        return date.fromisoformat(raw[:10]) < date.today()
    except ValueError:
        return False


def author_display_name(current_user_name: str, current_role: str) -> str:
    name = (current_user_name or "").strip()
    if name:
        return name
    return (current_role or "Assessor").strip() or "Assessor"


def my_work_rows(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    current_user_name: str,
) -> List[Dict[str, Any]]:
    from controls import CMMC_FRAMEWORK

    user = (current_user_name or "").strip()
    if not user:
        return []

    rows: List[Dict[str, Any]] = []
    for cid in scoped_controls:
        if cid not in CMMC_FRAMEWORK:
            continue
        ans = answers.get(cid, {})
        owner = (ans.get("owner") or "").strip()
        if not owner or not names_match(owner, user):
            continue
        if not assignment_open(ans):
            continue
        info = CMMC_FRAMEWORK[cid]
        status = ans.get("status", "NOT STARTED")
        rows.append(
            {
                "id": cid,
                "family": info["family"],
                "name": info["name"][:80],
                "status": status,
                "owner": owner,
                "target_date": ans.get("target_date", ""),
                "overdue": target_date_overdue(ans.get("target_date", ""), status),
                "has_narrative": has_implementation_narrative(ans),
                "comment_count": len(ans.get("comments") or []),
            }
        )

    rows.sort(key=lambda r: (not r["overdue"], r["id"]))
    return rows
