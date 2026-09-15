"""Production deployment flags for the ISO 27001 API."""

from __future__ import annotations

import os

_DEFAULT_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5177",
    "http://127.0.0.1:5177",
    "http://localhost:8085",
    "http://127.0.0.1:8085",
]


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes")


def demo_api_enabled() -> bool:
    return _env_flag("DEMO_MODE") or _env_flag("ISO27001_DEMO_MODE")


def allowed_cors_origins() -> list[str]:
    raw = os.environ.get("ISO27001_ALLOWED_ORIGINS", "").strip()
    if not raw:
        shared = os.environ.get("CMMC_ALLOWED_ORIGINS", "").strip()
        if shared:
            raw = shared
    if not raw:
        return list(_DEFAULT_DEV_ORIGINS)
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins or list(_DEFAULT_DEV_ORIGINS)
