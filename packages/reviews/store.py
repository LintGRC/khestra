"""Reviews polymorphic store — access reviews, vendor reviews, policy reviews, BCP/DR tests, risk reviews, firewall reviews."""

import json
import sqlite3
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional

DB_PATH: str | None = None

REVIEW_TYPES = [
    "access_review",
    "policy_review",
    "vendor_review",
    "bcp_dr_test",
    "risk_review",
    "firewall_review",
]

REVIEW_FREQUENCIES = [
    "monthly",
    "quarterly",
    "annual",
    "one_time",
]

REVIEW_STATUSES = [
    "pending",
    "in_progress",
    "completed",
    "overdue",
]


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("REVIEWS_DB_PATH") or DB_PATH or "/tmp/khestra-reviews.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS reviews (
  id TEXT PRIMARY KEY,
  type TEXT DEFAULT '',
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  frequency TEXT DEFAULT '',
  owner_id TEXT DEFAULT '',
  owner_name TEXT DEFAULT '',
  scheduled_date TEXT DEFAULT '',
  completed_date TEXT DEFAULT '',
  status TEXT DEFAULT 'pending',
  evidence_ids TEXT DEFAULT '[]',
  findings TEXT DEFAULT '[]',
  control_ids TEXT DEFAULT '[]',
  framework_id TEXT DEFAULT '',
  workspace_id TEXT DEFAULT '',
  org_id TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("evidence_ids", "findings", "control_ids"):
        val = d.get(col)
        if isinstance(val, str):
            try:
                d[col] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                d[col] = []
        elif val is None:
            d[col] = []
    return d


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = os.environ.get("REVIEWS_DB_PATH") or str(Path(data_dir) / "reviews.db")
    db = _get_db()
    db.close()


def list_reviews(
    review_type: Optional[str] = None,
    framework_id: Optional[str] = None,
    status: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> list[dict]:
    db = _get_db()
    try:
        sql = "SELECT * FROM reviews WHERE 1=1"
        params: list = []
        if review_type:
            sql += " AND type = ?"
            params.append(review_type)
        if framework_id:
            sql += " AND framework_id = ?"
            params.append(framework_id)
        if status:
            sql += " AND status = ?"
            params.append(status)
        if workspace_id:
            sql += " AND workspace_id = ?"
            params.append(workspace_id)
        sql += " ORDER BY scheduled_date DESC"
        rows = db.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def get_review(rid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM reviews WHERE id = ?", (rid,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def create_review(
    title: str,
    review_type: str = "",
    description: str = "",
    frequency: str = "",
    owner_id: str = "",
    owner_name: str = "",
    scheduled_date: str = "",
    framework_id: str = "",
    workspace_id: str = "",
    org_id: str = "",
    control_ids: list[str] | None = None,
) -> dict:
    rid = uuid4().hex[:12]
    now = _utcnow()
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO reviews (id, type, title, description, frequency, owner_id, owner_name, "
            "scheduled_date, status, evidence_ids, findings, control_ids, framework_id, "
            "workspace_id, org_id, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', '[]', '[]', ?, ?, ?, ?, ?)",
            (rid, review_type, title, description, frequency, owner_id, owner_name,
             scheduled_date, json.dumps(control_ids or []), framework_id, workspace_id, org_id, now),
        )
        db.commit()
    finally:
        db.close()
    return get_review(rid) or {}


def update_review(rid: str, **kwargs) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM reviews WHERE id = ?", (rid,)).fetchone()
        if not row:
            return None
        current = _row_to_dict(row)
        for k, v in kwargs.items():
            if v is not None and k != "id":
                if isinstance(v, list):
                    current[k] = v
                else:
                    current[k] = v
        current["updated_at"] = _utcnow()
        sets = []
        vals = []
        for k in kwargs:
            if k == "id" or kwargs[k] is None:
                continue
            val = kwargs[k]
            if isinstance(val, list):
                sets.append(f"{k} = ?")
                vals.append(json.dumps(val))
            else:
                sets.append(f"{k} = ?")
                vals.append(val)
        if not sets:
            return current
        sets.append("updated_at = ?")
        vals.append(current["updated_at"])
        vals.append(rid)
        db.execute(f"UPDATE reviews SET {', '.join(sets)} WHERE id = ?", vals)
        db.commit()
    finally:
        db.close()
    return get_review(rid)


def delete_review(rid: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT id FROM reviews WHERE id = ?", (rid,)).fetchone()
        if not row:
            return False
        db.execute("DELETE FROM reviews WHERE id = ?", (rid,))
        db.commit()
        return True
    finally:
        db.close()
