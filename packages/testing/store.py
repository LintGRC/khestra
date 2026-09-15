import json
import os
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Optional

from .models import ControlTest, TestResult, utcnow


DB_PATH: str | None = None


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tests (
  id TEXT PRIMARY KEY,
  control_id TEXT NOT NULL DEFAULT '',
  framework TEXT NOT NULL DEFAULT '',
  test_procedure TEXT NOT NULL DEFAULT '',
  frequency TEXT DEFAULT '',
  sample_size INTEGER DEFAULT 0,
  last_tested TEXT DEFAULT '',
  next_test_due TEXT DEFAULT '',
  status TEXT DEFAULT 'not_tested',
  tested_by TEXT DEFAULT '',
  evidence_id TEXT DEFAULT '',
  notes TEXT DEFAULT '',
  created_by TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS test_results (
  id TEXT PRIMARY KEY,
  test_id TEXT NOT NULL,
  result TEXT NOT NULL DEFAULT '',
  tested_by TEXT DEFAULT '',
  tested_at TEXT DEFAULT '',
  evidence_id TEXT DEFAULT '',
  notes TEXT DEFAULT '',
  created_at TEXT DEFAULT ''
);
"""

_TEST_COLS = [
    "id", "control_id", "framework", "test_procedure", "frequency",
    "sample_size", "sampling_methodology", "population_size", "confidence_level", "margin_of_error",
    "last_tested", "next_test_due", "status",
    "tested_by", "evidence_id", "notes", "created_by",
    "created_at", "updated_at",
]
_RESULT_COLS = [
    "id", "test_id", "result", "tested_by", "tested_at",
    "evidence_id", "notes", "created_at",
]


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("TESTING_DB_PATH") or DB_PATH or "/tmp/khestra-testing.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    for col, dtype in {"sampling_methodology": "TEXT DEFAULT ''", "population_size": "INTEGER DEFAULT 0", "confidence_level": "REAL DEFAULT 0.0", "margin_of_error": "REAL DEFAULT 0.0"}.items():
        try:
            db.execute(f"ALTER TABLE tests ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass


def _test_to_row(t: dict) -> list:
    return [t.get(col, "") for col in _TEST_COLS]


def _row_to_test(row: sqlite3.Row) -> dict:
    return dict(row)


def _result_to_row(r: dict) -> list:
    return [r.get(col, "") for col in _RESULT_COLS]


def _row_to_result(row: sqlite3.Row) -> dict:
    return dict(row)


def _compute_next_due(frequency: str) -> str:
    if frequency == "once":
        return ""
    now = datetime.now(timezone.utc)
    if frequency == "daily":
        d = now + timedelta(days=1)
    elif frequency == "weekly":
        d = now + timedelta(weeks=1)
    elif frequency == "monthly":
        day = now.day
        month = now.month + 1
        year = now.year
        if month > 12:
            month = 1
            year += 1
        try:
            d = now.replace(year=year, month=month)
        except ValueError:
            import calendar
            last = calendar.monthrange(year, month)[1]
            d = now.replace(year=year, month=month, day=last)
    elif frequency == "quarterly":
        month = now.month + 3
        year = now.year
        if month > 12:
            month -= 12
            year += 1
        try:
            d = now.replace(year=year, month=month)
        except ValueError:
            import calendar
            last = calendar.monthrange(year, month)[1]
            d = now.replace(year=year, month=month, day=last)
    elif frequency == "annual":
        try:
            d = now.replace(year=now.year + 1)
        except ValueError:
            d = now.replace(year=now.year + 1, month=2, day=28)
    elif frequency == "continuous":
        return ""
    else:
        return ""
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = str(Path(data_dir) / "tests.db")

    old_json = Path(data_dir) / "tests.json"
    db_path = Path(DB_PATH)

    if not db_path.exists() and old_json.exists():
        _migrate_from_json(old_json)
    else:
        db = _get_db()
        db.close()


def _migrate_from_json(json_path: Path):
    raw = json.loads(json_path.read_text())
    tests = raw.get("tests", {})
    results_map = raw.get("results", {})
    db = _get_db()
    try:
        for t in tests.values():
            placeholders = ", ".join(["?"] * len(_TEST_COLS))
            cols = ", ".join(_TEST_COLS)
            db.execute(f"INSERT INTO tests ({cols}) VALUES ({placeholders})", _test_to_row(t))
        for test_id, results in results_map.items():
            for r in results:
                r.setdefault("test_id", test_id)
                placeholders = ", ".join(["?"] * len(_RESULT_COLS))
                cols = ", ".join(_RESULT_COLS)
                db.execute(f"INSERT INTO test_results ({cols}) VALUES ({placeholders})", _result_to_row(r))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        for t in tests.values():
            try:
                placeholders = ", ".join(["?"] * len(_TEST_COLS))
                cols = ", ".join(_TEST_COLS)
                db.execute(f"INSERT INTO tests ({cols}) VALUES ({placeholders})", _test_to_row(t))
            except sqlite3.IntegrityError:
                pass
        for test_id, results in results_map.items():
            for r in results:
                try:
                    r.setdefault("test_id", test_id)
                    placeholders = ", ".join(["?"] * len(_RESULT_COLS))
                    cols = ", ".join(_RESULT_COLS)
                    db.execute(f"INSERT INTO test_results ({cols}) VALUES ({placeholders})", _result_to_row(r))
                except sqlite3.IntegrityError:
                    pass
        db.commit()
    finally:
        db.close()
    json_path.rename(json_path.with_suffix(json_path.suffix + ".migrated"))


def list_tests(
    control_id: str | None = None,
    framework: str | None = None,
    status: str | None = None,
    frequency: str | None = None,
) -> list[dict]:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if control_id:
            conditions.append("control_id = ?")
            params.append(control_id)
        if framework:
            conditions.append("framework = ?")
            params.append(framework)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if frequency:
            conditions.append("frequency = ?")
            params.append(frequency)
        sql = "SELECT * FROM tests"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC"
        return [dict(r) for r in db.execute(sql, params).fetchall()]
    finally:
        db.close()


def get_test(test_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM tests WHERE id = ?", (test_id,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def create_test(
    control_id: str,
    framework: str,
    test_procedure: str,
    frequency: str = "",
    sample_size: int = 0,
    sampling_methodology: str = "",
    population_size: int = 0,
    confidence_level: float = 0.0,
    margin_of_error: float = 0.0,
    notes: str = "",
    created_by: str = "",
) -> dict:
    now = utcnow()
    test = ControlTest(
        id=uuid4().hex[:12],
        control_id=control_id,
        framework=framework,
        test_procedure=test_procedure,
        frequency=frequency,
        sample_size=sample_size,
        sampling_methodology=sampling_methodology,
        population_size=population_size,
        confidence_level=confidence_level,
        margin_of_error=margin_of_error,
        notes=notes,
        created_by=created_by,
        created_at=now,
        updated_at=now,
        next_test_due=_compute_next_due(frequency),
    )
    d = test.to_dict()
    db = _get_db()
    try:
        placeholders = ", ".join(["?"] * len(_TEST_COLS))
        cols = ", ".join(_TEST_COLS)
        db.execute(f"INSERT INTO tests ({cols}) VALUES ({placeholders})", _test_to_row(d))
        db.commit()
    finally:
        db.close()
    return d


def update_test(
    test_id: str,
    *,
    control_id: str | None = None,
    framework: str | None = None,
    test_procedure: str | None = None,
    frequency: str | None = None,
    sample_size: int | None = None,
    status: str | None = None,
    last_tested: str | None = None,
    tested_by: str | None = None,
    evidence_id: str | None = None,
    notes: str | None = None,
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM tests WHERE id = ?", (test_id,)).fetchone()
        if not row:
            return None
        test = dict(row)

        if control_id is not None:
            test["control_id"] = control_id
        if framework is not None:
            test["framework"] = framework
        if test_procedure is not None:
            test["test_procedure"] = test_procedure
        if frequency is not None:
            test["frequency"] = frequency
            test["next_test_due"] = _compute_next_due(frequency)
        if sample_size is not None:
            test["sample_size"] = sample_size
        if status is not None:
            test["status"] = status
        if last_tested is not None:
            test["last_tested"] = last_tested
        if tested_by is not None:
            test["tested_by"] = tested_by
        if evidence_id is not None:
            test["evidence_id"] = evidence_id
        if notes is not None:
            test["notes"] = notes

        test["updated_at"] = utcnow()
        set_clause = ", ".join(f"{c} = ?" for c in _TEST_COLS[1:])
        db.execute(
            f"UPDATE tests SET {set_clause} WHERE id = ?",
            _test_to_row(test)[1:] + [test["id"]],
        )
        db.commit()
        return test
    finally:
        db.close()


def delete_test(test_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM tests WHERE id = ?", (test_id,))
        db.execute("DELETE FROM test_results WHERE test_id = ?", (test_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


def add_result(
    test_id: str,
    result: str,
    tested_by: str,
    evidence_id: str = "",
    notes: str = "",
) -> dict | None:
    db = _get_db()
    try:
        test_row = db.execute("SELECT * FROM tests WHERE id = ?", (test_id,)).fetchone()
        if not test_row:
            return None
        test = dict(test_row)
        now = utcnow()
        res = TestResult(
            id=uuid4().hex[:12],
            test_id=test_id,
            result=result,
            tested_by=tested_by,
            tested_at=now,
            evidence_id=evidence_id,
            notes=notes,
            created_at=now,
        )
        d = res.to_dict()
        placeholders = ", ".join(["?"] * len(_RESULT_COLS))
        cols = ", ".join(_RESULT_COLS)
        db.execute(f"INSERT INTO test_results ({cols}) VALUES ({placeholders})", _result_to_row(d))

        test["status"] = result
        test["last_tested"] = now
        test["tested_by"] = tested_by
        test["evidence_id"] = evidence_id or test.get("evidence_id", "")
        test["updated_at"] = now
        set_clause = ", ".join(f"{c} = ?" for c in _TEST_COLS[1:])
        db.execute(
            f"UPDATE tests SET {set_clause} WHERE id = ?",
            _test_to_row(test)[1:] + [test["id"]],
        )
        db.commit()
        return d
    finally:
        db.close()


def get_results(test_id: str) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT * FROM test_results WHERE test_id = ? ORDER BY created_at DESC",
            (test_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def get_stats(framework: str | None = None) -> dict:
    items = list_tests(framework=framework)
    total = len(items)
    by_status: dict[str, int] = {}
    by_framework: dict[str, int] = {}
    passed = 0
    for t in items:
        s = t.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        f = t.get("framework", "unknown")
        by_framework[f] = by_framework.get(f, 0) + 1
        if s == "pass":
            passed += 1
    pass_rate = round(passed / total * 100, 1) if total else 0.0
    return {
        "total": total,
        "by_status": by_status,
        "by_framework": by_framework,
        "pass_rate": pass_rate,
        "not_tested": by_status.get("not_tested", 0),
        "pass": by_status.get("pass", 0),
        "fail": by_status.get("fail", 0),
        "needs_review": by_status.get("needs_review", 0),
    }


def overdue_test_count(framework: str | None = None) -> int:
    items = list_tests(framework=framework)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return sum(1 for t in items if t.get("next_test_due", "") and t["next_test_due"] < now)
