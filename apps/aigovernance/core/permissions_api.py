"""Role capabilities for AI Governance — mirrors SOC2 pattern."""

from __future__ import annotations

from app_config import ROLE_PERMISSIONS


def _perms(role: str) -> dict:
    return ROLE_PERMISSIONS.get(role, {})


def can_edit_controls(role: str) -> bool:
    return bool(_perms(role).get("edit_controls"))


def can_edit_org(role: str) -> bool:
    return bool(_perms(role).get("edit_org"))


def can_export(role: str) -> bool:
    return bool(_perms(role).get("export_data"))


def role_capabilities(role: str) -> dict:
    return {
        "edit_controls": can_edit_controls(role),
        "edit_org": can_edit_org(role),
        "export_data": can_export(role),
    }
