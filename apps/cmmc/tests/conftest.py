"""Test configuration — insert core/ and evidence collectors into sys.path."""

import sys
from pathlib import Path

KHESTRA_ROOT = Path(__file__).resolve().parents[3]  # khestra/
EVIDENCE = KHESTRA_ROOT / "packages" / "evidence"
PACKAGES = KHESTRA_ROOT / "packages"
APP = Path(__file__).resolve().parents[1]
CORE = APP / "core"

for p in (EVIDENCE, PACKAGES, CORE):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)


import pytest  # noqa: E402

from kevidence.config import configure as _configure_evidence  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _evidence_configured(tmp_path_factory):
    """Point the evidence layer at a temp dir so tests never touch real data."""
    _configure_evidence(
        data_dir=tmp_path_factory.mktemp("evidence-data"),
        platform_root=APP,
    )
