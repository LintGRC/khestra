import json
import sqlite3
from pathlib import Path
from uuid import uuid4
from typing import Optional

from .models import RaciAssignment, utcnow


DB_PATH: str | None = None


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS assignments (
  id TEXT PRIMARY KEY,
  org_id TEXT NOT NULL DEFAULT '',
  framework TEXT NOT NULL DEFAULT '',
  ref_type TEXT NOT NULL DEFAULT '',
  ref_id TEXT NOT NULL DEFAULT '',
  user_id TEXT NOT NULL DEFAULT '',
  user_name TEXT DEFAULT '',
  responsibility TEXT DEFAULT 'Responsible',
  notes TEXT DEFAULT '',
  created_at TEXT DEFAULT ''
);
"""

_COLS = [
    "id", "org_id", "framework", "ref_type", "ref_id",
    "user_id", "user_name", "responsibility", "notes", "created_at",
]


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = DB_PATH or "/tmp/khestra-raci.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)


def _obj_to_row(obj: dict) -> list:
    return [obj.get(col, "") for col in _COLS]


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = str(Path(data_dir) / "raci.db")

    old_json = Path(data_dir) / "raci.json"
    db_path = Path(DB_PATH)

    if not db_path.exists() and old_json.exists():
        _migrate_from_json(old_json)
    else:
        db = _get_db()
        db.close()


def _migrate_from_json(json_path: Path):
    raw = json.loads(json_path.read_text())
    items = raw.get("assignments", {})
    db = _get_db()
    try:
        cols_str = ", ".join(_COLS)
        placeholders = ", ".join(["?"] * len(_COLS))
        for item in items.values():
            db.execute(f"INSERT INTO assignments ({cols_str}) VALUES ({placeholders})", _obj_to_row(item))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        cols_str = ", ".join(_COLS)
        placeholders = ", ".join(["?"] * len(_COLS))
        for item in items.values():
            try:
                db.execute(f"INSERT INTO assignments ({cols_str}) VALUES ({placeholders})", _obj_to_row(item))
            except sqlite3.IntegrityError:
                pass
        db.commit()
    finally:
        db.close()
    json_path.rename(json_path.with_suffix(json_path.suffix + ".migrated"))


# ─── Assignments ──────────────────────────────────


def list_assignments(
    org_id: str | None = None,
    framework: str | None = None,
    ref_type: str | None = None,
    ref_id: str | None = None,
    user_id: str | None = None,
) -> list[dict]:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if org_id:
            conditions.append("org_id = ?")
            params.append(org_id)
        if framework:
            conditions.append("framework = ?")
            params.append(framework)
        if ref_type:
            conditions.append("ref_type = ?")
            params.append(ref_type)
        if ref_id:
            conditions.append("ref_id = ?")
            params.append(ref_id)
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        sql = "SELECT * FROM assignments"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        return [dict(r) for r in db.execute(sql, params).fetchall()]
    finally:
        db.close()


def get_assignment(assignment_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def create_assignment(
    org_id: str,
    framework: str,
    ref_type: str,
    ref_id: str,
    user_id: str,
    user_name: str = "",
    responsibility: str = "Responsible",
    notes: str = "",
) -> dict:
    a = RaciAssignment(
        id=uuid4().hex[:12],
        org_id=org_id,
        framework=framework,
        ref_type=ref_type,
        ref_id=ref_id,
        user_id=user_id,
        user_name=user_name,
        responsibility=responsibility,
        notes=notes,
        created_at=utcnow(),
    )
    d = a.to_dict()
    db = _get_db()
    try:
        cols_str = ", ".join(_COLS)
        placeholders = ", ".join(["?"] * len(_COLS))
        db.execute(f"INSERT INTO assignments ({cols_str}) VALUES ({placeholders})", _obj_to_row(d))
        db.commit()
    finally:
        db.close()
    return d


def update_assignment(
    assignment_id: str,
    *,
    responsibility: str | None = None,
    user_id: str | None = None,
    user_name: str | None = None,
    notes: str | None = None,
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
        if not row:
            return None
        a = dict(row)
        if responsibility is not None:
            a["responsibility"] = responsibility
        if user_id is not None:
            a["user_id"] = user_id
        if user_name is not None:
            a["user_name"] = user_name
        if notes is not None:
            a["notes"] = notes
        set_clause = ", ".join(f"{c} = ?" for c in _COLS[1:])
        db.execute(f"UPDATE assignments SET {set_clause} WHERE id = ?", _obj_to_row(a)[1:] + [a["id"]])
        db.commit()
        return a
    finally:
        db.close()


def delete_assignment(assignment_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


def get_raci_matrix(org_id: str, framework: str | None = None, ref_type: str | None = None) -> dict:
    items = list_assignments(org_id=org_id, framework=framework, ref_type=ref_type)
    matrix: dict[str, dict[str, dict]] = {}
    for a in items:
        key = f"{a['framework']}:{a['ref_type']}:{a['ref_id']}"
        if key not in matrix:
            matrix[key] = {
                "framework": a["framework"],
                "ref_type": a["ref_type"],
                "ref_id": a["ref_id"],
                "assignments": [],
            }
        matrix[key]["assignments"].append(a)
    return {"items": list(matrix.values())}
