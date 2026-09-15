"""Local JWT creation and validation using PyJWT."""

from __future__ import annotations

import os
import stat
import time
from pathlib import Path

import jwt


_SECRET_PATH: str | None = None
_SECRET_CACHED: str | None = None
_SECRET_FROM_ENV: str | None = None


def _secret() -> str:
    global _SECRET_CACHED
    if _SECRET_CACHED:
        return _SECRET_CACHED
    if _SECRET_FROM_ENV:
        _SECRET_CACHED = _SECRET_FROM_ENV
        return _SECRET_CACHED
    raw = os.environ.get("CMMC_AUTH_SECRET", "").strip()
    if raw:
        _SECRET_CACHED = raw
        return _SECRET_CACHED
    if _SECRET_PATH and Path(_SECRET_PATH).is_file():
        _SECRET_CACHED = Path(_SECRET_PATH).read_text().strip()
        return _SECRET_CACHED
    raise RuntimeError("No JWT secret configured — set CMMC_AUTH_SECRET or run init_secret()")


def _secret_file_path(data_dir: str) -> str:
    """Prefer auth_secret next to shared AUTH_DB_PATH when set."""
    auth_db = os.environ.get("AUTH_DB_PATH", "").strip()
    if auth_db:
        return str(Path(auth_db).parent / "auth_secret")
    return str(Path(data_dir) / "auth_secret")


def init_secret(data_dir: str) -> str:
    """Configure JWT signing secret.

    Preference order:
      1. CMMC_AUTH_SECRET env (required for multi-service / Docker)
      2. auth_secret file next to AUTH_DB_PATH (shared identity)
      3. auth_secret under the service data_dir
      4. generate a new file secret
    """
    global _SECRET_PATH, _SECRET_CACHED, _SECRET_FROM_ENV
    _SECRET_PATH = _secret_file_path(data_dir)

    raw = os.environ.get("CMMC_AUTH_SECRET", "").strip()
    if raw:
        _SECRET_FROM_ENV = raw
        _SECRET_CACHED = raw
        return _SECRET_PATH

    if Path(_SECRET_PATH).is_file():
        _SECRET_CACHED = Path(_SECRET_PATH).read_text().strip()
        return _SECRET_PATH

    new_secret = os.urandom(32).hex()
    Path(_SECRET_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(_SECRET_PATH).write_text(new_secret)
    os.chmod(_SECRET_PATH, stat.S_IRUSR | stat.S_IWUSR)
    _SECRET_CACHED = new_secret
    return _SECRET_PATH


_TOKEN_TTL = int(os.environ.get("CMMC_AUTH_TOKEN_TTL", "86400"))


def create_token(
    user_id: str,
    email: str,
    name: str,
    role: str,
    org_id: str = "",
    is_org_owner: bool = False,
    is_msp: bool = False,
    token_version: int = 0,
) -> str:
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "role": role,
        "org_id": org_id,
        "is_org_owner": int(is_org_owner),
        "is_msp": int(is_msp),
        "iat": now,
        "exp": now + _TOKEN_TTL,
        "tv": token_version,
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _secret(), algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
