"""Paths for standalone platform package (all data under platform/)."""

import shutil
from pathlib import Path

PLATFORM_ROOT = Path(__file__).resolve().parent.parent
KHESTRA_ROOT = PLATFORM_ROOT.parent.parent
ROOT_DIR = KHESTRA_ROOT
DATA_DIR = KHESTRA_ROOT / "data"
LEGACY_DATA_DIR = PLATFORM_ROOT / "heavygrc_data"
SESSION_FILENAME = "session_state.json"
SSP_TEMPLATE_CANDIDATES = [
    PLATFORM_ROOT / "assets" / "cui-ssp-template-final.docx",
    PLATFORM_ROOT / "cui-ssp-template-final.docx",
    PLATFORM_ROOT / "templates" / "cui-ssp-template.docx",
]


def resolve_ssp_template() -> str | None:
    for path in SSP_TEMPLATE_CANDIDATES:
        if path.is_file():
            return str(path)
    return None


def resolve_org_assets_dir() -> Path:
    path = DATA_DIR / "org_assets"
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_session_state_path() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    target = DATA_DIR / SESSION_FILENAME
    if target.exists():
        return target
    legacy = LEGACY_DATA_DIR / SESSION_FILENAME
    if legacy.is_file():
        shutil.copy2(legacy, target)
    return target
