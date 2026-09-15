"""Compliance calendar milestones — cross-service assessment/expiry events.

Framework apps (e.g. cmmc) write their program milestones here (POA&M
closeout due, 3-year reassessment, annual affirmation); `collect_items`
picks them up so the shared reminder engine turns them into notifications
and dashboard badges.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH: str = ""
_lock = threading.Lock()


def init_store(data_dir: str) -> None:
    global DB_PATH
    DB_PATH = os.environ.get("COMPLIANCE_CALENDAR_DB_PATH") or str(Path(data_dir) / "compliance_calendar.db")
    _get_db().close()


def _get_db() -> sqlite3.Connection:
    if not DB_PATH:
        raise RuntimeError("Compliance calendar store not initialized. Call init_store() during app startup.")
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS milestones (
            framework_id   TEXT NOT NULL,
            client_id      TEXT NOT NULL DEFAULT '',
            milestone_type TEXT NOT NULL,
            due_date       TEXT NOT NULL,
            title          TEXT NOT NULL,
            details        TEXT NOT NULL DEFAULT '',
            link           TEXT NOT NULL DEFAULT '',
            status         TEXT NOT NULL DEFAULT 'open',
            updated_at     TEXT NOT NULL,
            PRIMARY KEY (framework_id, client_id, milestone_type)
        )
        """
    )
    db.commit()
    return db


def upsert_milestone(
    framework_id: str,
    milestone_type: str,
    due_date: str,
    title: str,
    details: str = "",
    link: str = "",
    client_id: str = "",
    status: str = "open",
) -> None:
    """Create or update a milestone row (one per framework/client/type)."""
    db = _get_db()
    try:
        with _lock:
            db.execute(
                """
                INSERT INTO milestones
                    (framework_id, client_id, milestone_type, due_date, title, details, link, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(framework_id, client_id, milestone_type)
                DO UPDATE SET
                    due_date = excluded.due_date,
                    title = excluded.title,
                    details = excluded.details,
                    link = excluded.link,
                    status = excluded.status,
                    updated_at = excluded.updated_at
                """,
                (framework_id, client_id, milestone_type, due_date, title, details, link, status,
                 datetime.now(timezone.utc).isoformat()),
            )
            db.commit()
    finally:
        db.close()


def clear_milestones(framework_id: str, client_id: str = "") -> None:
    """Remove all open milestones for a client (status changes recompute them)."""
    db = _get_db()
    try:
        with _lock:
            db.execute(
                "DELETE FROM milestones WHERE framework_id = ? AND client_id = ?",
                (framework_id, client_id),
            )
            db.commit()
    finally:
        db.close()


def list_milestones(due_before: str) -> List[Dict[str, Any]]:
    """Return open milestones due on or before a date (used by the reminder sweep)."""
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT * FROM milestones WHERE status = 'open' AND due_date <= ?",
            (due_before,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()
