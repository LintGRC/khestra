"""Notification queue — stores in-app notifications from all trigger sources."""

from __future__ import annotations

import json
import sqlite3
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from . import email as _email
from . import chat as _chat


DB_PATH: str | None = None


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = DB_PATH or "/tmp/khestra-notifications.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


def _ensure_schema(db: sqlite3.Connection):
    db.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            recipient TEXT NOT NULL DEFAULT '',
            type TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL DEFAULT '',
            body TEXT DEFAULT '',
            link TEXT DEFAULT '',
            metadata TEXT DEFAULT '{}',
            read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT ''
        )
    """)
    try:
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_notifications_type_title ON notifications(type, title) WHERE read = 0")
    except sqlite3.OperationalError:
        pass


def init_store(data_dir: str):
    global DB_PATH
    path = os.environ.get("NOTIFICATIONS_DB_PATH") or str(Path(data_dir) / "notifications.db")
    DB_PATH = path
    _get_db().close()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_notification(recipient: str, type: str, title: str, body: str = "", link: str = "", metadata: Optional[Dict[str, Any]] = None) -> dict:
    db = _get_db()
    try:
        nid = uuid4().hex[:12]
        db.execute(
            "INSERT OR IGNORE INTO notifications (id, recipient, type, title, body, link, metadata, read, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)",
            (nid, recipient, type, title, body, link, json.dumps(metadata or {}), _now()),
        )
        db.commit()
        notification = {"id": nid, "recipient": recipient, "type": type, "title": title, "body": body, "link": link, "read": False}
        try:
            _email.send_email_notification(notification)
        except Exception:
            pass
        try:
            _chat.send_chat_notification(notification)
        except Exception:
            pass
        return notification
    finally:
        db.close()


def list_notifications(recipient: str = "", type: Optional[str] = None, unread_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
    db = _get_db()
    try:
        conditions = []
        params: list = []
        if recipient:
            conditions.append("recipient = ?")
            params.append(recipient)
        if type:
            conditions.append("type = ?")
            params.append(type)
        if unread_only:
            conditions.append("read = 0")
        where = " AND ".join(conditions) if conditions else "1=1"
        rows = db.execute(f"SELECT * FROM notifications WHERE {where} ORDER BY created_at DESC LIMIT ?", (*params, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def mark_read(notification_id: str) -> bool:
    db = _get_db()
    try:
        db.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
        db.commit()
        return db.total_changes > 0
    finally:
        db.close()


def mark_all_read(recipient: str = "") -> int:
    db = _get_db()
    try:
        if recipient:
            db.execute("UPDATE notifications SET read = 1 WHERE recipient = ? AND read = 0", (recipient,))
        else:
            db.execute("UPDATE notifications SET read = 1 WHERE read = 0")
        db.commit()
        return db.total_changes
    finally:
        db.close()


def unread_count(recipient: str = "") -> int:
    db = _get_db()
    try:
        if recipient:
            row = db.execute("SELECT COUNT(*) AS cnt FROM notifications WHERE recipient = ? AND read = 0", (recipient,)).fetchone()
        else:
            row = db.execute("SELECT COUNT(*) AS cnt FROM notifications WHERE read = 0").fetchone()
        return row["cnt"] if row else 0
    finally:
        db.close()


def check_all_triggers() -> int:
    """Run all notification triggers and return count of new notifications created."""
    total = 0
    try:
        total += _check_policy_review_triggers()
    except Exception:
        pass
    try:
        total += _check_vendor_soc_triggers()
    except Exception:
        pass
    try:
        total += _check_test_triggers()
    except Exception:
        pass
    return total


def _check_policy_review_triggers() -> int:
    created = 0
    db = None
    try:
        from policies.review_reminders import get_policies_due_review
        due = get_policies_due_review()
        db = _get_db()
        for p in due:
            title = f"Policy review: {p['title']}"
            body = f"{p.get('days_since_update', 0)} days since last review."
            if p.get("urgency") == "overdue":
                title = f"Policy review overdue: {p['title']}"
            existing = db.execute("SELECT 1 FROM notifications WHERE type='policy_review' AND title=? AND read=0", (title,)).fetchone()
            if not existing:
                create_notification("admin", "policy_review", title, body, link="/policies")
                created += 1
    except Exception:
        pass
    finally:
        if db:
            db.close()
    return created


def _check_vendor_soc_triggers() -> int:
    created = 0
    db = None
    try:
        from vendors.review_reminders import get_vendors_due_review
        due = get_vendors_due_review()
        db = _get_db()
        for v in due:
            title = f"Vendor SOC report: {v['name']}"
            body = f"Review due: {v.get('next_review_due', 'N/A')}"
            if v.get("urgency") == "overdue":
                title = f"Vendor SOC report overdue: {v['name']}"
            existing = db.execute("SELECT 1 FROM notifications WHERE type='vendor_soc' AND title=? AND read=0", (title,)).fetchone()
            if not existing:
                create_notification("admin", "vendor_soc", title, body, link="/vendors")
                created += 1
    except Exception:
        pass
    finally:
        if db:
            db.close()
    return created


def _check_test_triggers() -> int:
    created = 0
    try:
        from testing.store import overdue_test_count
        count = overdue_test_count(framework="SOC2")
        if count > 0:
            title = f"{count} test(s) overdue"
            db = _get_db()
            try:
                existing = db.execute("SELECT 1 FROM notifications WHERE type='test_overdue' AND title=? AND read=0", (title,)).fetchone()
                if not existing:
                    create_notification("admin", "test_overdue", title, f"{count} control test(s) are past their due date.", link="/testing")
                    created += 1
            finally:
                db.close()
    except Exception:
        pass
    return created
