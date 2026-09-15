"""Central probe for the closed collectors package (open-core split §4.3).

Single detection point: app boot code must call ``collectors_available()``
instead of scattering `try/except ImportError` booleans through `main.py`.
"""

from __future__ import annotations

import importlib.util
from functools import lru_cache


@lru_cache(maxsize=1)
def collectors_available() -> bool:
    """True when the closed `khestra-collectors` package is importable."""
    try:
        return importlib.util.find_spec("collectors") is not None
    except (ImportError, ValueError):
        return False
