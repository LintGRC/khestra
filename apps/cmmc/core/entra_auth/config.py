"""Entra ID auth configuration from environment."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from app_config import USER_ROLES

ROLE_PRIORITY: List[str] = [
    "Organization Admin",
    "Compliance Manager",
    "Assessor",
    "Auditor",
    "Executive",
    "Engineer",
]

_PUBLIC_PATHS = frozenset(
    {
        "/api/health",
        "/api/auth/config",
        "/api/auth/login",
        "/api/collectors/health",
    }
)


def tenant_id() -> str:
    return (
        os.environ.get("CMMC_ENTRA_TENANT_ID", "").strip()
        or os.environ.get("AZURE_TENANT_ID", "").strip()
    )


def client_id() -> str:
    return (
        os.environ.get("CMMC_ENTRA_CLIENT_ID", "").strip()
        or os.environ.get("AZURE_CLIENT_ID", "").strip()
    )


def auth_enabled() -> bool:
    return auth_mode() != "none"


def _auth_secret_file() -> str:
    from config import DATA_DIR
    auth_db = os.environ.get("AUTH_DB_PATH", "").strip()
    if auth_db:
        # Mirror auth.jwt.init_secret(): the shared secret lives next to the
        # shared auth DB so every service reads the same identity.
        return str(Path(auth_db).parent / "auth_secret")
    return str(Path(DATA_DIR) / "auth_secret")


def auth_mode() -> str:
    """Returns 'entra', 'local', or 'none'."""
    explicit = os.environ.get("CMMC_AUTH_MODE", "").strip().lower()
    if explicit in ("entra",):
        if not tenant_id() or not client_id():
            return "none"
        return "entra"
    if explicit in ("local",):
        return "local"
    if explicit in ("none", "0", "false", "no"):
        return "none"
    explicit_entra = os.environ.get("CMMC_ENTRA_AUTH_ENABLED", "").strip().lower()
    if explicit_entra in ("0", "false", "no"):
        return "none"
    if tenant_id() and client_id():
        return "entra"
    if os.environ.get("CMMC_AUTH_SECRET", "").strip():
        return "local"
    if Path(_auth_secret_file()).is_file():
        return "local"
    return "none"


def require_group_match() -> bool:
    return os.environ.get("CMMC_ENTRA_REQUIRE_GROUP", "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )


def default_role() -> str:
    role = os.environ.get("CMMC_ENTRA_DEFAULT_ROLE", "Assessor").strip()
    return role if role in USER_ROLES else "Assessor"


def api_audiences() -> List[str]:
    cid = client_id()
    if not cid:
        return []
    configured = os.environ.get("CMMC_ENTRA_API_AUDIENCE", "").strip()
    if configured:
        return [a.strip() for a in configured.split(",") if a.strip()]
    return [cid, f"api://{cid}"]


def api_scopes() -> List[str]:
    cid = client_id()
    custom = os.environ.get("CMMC_ENTRA_API_SCOPE", "").strip()
    if custom:
        return [custom]
    if not cid:
        return []
    return [f"api://{cid}/access_as_user"]


def issuer() -> str:
    return f"https://login.microsoftonline.com/{tenant_id()}/v2.0"


def jwks_url() -> str:
    return f"https://login.microsoftonline.com/{tenant_id()}/discovery/v2.0/keys"


def load_group_map() -> Dict[str, str]:
    raw = os.environ.get("CMMC_ENTRA_GROUP_MAP", "").strip()
    if raw:
        parsed = json.loads(raw)
        return {str(k): str(v) for k, v in parsed.items() if str(v) in USER_ROLES}

    mapping: Dict[str, str] = {}
    for role in USER_ROLES:
        env_key = f"CMMC_ENTRA_GROUP_{role.upper().replace(' ', '_')}"
        guid = os.environ.get(env_key, "").strip()
        if guid:
            mapping[guid] = role
    return mapping


def is_public_api_path(path: str) -> bool:
    if path in _PUBLIC_PATHS:
        return True
    if path.startswith("/api/webhook/"):
        return True
    return False


from sandbox_config import sandbox_fixture_only, sandbox_mode


def public_auth_config() -> Dict[str, Any]:
    mode = auth_mode()
    auth_active = auth_enabled()
    cid = client_id()
    return {
        "enabled": auth_active,
        "mode": mode,
        "tenant_id": tenant_id() if mode == "entra" else "",
        "client_id": cid if mode == "entra" else "",
        "scopes": api_scopes() if mode == "entra" else [],
        "role_locked": mode == "entra",
        "login_hint": os.environ.get("CMMC_ENTRA_LOGIN_HINT", "").strip() if mode == "entra" else "",
        "sandbox_mode": sandbox_mode(),
        "sandbox_fixture_only": sandbox_fixture_only(),
    }
