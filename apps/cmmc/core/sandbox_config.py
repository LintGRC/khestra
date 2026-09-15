"""Public sandbox / demo environment flags."""

from __future__ import annotations

import os


def sandbox_mode() -> bool:
    return os.environ.get("CMMC_SANDBOX_MODE", "").strip().lower() in ("1", "true", "yes")


def sandbox_fixture_only() -> bool:
    """Force collector runs to use bundled fixtures (no live creds on shared sandbox)."""
    if os.environ.get("CMMC_SANDBOX_FIXTURE_ONLY", "").strip().lower() in ("0", "false", "no"):
        return False
    return sandbox_mode()


def sandbox_signup_group_id() -> str:
    """Optional Entra group — user must be a member to access the public sandbox."""
    return os.environ.get("CMMC_ENTRA_GROUP_SANDBOX", "").strip()


def sandbox_platform_admin_group_id() -> str:
    """Optional Entra group — members can access every organization (operator support)."""
    return os.environ.get("CMMC_ENTRA_GROUP_PLATFORM_ADMIN", "").strip()


def sandbox_creator_role() -> str:
    role = os.environ.get("CMMC_SANDBOX_CREATOR_ROLE", "Compliance Manager").strip()
    from app_config import USER_ROLES

    return role if role in USER_ROLES else "Compliance Manager"


def sandbox_max_orgs_per_user() -> int:
    raw = os.environ.get("CMMC_SANDBOX_MAX_ORGS_PER_USER", "3").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 3
