"""Sandbox access control — per-user organization isolation."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import HTTPException

from entra_auth.context import get_auth_user
from entra_auth.user import AuthUser
from org_membership import client_ids_for_user, membership_for_user, org_count_for_user
from sandbox_config import (
    sandbox_max_orgs_per_user,
    sandbox_mode,
    sandbox_platform_admin_group_id,
    sandbox_signup_group_id,
)


def is_platform_admin(user: AuthUser) -> bool:
    admin_group = sandbox_platform_admin_group_id()
    if not admin_group:
        return False
    return admin_group in user.groups


class OrgAccessError(PermissionError):
    """User authenticated but not a member of the organization."""


def enforce_org_access_for_workspace(client_id: str) -> None:
    """Called from workspace load/save — no-op when auth or sandbox is off."""
    if not sandbox_mode():
        return
    user = get_auth_user()
    if not user:
        return
    if is_platform_admin(user):
        return
    if not membership_for_user(user.oid, client_id):
        raise OrgAccessError("You do not have access to this organization")


def user_may_access_sandbox(user: AuthUser) -> bool:
    signup_group = sandbox_signup_group_id()
    if not signup_group:
        return True
    return signup_group in user.groups or is_platform_admin(user)


def require_sandbox_user() -> AuthUser:
    user = get_auth_user()
    if not user:
        raise HTTPException(401, "Authentication required")
    if sandbox_mode() and not user_may_access_sandbox(user):
        raise HTTPException(403, "You are not authorized for this sandbox environment")
    return user


def require_org_access(client_id: str) -> AuthUser:
    user = require_sandbox_user()
    if not sandbox_mode():
        return user
    try:
        enforce_org_access_for_workspace(client_id)
    except OrgAccessError as exc:
        raise HTTPException(403, str(exc)) from exc
    return user


def resolve_workspace_role(ws: Dict[str, Any], client_id: str) -> str:
    user = get_auth_user()
    if user and sandbox_mode():
        if is_platform_admin(user):
            return user.role
        membership = membership_for_user(user.oid, client_id)
        if membership:
            return membership.role
        raise HTTPException(403, "You do not have access to this organization")
    if user:
        return user.role
    return ws.get("current_role", "Assessor")


def filter_clients_for_user(all_clients: List[Dict[str, str]]) -> List[Dict[str, str]]:
    user = get_auth_user()
    if not sandbox_mode() or not user:
        return all_clients
    if is_platform_admin(user):
        return all_clients
    allowed = set(client_ids_for_user(user.oid))
    return [c for c in all_clients if c["id"] in allowed]


def user_needs_organization() -> bool:
    if not sandbox_mode():
        return False
    user = get_auth_user()
    if not user:
        return False
    if is_platform_admin(user):
        return False
    return org_count_for_user(user.oid) == 0


def assert_may_create_org(user: AuthUser) -> None:
    if org_count_for_user(user.oid) >= sandbox_max_orgs_per_user():
        raise HTTPException(
            400,
            f"Sandbox limit: {sandbox_max_orgs_per_user()} organization(s) per user",
        )
