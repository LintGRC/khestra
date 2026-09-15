"""Paths for SOC 2 app."""

import os
from pathlib import Path

PLATFORM_ROOT = Path(__file__).resolve().parent.parent
KHESTRA_ROOT = PLATFORM_ROOT.parent.parent

# SOC2's own data dir, distinct from CMMC's (KHESTRA_ROOT / "data"). Both
# apps used to fall back to the exact same KHESTRA_ROOT/data path, so any
# SOC2 store without an explicit *_DB_PATH env override (RACI, exceptions,
# testing, findings, audit center, training, notifications, remediation,
# orgs, audit.db, evidence hub, and client workspaces/session_state.json)
# silently shared a single file with CMMC's equivalent store — whichever
# app was used more recently locally clobbered the other's data (e.g. SOC2's
# TSC-criteria control answers overwritten by CMMC's practice-ID answers,
# or vice versa). This matches production, where soc2-api's own volume is
# mounted at /apps/soc2/soc2_data (this resolves to that same path in a
# container), separate from cmmc-api's cmmc_data volume.
DATA_DIR = Path(os.environ.get("SOC2_DATA_DIR") or (PLATFORM_ROOT / "soc2_data"))
SESSION_FILENAME = "session_state.json"


def resolve_session_state_path() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / SESSION_FILENAME
