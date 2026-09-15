import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GLOBAL_DIR = HERE.parent
PACKAGES = GLOBAL_DIR / "packages"
if not PACKAGES.is_dir():
    PACKAGES = GLOBAL_DIR.parent.parent / "packages"

for p in [str(PACKAGES)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Prefer explicit env (Docker sets CORE_DATA_DIR=/data); else apps/core/data
_env_data = os.environ.get("CORE_DATA_DIR", "").strip()
DATA_DIR = Path(_env_data) if _env_data else (GLOBAL_DIR / "data")
