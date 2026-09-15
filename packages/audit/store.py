import json
import sqlite3
from pathlib import Path
from uuid import uuid4
from typing import Optional

from .models import AuditEntry, utcnow


DB_PATH: str | None = None


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS audit_log (
  id TEXT PRIMARY KEY,
  action TEXT NOT NULL DEFAULT '',
  resource_type TEXT NOT NULL DEFAULT '',
  resource_id TEXT NOT NULL DEFAULT '',
  resource_name TEXT DEFAULT '',
  user TEXT DEFAULT '',
  timestamp TEXT DEFAULT '',
  details TEXT DEFAULT '',
  framework TEXT DEFAULT '',
  source TEXT DEFAULT ''
);
"""

_COLS = [
    "id", "action", "resource_type", "resource_id", "resource_name",
    "user", "timestamp", "details", "framework", "source",
]


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = DB_PATH or "/tmp/khestra-audit.db"
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
    DB_PATH = str(Path(data_dir) / "audit.db")

    old_jsonl = Path(data_dir) / "audit.jsonl"
    db_path = Path(DB_PATH)

    if not db_path.exists() and old_jsonl.exists():
        _migrate_from_jsonl(old_jsonl)
    else:
        db = _get_db()
        db.close()


def _migrate_from_jsonl(jsonl_path: Path):
    entries: list[dict] = []
    for line in jsonl_path.read_text().strip().split("\n"):
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    if not entries:
        jsonl_path.rename(jsonl_path.with_suffix(jsonl_path.suffix + ".migrated"))
        return

    db = _get_db()
    try:
        cols_str = ", ".join(_COLS)
        placeholders = ", ".join(["?"] * len(_COLS))
        for e in entries:
            db.execute(f"INSERT INTO audit_log ({cols_str}) VALUES ({placeholders})", _obj_to_row(e))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        cols_str = ", ".join(_COLS)
        placeholders = ", ".join(["?"] * len(_COLS))
        for e in entries:
            try:
                db.execute(f"INSERT INTO audit_log ({cols_str}) VALUES ({placeholders})", _obj_to_row(e))
            except sqlite3.IntegrityError:
                pass
        db.commit()
    finally:
        db.close()
    jsonl_path.rename(jsonl_path.with_suffix(jsonl_path.suffix + ".migrated"))


def log_action(
    action: str,
    resource_type: str,
    resource_id: str,
    resource_name: str = "",
    user: str = "",
    details: str = "",
    framework: str = "",
    source: str = "",
) -> AuditEntry:
    entry = AuditEntry(
        id=uuid4().hex[:12],
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        user=user or "system",
        timestamp=utcnow(),
        details=details,
        framework=framework,
        source=source or "platform",
    )
    d = entry.to_dict()
    db = _get_db()
    try:
        cols_str = ", ".join(_COLS)
        placeholders = ", ".join(["?"] * len(_COLS))
        db.execute(f"INSERT INTO audit_log ({cols_str}) VALUES ({placeholders})", _obj_to_row(d))
        db.commit()
    finally:
        db.close()
    return entry


def list_entries(
    action: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    user: str | None = None,
    framework: str | None = None,
    source: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if action:
            conditions.append("action = ?")
            params.append(action)
        if resource_type:
            conditions.append("resource_type = ?")
            params.append(resource_type)
        if resource_id:
            conditions.append("resource_id = ?")
            params.append(resource_id)
        if user:
            conditions.append("user = ?")
            params.append(user)
        if framework:
            conditions.append("framework = ?")
            params.append(framework)
        if source:
            conditions.append("source = ?")
            params.append(source)

        where = " WHERE " + " AND ".join(conditions) if conditions else ""

        total = db.execute(f"SELECT COUNT(*) as c FROM audit_log{where}", params).fetchone()["c"]
        rows = db.execute(
            f"SELECT * FROM audit_log{where} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

        return {
            "entries": [dict(r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        db.close()


def get_entry(entry_id: str) -> AuditEntry | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM audit_log WHERE id = ?", (entry_id,)).fetchone()
        return AuditEntry.from_dict(dict(row)) if row else None
    finally:
        db.close()


def get_stats(framework: str | None = None, source: str | None = None) -> dict:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if framework:
            conditions.append("framework = ?")
            params.append(framework)
        if source:
            conditions.append("source = ?")
            params.append(source)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""

        total = db.execute(f"SELECT COUNT(*) as c FROM audit_log{where}", params).fetchone()["c"]

        by_action = {r["action"]: r["c"] for r in db.execute(
            f"SELECT action, COUNT(*) as c FROM audit_log{where} GROUP BY action", params
        ).fetchall()}
        by_resource = {r["resource_type"]: r["c"] for r in db.execute(
            f"SELECT resource_type, COUNT(*) as c FROM audit_log{where} GROUP BY resource_type", params
        ).fetchall()}
        by_user = {r["user"]: r["c"] for r in db.execute(
            f"SELECT user, COUNT(*) as c FROM audit_log{where} GROUP BY user", params
        ).fetchall()}

        return {
            "total": total,
            "by_action": by_action,
            "by_resource": by_resource,
            "by_user": by_user,
        }
    finally:
        db.close()


def get_store():
    db = _get_db()
    try:
        rows = db.execute("SELECT * FROM audit_log").fetchall()
        return [AuditEntry.from_dict(dict(r)) for r in rows]
    finally:
        db.close()
