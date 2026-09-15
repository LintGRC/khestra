"""Control tests — recurring evidence-producing activities.

Models a "control test" (e.g. backup restore test for SOC 2 A1.2/A1.3,
recovery test for CMMC 3.10.5) with a policy-set frequency, plus the log
of actual runs with result and optional evidence reference. The calendar
collector derives next-due from the last run; the sweep turns overdue
tests into compliance reminders.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

FREQUENCY_MONTHS: Dict[str, int] = {
    "monthly": 1,
    "quarterly": 3,
    "semi_annual": 6,
    "annual": 12,
}

DB_PATH: str | None = None


def _get_db() -> sqlite3.Connection:
    path = os.environ.get("CONTROL_TESTS_DB_PATH") or DB_PATH or "/tmp/khestra-control-tests.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


def _ensure_schema(db: sqlite3.Connection) -> None:
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS control_tests (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL DEFAULT '',
          control_id TEXT DEFAULT '',
          framework TEXT DEFAULT '',
          frequency TEXT DEFAULT 'quarterly',
          owner TEXT DEFAULT '',
          active INTEGER DEFAULT 1,
          target_rpo_minutes INTEGER,
          target_rto_minutes INTEGER,
          created_at TEXT DEFAULT '',
          updated_at TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS test_runs (
          id TEXT PRIMARY KEY,
          test_id TEXT NOT NULL,
          run_date TEXT DEFAULT '',
          result TEXT DEFAULT 'passed',
          notes TEXT DEFAULT '',
          evidence_hub_id TEXT DEFAULT '',
          evidence_title TEXT DEFAULT '',
          run_by TEXT DEFAULT '',
          actual_rpo_minutes INTEGER,
          actual_rto_minutes INTEGER,
          verified_by TEXT DEFAULT '',
          created_at TEXT DEFAULT ''
        );

        CREATE INDEX IF NOT EXISTS idx_control_tests_framework ON control_tests(framework);
        CREATE INDEX IF NOT EXISTS idx_test_runs_test_id ON test_runs(test_id);
        """
    )
    _migrate(db)
    db.commit()


def _migrate(db: sqlite3.Connection) -> None:
    cols = {r[1] for r in db.execute("PRAGMA table_info(control_tests)")}
    if "target_rpo_minutes" not in cols:
        db.execute("ALTER TABLE control_tests ADD COLUMN target_rpo_minutes INTEGER")
    if "target_rto_minutes" not in cols:
        db.execute("ALTER TABLE control_tests ADD COLUMN target_rto_minutes INTEGER")
    run_cols = {r[1] for r in db.execute("PRAGMA table_info(test_runs)")}
    if "actual_rpo_minutes" not in run_cols:
        db.execute("ALTER TABLE test_runs ADD COLUMN actual_rpo_minutes INTEGER")
    if "actual_rto_minutes" not in run_cols:
        db.execute("ALTER TABLE test_runs ADD COLUMN actual_rto_minutes INTEGER")
    if "verified_by" not in run_cols:
        db.execute("ALTER TABLE test_runs ADD COLUMN verified_by TEXT DEFAULT ''")


def _utcnow() -> str:
    return datetime.utcnow().isoformat()


def _row_to_test(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "control_id": row["control_id"],
        "framework": row["framework"],
        "frequency": row["frequency"],
        "owner": row["owner"],
        "active": bool(row["active"]),
        "target_rpo_minutes": row["target_rpo_minutes"],
        "target_rto_minutes": row["target_rto_minutes"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_run(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "test_id": row["test_id"],
        "run_date": row["run_date"],
        "result": row["result"],
        "notes": row["notes"],
        "evidence_hub_id": row["evidence_hub_id"],
        "evidence_title": row["evidence_title"],
        "run_by": row["run_by"],
        "actual_rpo_minutes": row["actual_rpo_minutes"],
        "actual_rto_minutes": row["actual_rto_minutes"],
        "verified_by": row["verified_by"],
        "created_at": row["created_at"],
    }


def init_store(data_dir: str) -> None:
    global DB_PATH
    DB_PATH = str(Path(data_dir) / "control_tests.db")


def list_tests() -> List[Dict[str, Any]]:
    db = _get_db()
    rows = db.execute(
        "SELECT * FROM control_tests ORDER BY created_at DESC"
    ).fetchall()
    return [_row_to_test(r) for r in rows]


def create_test(
    *,
    title: str,
    control_id: str = "",
    framework: str = "",
    frequency: str = "quarterly",
    owner: str = "",
    target_rpo_minutes: Optional[int] = None,
    target_rto_minutes: Optional[int] = None,
) -> Dict[str, Any]:
    db = _get_db()
    now = _utcnow()
    tid = str(uuid4())
    db.execute(
        "INSERT INTO control_tests (id, title, control_id, framework, frequency, owner, active, target_rpo_minutes, target_rto_minutes, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)",
        (tid, title, control_id, framework, frequency, owner, target_rpo_minutes, target_rto_minutes, now, now),
    )
    db.commit()
    row = db.execute("SELECT * FROM control_tests WHERE id = ?", (tid,)).fetchone()
    return _row_to_test(row)


def update_test(test_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _get_db()
    allowed = ("title", "control_id", "framework", "frequency", "owner", "active", "target_rpo_minutes", "target_rto_minutes")
    sets = [f"{k} = ?" for k in allowed if k in fields]
    if not sets:
        return get_test(test_id)
    params = [fields[k] for k in allowed if k in fields]
    sets.append("updated_at = ?")
    params.append(_utcnow())
    params.append(test_id)
    db.execute(
        f"UPDATE control_tests SET {', '.join(sets)} WHERE id = ?",
        params,
    )
    db.commit()
    return get_test(test_id)


def delete_test(test_id: str) -> bool:
    db = _get_db()
    db.execute("DELETE FROM test_runs WHERE test_id = ?", (test_id,))
    cur = db.execute("DELETE FROM control_tests WHERE id = ?", (test_id,))
    db.commit()
    return cur.rowcount > 0


def get_test(test_id: str) -> Optional[Dict[str, Any]]:
    db = _get_db()
    row = db.execute("SELECT * FROM control_tests WHERE id = ?", (test_id,)).fetchone()
    return _row_to_test(row) if row else None


def list_runs(test_id: str) -> List[Dict[str, Any]]:
    db = _get_db()
    rows = db.execute(
        "SELECT * FROM test_runs WHERE test_id = ? ORDER BY run_date DESC, created_at DESC",
        (test_id,),
    ).fetchall()
    return [_row_to_run(r) for r in rows]


def add_run(
    test_id: str,
    *,
    run_date: str = "",
    result: str = "passed",
    notes: str = "",
    evidence_hub_id: str = "",
    evidence_title: str = "",
    run_by: str = "",
    actual_rpo_minutes: Optional[int] = None,
    actual_rto_minutes: Optional[int] = None,
    verified_by: str = "",
) -> Optional[Dict[str, Any]]:
    db = _get_db()
    if get_test(test_id) is None:
        return None
    rid = str(uuid4())
    if not run_date:
        run_date = date.today().isoformat()
    now = _utcnow()
    db.execute(
        "INSERT INTO test_runs (id, test_id, run_date, result, notes, evidence_hub_id, evidence_title, run_by, actual_rpo_minutes, actual_rto_minutes, verified_by, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rid, test_id, run_date, result, notes, evidence_hub_id, evidence_title, run_by, actual_rpo_minutes, actual_rto_minutes, verified_by, now),
    )
    db.execute("UPDATE control_tests SET updated_at = ? WHERE id = ?", (now, test_id))
    db.commit()
    row = db.execute("SELECT * FROM test_runs WHERE id = ?", (rid,)).fetchone()
    return _row_to_run(row)


def next_due(test: Dict[str, Any], last_run_date: str = "") -> Optional[date]:
    """Next due = last run (or creation) + frequency period; None if unknown frequency."""
    months = FREQUENCY_MONTHS.get(test.get("frequency") or "")
    if not months:
        return None
    base = last_run_date or test.get("created_at") or ""
    base = base[:10]
    try:
        d = date.fromisoformat(base)
    except ValueError:
        return None
    return d + timedelta(days=months * 30)
