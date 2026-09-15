"""Persisted workspace flags (scope confirmed, etc.)."""


def resolve_scope_confirmed(loaded: dict) -> bool:
    """Load scope_confirmed from disk, with safe defaults for older saves."""
    if "scope_confirmed" in loaded:
        return bool(loaded["scope_confirmed"])

    org = (
        (loaded.get("org_profile") or {}).get("org_name")
        or loaded.get("org_name")
        or ""
    ).strip().lower()
    if org in ("", "your organization"):
        return False

    answers = loaded.get("answers") or {}
    assessed = sum(
        1
        for ans in answers.values()
        if (ans.get("status") or "NOT STARTED") != "NOT STARTED"
    )
    if assessed > 0:
        return True

    return loaded.get("asset_scope", {}).get("CUI Assets", 0) > 0
