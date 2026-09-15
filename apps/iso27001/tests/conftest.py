"""Test configuration — insert iso core/ and packages into sys.path."""

import sys
from pathlib import Path

KHESTRA_ROOT = Path(__file__).resolve().parents[3]  # khestra/
PACKAGES = KHESTRA_ROOT / "packages"
APP = Path(__file__).resolve().parents[1]
CORE = APP / "core"

for p in (PACKAGES, CORE):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
