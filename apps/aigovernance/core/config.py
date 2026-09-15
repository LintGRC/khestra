"""Paths for AI Governance app."""

from pathlib import Path

PLATFORM_ROOT = Path(__file__).resolve().parent.parent
KHESTRA_ROOT = PLATFORM_ROOT.parent.parent
DATA_DIR = KHESTRA_ROOT / "data"


def resolve_session_state_path() -> Path:
    return DATA_DIR / "session_state.json"
