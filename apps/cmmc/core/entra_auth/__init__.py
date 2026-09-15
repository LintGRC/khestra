"""Microsoft Entra ID (Azure AD) authentication for platform RBAC."""

from entra_auth.config import auth_enabled, public_auth_config
from entra_auth.context import get_auth_user, set_auth_user
from entra_auth.user import AuthUser, resolve_role_from_claims, user_from_claims

__all__ = [
    "AuthUser",
    "auth_enabled",
    "get_auth_user",
    "public_auth_config",
    "resolve_role_from_claims",
    "set_auth_user",
    "user_from_claims",
]
