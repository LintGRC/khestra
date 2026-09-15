"""Load filtered data from shared modules for SSP rendering."""

from __future__ import annotations

from typing import Any, Dict, List

from team_roster import KEY_PERSONNEL_FIELDS


ROLE_FIELD_MAP: Dict[str, List[str]] = {
    "DomainAdmin": ["sysadmin_name", "network_admin_name"],
    "PrivilegedUser": ["system_owner", "sysadmin_name", "network_admin_name"],
    "SeparateDuty": ["iso_name", "auditor_name"],
    "AllStaff": list(KEY_PERSONNEL_FIELDS),
}


def load_profile_team(org_profile: Dict[str, Any], role: str, _expect: str) -> List[Dict[str, str]]:
    """Return team members matching a role category from the org profile."""
    fields = ROLE_FIELD_MAP.get(role, list(KEY_PERSONNEL_FIELDS))
    seen: set[str] = set()
    members: List[Dict[str, str]] = []
    for field in fields:
        name = (org_profile.get(field, "") or "").strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        members.append({"name": name, "role": field.replace("_name", "").replace("_", " ").title()})
    return members


def load_inventory_assets(org_inventory: Dict[str, Any] | None, field: str, expect: str) -> List[Dict[str, str]]:
    """Return inventory rows matching a filter condition."""
    assets = (org_inventory or {}).get("assets", []) or []
    if not expect:
        return assets
    result = []
    for row in assets:
        val = (row.get(field, "") or "").strip().lower()
        if val == expect.lower():
            result.append(row)
    return result


def load_policies(policies_db_path: str | None, topic: str, label: str) -> List[Dict[str, str]]:
    """Return policies matching a topic tag from the policies store."""
    try:
        from policies.store import _get_db
    except ImportError:
        return []
    import json
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT id, title, status, version, updated_at, framework_tags FROM documents ORDER BY updated_at DESC"
        ).fetchall()
        matches = []
        for row in rows:
            tags = []
            try:
                tags = json.loads(row["framework_tags"]) if row["framework_tags"] else []
            except (json.JSONDecodeError, TypeError):
                tags = []
            tag_text = " ".join(tags).lower()
            if topic.lower() in tag_text or topic.lower() in (row["title"] or "").lower():
                matches.append({
                    "id": row["id"],
                    "title": row["title"],
                    "status": row["status"],
                    "version": row["version"],
                    "updated_at": row["updated_at"] or "",
                })
        return matches
    finally:
        db.close()


def load_for_control(
    rule: Dict[str, Any],
    org_profile: Dict[str, Any],
    org_inventory: Dict[str, Any] | None,
) -> List[Dict[str, str]]:
    """Dispatch a single ssp_rule to the correct loader."""
    source = rule.get("source", "")
    if source == "profile":
        return load_profile_team(org_profile, rule.get("expect", ""), rule.get("expect", ""))
    elif source == "inventory":
        return load_inventory_assets(org_inventory, rule.get("field", ""), rule.get("expect", ""))
    elif source == "policies":
        return load_policies(None, rule.get("topic", ""), rule.get("label", ""))
    return []
