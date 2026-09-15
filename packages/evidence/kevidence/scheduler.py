"""Scheduler token configuration (open side).

The token helpers are needed by the auth layer, which must not know whether
the closed collectors package is installed (`docs/OPEN_CORE_CONTRACT.md` §A5).
The `dev_scheduler_*` helpers stay in the closed package.
"""

from __future__ import annotations

import os
import secrets


def scheduler_token() -> str:
    return (
        os.environ.get("CMMC_COLLECTOR_SCHEDULER_TOKEN", "").strip()
        or os.environ.get("COLLECTOR_SCHEDULER_TOKEN", "").strip()
    )


def scheduler_token_matches(token: str | None) -> bool:
    expected = scheduler_token()
    if not expected or not token:
        return False
    return secrets.compare_digest(token, expected)
