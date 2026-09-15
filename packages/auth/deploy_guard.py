"""Production auth-posture guard.

Refuses to start when the deployment signals production (`KHESTRA_ENV=production`)
with local-mode auth and no declared trusted network boundary. Local auth is
acceptable ONLY behind a VPN / IP allowlist / private subnet; public exposure
requires Entra ID (see each app's PRODUCTION.md). The operator attests the
boundary by setting `KHESTRA_TRUSTED_NETWORK=1` — an explicit two-step, not an
accidental default.
"""

from __future__ import annotations

import os


def production_enabled() -> bool:
    return os.environ.get("KHESTRA_ENV", "").strip().lower() == "production"


def assert_safe_auth_posture() -> None:
    """Raise at startup when production + local auth + no declared boundary."""
    if not production_enabled():
        return
    mode = os.environ.get("CMMC_AUTH_MODE", "").strip().lower()
    trusted = os.environ.get("KHESTRA_TRUSTED_NETWORK", "").strip().lower() in ("1", "true", "yes")
    if mode in ("", "local", "none") and not trusted:
        raise RuntimeError(
            "Refusing to start: KHESTRA_ENV=production with local auth requires "
            "KHESTRA_TRUSTED_NETWORK=1 (VPN / IP allowlist / private subnet). "
            "For public exposure, configure Entra ID (CMMC_ENTRA_TENANT_ID / "
            "CMMC_ENTRA_CLIENT_ID) and set CMMC_AUTH_MODE=entra."
        )
