"""Authenticated user and Entra group → app role mapping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app_config import USER_ROLES
from entra_auth.config import (
    ROLE_PRIORITY,
    default_role,
    load_group_map,
    require_group_match,
)


@dataclass(frozen=True)
class AuthUser:
    oid: str
    name: str
    email: str
    role: str
    groups: List[str]
    app_roles: List[str]
    org_id: str = ""
    is_org_owner: bool = False
    is_msp: bool = False


def _claim_list(claims: Dict[str, Any], key: str) -> List[str]:
    raw = claims.get(key)
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(x) for x in raw]
    return []


def resolve_role_from_claims(claims: Dict[str, Any]) -> Optional[str]:
    """Map Entra groups / app roles to a single platform role."""
    group_map = load_group_map()
    groups = _claim_list(claims, "groups")
    app_roles = _claim_list(claims, "roles")

    matched: List[str] = []
    for gid in groups:
        role = group_map.get(gid)
        if role:
            matched.append(role)

    for app_role in app_roles:
        if app_role in USER_ROLES:
            matched.append(app_role)

    for role in ROLE_PRIORITY:
        if role in matched:
            return role

    if require_group_match():
        return None
    return default_role()


def user_from_claims(claims: Dict[str, Any]) -> AuthUser:
    role = resolve_role_from_claims(claims)
    if role is None:
        raise PermissionError("No CMMC role assigned — contact your administrator.")

    name = (
        str(claims.get("name") or "").strip()
        or str(claims.get("preferred_username") or "").strip()
        or str(claims.get("upn") or "").strip()
    )
    email = (
        str(claims.get("preferred_username") or "").strip()
        or str(claims.get("email") or "").strip()
        or str(claims.get("upn") or "").strip()
    )
    oid = str(claims.get("oid") or claims.get("sub") or "").strip()

    return AuthUser(
        oid=oid,
        name=name,
        email=email,
        role=role,
        groups=_claim_list(claims, "groups"),
        app_roles=_claim_list(claims, "roles"),
    )
