"""Production deployment flags — demo endpoints, CORS, etc."""

from __future__ import annotations

import os

from sandbox_config import sandbox_mode

_DEFAULT_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes")


def demo_api_enabled() -> bool:
    """Sample workspace load/clear — off in production unless explicitly enabled."""
    if _env_flag("DEMO_MODE"):
        return True
    return sandbox_mode()


def allowed_cors_origins() -> list[str]:
    """Comma-separated CMMC_ALLOWED_ORIGINS; dev localhost origins when unset."""
    raw = os.environ.get("CMMC_ALLOWED_ORIGINS", "").strip()
    if not raw:
        return list(_DEFAULT_DEV_ORIGINS)
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins or list(_DEFAULT_DEV_ORIGINS)
