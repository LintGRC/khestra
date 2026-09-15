"""Organizational context store — ISO 27001 clauses 4.1/4.2/4.3 (+ Amd 1:2024 climate).

Records internal/external issues, interested parties and their requirements,
ISMS scope/boundaries, and the climate-change relevance determination.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

DB_PATH: str | None = None

_CLIMATE_ISSUE_HINT = "climate change"

# Amd 1:2024 — the org must DETERMINE climate relevance (4.1 external context)
# and whether interested parties have climate-related requirements (4.2).
# `not_assessed` is a distinct state from "determined not relevant".
CLIMATE_STATUSES = ("not_assessed", "relevant", "not_relevant")


def _status_to_bool(status: str | None) -> bool:
    return status == "relevant"


def _bool_relevant_bump(current: str, climate_relevant: bool) -> str:
    """Map a legacy bool-only update to an explicit determination."""
    if climate_relevant:
        return "relevant"
    return "not_relevant"


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("ORG_CONTEXT_DB_PATH") or DB_PATH or "/tmp/khestra-org-context.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS org_context (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL DEFAULT '',
  internal_issues TEXT DEFAULT '[]',
  external_issues TEXT DEFAULT '[]',
  interested_parties TEXT DEFAULT '[]',
  climate_relevant INTEGER NOT NULL DEFAULT 0,
  climate_note TEXT DEFAULT '',
  climate_status TEXT NOT NULL DEFAULT 'not_assessed',
  scope_statement TEXT DEFAULT '',
  boundaries TEXT DEFAULT '',
  interfaces_dependencies TEXT DEFAULT '[]',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    cols = {r[1] for r in db.execute("PRAGMA table_info(org_context)").fetchall()}
    if "climate_status" not in cols:
        db.execute(
            "ALTER TABLE org_context ADD COLUMN climate_status TEXT NOT NULL DEFAULT 'not_assessed'"
        )
        db.execute(
            "UPDATE org_context SET climate_status = 'not_assessed' WHERE climate_status = ''"
        )


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("internal_issues", "external_issues", "interested_parties", "interfaces_dependencies"):
        val = d.get(col)
        if isinstance(val, str):
            try:
                d[col] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                d[col] = []
        elif val is None:
            d[col] = []
    status = d.get("climate_status") or "not_assessed"
    if status not in CLIMATE_STATUSES:
        status = "not_assessed"
    d["climate_status"] = status
    d["climate_relevant"] = _status_to_bool(status)
    return d


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = os.environ.get("ORG_CONTEXT_DB_PATH") or str(Path(data_dir) / "org_context.db")
    db = _get_db()
    db.close()


def list_records() -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute("SELECT * FROM org_context ORDER BY updated_at DESC").fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def get_record(rid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM org_context WHERE id = ?", (rid,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def create_record(
    label: str = "",
    internal_issues: list[str] | None = None,
    external_issues: list[str] | None = None,
    interested_parties: list[dict] | None = None,
    climate_relevant: bool = False,
    climate_note: str = "",
    climate_status: str = "",
    scope_statement: str = "",
    boundaries: str = "",
    interfaces_dependencies: list[str] | None = None,
) -> dict:
    rid = uuid4().hex[:12]
    now = _utcnow()
    if climate_status not in CLIMATE_STATUSES:
        if climate_relevant or any(_CLIMATE_ISSUE_HINT in (i or "").lower() for i in (internal_issues or [])):
            climate_status = "relevant"
        elif climate_status == "":
            climate_status = "not_assessed"
    climate_relevant = _status_to_bool(climate_status)
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO org_context (id, label, internal_issues, external_issues, interested_parties, "
            "climate_relevant, climate_note, climate_status, scope_statement, boundaries, interfaces_dependencies, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (rid, label, json.dumps(internal_issues or []), json.dumps(external_issues or []),
             json.dumps(interested_parties or []), 1 if climate_relevant else 0, climate_note,
             climate_status, scope_statement, boundaries, json.dumps(interfaces_dependencies or []), now, now),
        )
        db.commit()
    finally:
        db.close()
    return get_record(rid) or {}


def update_record(rid: str, **kwargs) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM org_context WHERE id = ?", (rid,)).fetchone()
        if not row:
            return None
        sets = []
        vals = []
        status_explicit = False
        legacy_bool: bool | None = None
        for k, v in kwargs.items():
            if k == "id" or v is None:
                continue
            if k == "climate_relevant":
                legacy_bool = bool(v)
                continue  # bool is derived from climate_status; applied after
            if k == "climate_status":
                if v not in CLIMATE_STATUSES:
                    continue
                status_explicit = True
                sets.append("climate_status = ?")
                vals.append(v)
            elif isinstance(v, list):
                sets.append(f"{k} = ?")
                vals.append(json.dumps(v))
            else:
                sets.append(f"{k} = ?")
                vals.append(v)
        if (status_explicit or legacy_bool is not None):
            current_status = str(row["climate_status"] or "not_assessed")
            next_status = kwargs.get("climate_status")
            if next_status not in CLIMATE_STATUSES:
                next_status = _bool_relevant_bump(current_status, bool(legacy_bool))
            sets.append("climate_status = ?")
            vals.append(next_status)
            sets.append("climate_relevant = ?")
            vals.append(1 if _status_to_bool(next_status) else 0)
        if not sets:
            return _row_to_dict(row)
        now = _utcnow()
        sets.append("updated_at = ?")
        vals.append(now)
        vals.append(rid)
        db.execute(f"UPDATE org_context SET {', '.join(sets)} WHERE id = ?", vals)
        db.commit()
    finally:
        db.close()
    return get_record(rid)


def delete_record(rid: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT id FROM org_context WHERE id = ?", (rid,)).fetchone()
        if not row:
            return False
        db.execute("DELETE FROM org_context WHERE id = ?", (rid,))
        db.commit()
        return True
    finally:
        db.close()


def stats() -> dict:
    db = _get_db()
    try:
        total = db.execute("SELECT COUNT(*) AS c FROM org_context").fetchone()["c"]
        latest = db.execute("SELECT * FROM org_context ORDER BY updated_at DESC LIMIT 1").fetchone()
        climate = db.execute("SELECT COUNT(*) AS c FROM org_context WHERE climate_relevant = 1").fetchone()["c"]
        parties = 0
        if latest:
            parties = len(_row_to_dict(latest).get("interested_parties") or [])
        return {
            "total": total,
            "climate_relevant": climate,
            "latest": _row_to_dict(latest) if latest else None,
            "interested_parties_latest": parties,
        }
    finally:
        db.close()
