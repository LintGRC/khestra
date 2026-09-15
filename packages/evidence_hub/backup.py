"""Automated backup for evidence DB and files.

Keeps last 7 daily + 4 weekly backups. Designed to be called
from the scheduler daemon once every cycle (idempotent — uses
a timestamp file to run at most once per day).
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path


_MAX_DAILY = 7
_MAX_WEEKLY = 4


def _backup_dir(base: Path) -> Path:
    p = base / "_backups"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _timestamp_file(base: Path, name: str) -> Path:
    return _backup_dir(base) / f"last_{name}_backup_at.txt"


def _should_backup(base: Path, name: str) -> bool:
    p = _timestamp_file(base, name)
    if not p.exists():
        return True
    try:
        last = float(p.read_text().strip())
        return (time.time() - last) > 86400
    except (ValueError, OSError):
        return True


def _mark_backup(base: Path, name: str) -> None:
    _timestamp_file(base, name).write_text(str(time.time()))


def _prune_old(base: Path, prefix: str, max_keep: int) -> None:
    backups = sorted(_backup_dir(base).glob(f"{prefix}_*.bak"))
    for old in backups[:-max_keep]:
        old.unlink(missing_ok=True)


def backup_database(db_path: str, data_dir: str) -> dict:
    """Backup SQLite database using sqlite3.backup().

    Returns backup info dict, or empty dict if skipped (already backed up today).
    """
    base = Path(data_dir)
    if not _should_backup(base, "db"):
        return {"skipped": True}

    if not Path(db_path).exists():
        return {"error": "Database not found"}

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = _backup_dir(base) / f"evidence_db_{stamp}.bak"

    try:
        src = sqlite3.connect(db_path)
        dst = sqlite3.connect(str(backup_file))
        src.backup(dst)
        dst.close()
        src.close()
        _mark_backup(base, "db")
        _prune_old(base, "evidence_db", _MAX_DAILY)
        # weekly backup (keep first backup each week)
        if datetime.now(timezone.utc).weekday() == 0:
            weekly = _backup_dir(base) / f"evidence_db_weekly_{stamp}.bak"
            shutil.copy2(backup_file, weekly)
            _prune_old(base, "evidence_db_weekly", _MAX_WEEKLY)
        return {"backup_file": str(backup_file), "size_bytes": backup_file.stat().st_size}
    except Exception as e:
        print(f"Backup failed: {e}", file=sys.stderr)
        return {"error": str(e)}


def backup_files(files_dir: str, data_dir: str) -> dict:
    """Tar-gzip the evidence files directory.

    Returns backup info dict, or empty dict if skipped (already backed up today).
    """
    base = Path(data_dir)
    if not _should_backup(base, "files"):
        return {"skipped": True}

    files_path = Path(files_dir)
    if not files_path.is_dir():
        return {"error": "Files directory not found"}

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = _backup_dir(base) / f"evidence_files_{stamp}.tar.gz"

    try:
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(files_path, arcname="evidence_files")
        _mark_backup(base, "files")
        _prune_old(base, "evidence_files", _MAX_DAILY)
        return {"backup_file": str(backup_file), "size_bytes": backup_file.stat().st_size}
    except Exception as e:
        print(f"Files backup failed: {e}", file=sys.stderr)
        return {"error": str(e)}
