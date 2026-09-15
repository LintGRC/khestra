"""Management review store — ISO 27001 clause 9.3.

Records top-management review meetings: attendees, inputs considered
(audit results, findings, risk status, previous actions, context changes,
interested-party needs, performance feedback, resource adequacy), outputs
and decisions, and action items.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

DB_PATH: str | None = None

REVIEW_STATUSES = ["scheduled", "in_progress", "completed"]

DEFAULT_INPUTS = [
    ("previous_actions", "Status of actions from previous management reviews"),
    ("context_changes", "Changes in external and internal issues relevant to the ISMS"),
    ("interested_party_needs", "Changes in needs and expectations of interested parties"),
    ("performance_feedback", "Feedback on information security performance, including trends in nonconformities, incidents and findings"),
    ("audit_results", "Results of internal audits"),
    ("risk_status", "Status of information security risk assessment and treatment"),
    ("resource_adequacy", "Adequacy of resources"),
    ("effectiveness", "Effectiveness of controls and risk treatment"),
]

OUTPUT_CATEGORIES = ["improvement", "resource", "policy", "risk_acceptance", "other"]


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("MANAGEMENT_REVIEW_DB_PATH") or DB_PATH or "/tmp/khestra-management-review.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS management_reviews (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '',
  date TEXT DEFAULT '',
  status TEXT DEFAULT 'scheduled',
  attendees TEXT DEFAULT '[]',
  inputs TEXT DEFAULT '[]',
  outputs TEXT DEFAULT '[]',
  action_items TEXT DEFAULT '[]',
  minutes TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("attendees", "inputs", "outputs", "action_items"):
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
    DB_PATH = os.environ.get("MANAGEMENT_REVIEW_DB_PATH") or str(Path(data_dir) / "management_review.db")
    db = _get_db()
    db.close()


def list_reviews(status: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        sql = "SELECT * FROM management_reviews"
        params: list = []
        if status:
            sql += " WHERE status = ?"
            params.append(status)
        sql += " ORDER BY date DESC, updated_at DESC"
        rows = db.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def get_review(rid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM management_reviews WHERE id = ?", (rid,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def create_review(
    title: str = "",
    date: str = "",
    status: str = "scheduled",
    attendees: list[dict] | None = None,
    inputs: list[dict] | None = None,
    outputs: list[dict] | None = None,
    action_items: list[dict] | None = None,
    minutes: str = "",
) -> dict:
    rid = uuid4().hex[:12]
    now = _utcnow()
    if status not in REVIEW_STATUSES:
        status = "scheduled"
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO management_reviews (id, title, date, status, attendees, inputs, outputs, "
            "action_items, minutes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (rid, title, date, status, json.dumps(attendees or []), json.dumps(inputs or []),
             json.dumps(outputs or []), json.dumps(action_items or []), minutes, now, now),
        )
        db.commit()
    finally:
        db.close()
    return get_review(rid) or {}


def update_review(rid: str, **kwargs) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM management_reviews WHERE id = ?", (rid,)).fetchone()
        if not row:
            return None
        sets = []
        vals = []
        for k, v in kwargs.items():
            if k == "id" or v is None:
                continue
            if isinstance(v, list):
                sets.append(f"{k} = ?")
                vals.append(json.dumps(v))
            else:
                sets.append(f"{k} = ?")
                vals.append(v)
        if not sets:
            return _row_to_dict(row)
        sets.append("updated_at = ?")
        vals.append(_utcnow())
        vals.append(rid)
        db.execute(f"UPDATE management_reviews SET {', '.join(sets)} WHERE id = ?", vals)
        db.commit()
    finally:
        db.close()
    return get_review(rid)


def delete_review(rid: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT id FROM management_reviews WHERE id = ?", (rid,)).fetchone()
        if not row:
            return False
        db.execute("DELETE FROM management_reviews WHERE id = ?", (rid,))
        db.commit()
        return True
    finally:
        db.close()


def stats() -> dict:
    db = _get_db()
    try:
        total = db.execute("SELECT COUNT(*) AS c FROM management_reviews").fetchone()["c"]
        by_status = {s: 0 for s in REVIEW_STATUSES}
        for r in db.execute("SELECT status, COUNT(*) AS c FROM management_reviews GROUP BY status"):
            by_status[r["status"]] = r["c"]
        open_actions = 0
        latest = db.execute("SELECT * FROM management_reviews ORDER BY date DESC LIMIT 1").fetchone()
        if latest:
            latest_d = _row_to_dict(latest)
            open_actions = sum(1 for a in latest_d.get("action_items") or [] if a.get("status") == "open")
        return {"total": total, "by_status": by_status, "open_actions_latest": open_actions}
    finally:
        db.close()
