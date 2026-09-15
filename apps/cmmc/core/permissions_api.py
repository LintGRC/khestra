"""Role capabilities for platform API — mirrors Streamlit check_permission logic."""

from __future__ import annotations

from app_config import ROLE_PERMISSIONS


def _perms(role: str) -> dict:
    return ROLE_PERMISSIONS.get(role, {})


def can_edit_controls(role: str) -> bool:
    """Admin / Assessor / CM / Engineer may edit control answers."""
    p = _perms(role)
    return bool(p.get("edit_controls")) or (
        role == "Engineer" and p.get("validate_evidence")
    )


def can_edit_org(role: str) -> bool:
    """Organization Admin / CM / Assessor may edit org profile."""
    if role in ("Organization Admin", "Compliance Manager", "Assessor"):
        return True
    return bool(_perms(role).get("edit_controls"))


def can_export(role: str) -> bool:
    return bool(_perms(role).get("export_data"))


def can_validate_config(role: str) -> bool:
    """Config file validation — editors and Engineer validate_evidence."""
    p = _perms(role)
    return bool(p.get("edit_controls") or p.get("validate_evidence"))


def can_view_dashboard(role: str) -> bool:
    p = _perms(role)
    if p.get("view_dashboard"):
        return True
    return role in ("Organization Admin", "Executive", "Compliance Manager", "Auditor")


def can_manage_users(role: str) -> bool:
    return bool(_perms(role).get("manage_users"))


def can_manage_billing(role: str) -> bool:
    return bool(_perms(role).get("manage_billing"))


def role_capabilities(role: str) -> dict:
    return {
        "edit_controls": can_edit_controls(role),
        "edit_org": can_edit_org(role),
        "export_data": can_export(role),
        "validate_config": can_validate_config(role),
        "view_dashboard": can_view_dashboard(role),
        "manage_users": can_manage_users(role),
        "manage_billing": can_manage_billing(role),
    }
