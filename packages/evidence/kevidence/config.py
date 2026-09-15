"""Injectable configuration for the evidence layer (open side).

Apps must call configure() during startup before using any evidence functions.
This replaces the previous dependency on per-app config modules
(from config import DATA_DIR).
"""

from __future__ import annotations

from pathlib import Path

_data_dir: Path | None = None
_platform_root: Path | None = None


def configure(*, data_dir: Path, platform_root: Path) -> None:
    global _data_dir, _platform_root
    _data_dir = data_dir
    _platform_root = platform_root


def get_data_dir() -> Path:
    if _data_dir is None:
        raise RuntimeError(
            "evidence package not configured. Call configure() during app startup."
        )
    return _data_dir


def get_platform_root() -> Path:
    if _platform_root is None:
        raise RuntimeError(
            "evidence package not configured. Call configure() during app startup."
        )
    return _platform_root
