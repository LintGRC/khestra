"""Optional AI (BYOK) — API key resolution.

Key precedence (first non-empty wins):
  1. Stored in-app key  (Integrations page -> credentials_store, encrypted at rest)
  2. CMMC_OPENAI_API_KEY (per-app environment override)
  3. OPENAI_API_KEY       (shared environment override)
  4. HOSTED_AI_KEY        (platform-provided default on hosted plans — injected at
                          deployment time, never committed to the repo)

No real key ever lives in the repository or in any API response.
"""

from __future__ import annotations

import os

# Reserved connector id for the stored BYOK key (credentials_store).
AI_KEY_CONNECTOR_ID = "ai"


def stored_api_key() -> str:
    """Load the in-app stored key (encrypted at rest under the data dir)."""
    try:
        from collectors.credentials_store import load_credentials

        creds = load_credentials(AI_KEY_CONNECTOR_ID) or {}
        return str(creds.get("api_key") or "").strip()
    except Exception:
        return ""


def api_key() -> str:
    return (
        stored_api_key()
        or os.environ.get("CMMC_OPENAI_API_KEY", "").strip()
        or os.environ.get("OPENAI_API_KEY", "").strip()
        or os.environ.get("HOSTED_AI_KEY", "").strip()
    )


def ai_key_source() -> str:
    """Where the active key comes from: stored | env | hosted | none."""
    if stored_api_key():
        return "stored"
    if os.environ.get("CMMC_OPENAI_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip():
        return "env"
    if os.environ.get("HOSTED_AI_KEY", "").strip():
        return "hosted"
    return "none"


def model() -> str:
    return (os.environ.get("CMMC_AI_MODEL", "").strip() or "gpt-4o-mini")


def ssp_extra_instructions() -> str:
    """Optional assessor/org-specific rules appended to the SSP polish prompt."""
    return os.environ.get("CMMC_AI_SSP_EXTRA_INSTRUCTIONS", "").strip()


def ai_disabled() -> bool:
    return os.environ.get("CMMC_AI_DISABLE", "").strip().lower() in ("1", "true", "yes")


def is_available() -> bool:
    return bool(api_key()) and not ai_disabled()


def public_status() -> dict:
    return {
        "ai_ssp_available": is_available(),
        "ai_model": model() if is_available() else None,
        "has_ai_key": bool(api_key()),
        "ai_key_source": ai_key_source(),
    }
