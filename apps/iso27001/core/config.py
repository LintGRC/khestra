"""Paths for the ISO 27001 app."""

from pathlib import Path

PLATFORM_ROOT = Path(__file__).resolve().parent.parent
KHESTRA_ROOT = PLATFORM_ROOT.parent.parent

# ISO 27001's own data dir, distinct from CMMC's (KHESTRA_ROOT / "data") and
# SOC2's (apps/soc2/soc2_data). Follows the soc2 split pattern so the ISO
# 27001 store never clobbers another framework's shared modules.
DATA_DIR = PLATFORM_ROOT / "data"
SESSION_FILENAME = "session_state.json"

FRAMEWORK_ID = "ISO 27001"

# Single source for the display name used by /api/settings and /api/dashboard.
ORG_NAME = "Khestra ISO 27001"
