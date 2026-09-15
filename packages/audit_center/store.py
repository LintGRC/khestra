import json
import sqlite3
from pathlib import Path
from uuid import uuid4
from typing import Optional

from .models import (
    Audit, EvidenceRequest,
    utcnow, AUDIT_STATUSES, AUDIT_TYPES, REQUEST_STATUSES,
)


DB_PATH: str | None = None


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS audits (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '',
  framework TEXT DEFAULT '',
  audit_type TEXT DEFAULT '',
  start_date TEXT DEFAULT '',
  end_date TEXT DEFAULT '',
  status TEXT DEFAULT 'planned',
  auditor_name TEXT DEFAULT '',
  auditor_email TEXT DEFAULT '',
  scope_notes TEXT DEFAULT '',
  preparation_notes TEXT DEFAULT '',
  control_id TEXT DEFAULT '',
  created_by TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS evidence_requests (
  id TEXT PRIMARY KEY,
  audit_id TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT '',
  control_id TEXT DEFAULT '',
  description TEXT DEFAULT '',
  requested_by TEXT DEFAULT '',
  assigned_to TEXT DEFAULT '',
  status TEXT DEFAULT 'open',
  evidence_id TEXT DEFAULT '',
  evidence_notes TEXT DEFAULT '',
  due_date TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);
"""

_AUDIT_COLS = [
    "id", "title", "framework", "audit_type", "start_date", "end_date",
    "status", "auditor_name", "auditor_email", "scope_notes",
    "preparation_notes", "control_id", "created_by", "created_at", "updated_at",
]
_REQUEST_COLS = [
    "id", "audit_id", "title", "control_id", "description",
    "requested_by", "assigned_to", "status", "evidence_id",
    "evidence_notes", "due_date", "created_at", "updated_at",
]


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = DB_PATH or "/tmp/khestra-audit-center.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    try:
        db.execute("ALTER TABLE audits ADD COLUMN control_id TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass


def _audit_to_row(a: dict) -> list:
    return [a.get(col, "") for col in _AUDIT_COLS]


def _row_to_audit(row: sqlite3.Row) -> dict:
    return dict(row)


def _request_to_row(r: dict) -> list:
    return [r.get(col, "") for col in _REQUEST_COLS]


def _row_to_request(row: sqlite3.Row) -> dict:
    return dict(row)


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = str(Path(data_dir) / "audit-center.db")

    old_json = Path(data_dir) / "audit-center.json"
    db_path = Path(DB_PATH)

    if not db_path.exists() and old_json.exists():
        _migrate_from_json(old_json)
    else:
        db = _get_db()
        db.close()


def _migrate_from_json(json_path: Path):
    raw = json.loads(json_path.read_text())
    audits = raw.get("audits", {})
    requests = raw.get("evidence_requests", {})
    db = _get_db()
    try:
        for a in audits.values():
            placeholders = ", ".join(["?"] * len(_AUDIT_COLS))
            cols = ", ".join(_AUDIT_COLS)
            db.execute(f"INSERT INTO audits ({cols}) VALUES ({placeholders})", _audit_to_row(a))
        for r in requests.values():
            placeholders = ", ".join(["?"] * len(_REQUEST_COLS))
            cols = ", ".join(_REQUEST_COLS)
            db.execute(f"INSERT INTO evidence_requests ({cols}) VALUES ({placeholders})", _request_to_row(r))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        for a in audits.values():
            try:
                placeholders = ", ".join(["?"] * len(_AUDIT_COLS))
                cols = ", ".join(_AUDIT_COLS)
                db.execute(f"INSERT INTO audits ({cols}) VALUES ({placeholders})", _audit_to_row(a))
            except sqlite3.IntegrityError:
                pass
        for r in requests.values():
            try:
                placeholders = ", ".join(["?"] * len(_REQUEST_COLS))
                cols = ", ".join(_REQUEST_COLS)
                db.execute(f"INSERT INTO evidence_requests ({cols}) VALUES ({placeholders})", _request_to_row(r))
            except sqlite3.IntegrityError:
                pass
        db.commit()
    finally:
        db.close()
    json_path.rename(json_path.with_suffix(json_path.suffix + ".migrated"))


# ─── Audits CRUD ────────────────────────────


def list_audits(
    framework: str | None = None,
    audit_type: str | None = None,
    status: str | None = None,
    auditor_name: str | None = None,
    control_id: str | None = None,
) -> list[dict]:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if framework:
            conditions.append("framework = ?")
            params.append(framework)
        if audit_type:
            conditions.append("audit_type = ?")
            params.append(audit_type)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if auditor_name:
            conditions.append("auditor_name = ?")
            params.append(auditor_name)
        if control_id:
            conditions.append("control_id = ?")
            params.append(control_id)
        sql = "SELECT * FROM audits"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC"
        return [dict(r) for r in db.execute(sql, params).fetchall()]
    finally:
        db.close()


def get_audit(audit_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM audits WHERE id = ?", (audit_id,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def create_audit(
    title: str,
    framework: str = "",
    audit_type: str = "",
    start_date: str = "",
    end_date: str = "",
    auditor_name: str = "",
    auditor_email: str = "",
    scope_notes: str = "",
    preparation_notes: str = "",
    control_id: str = "",
    created_by: str = "",
) -> dict:
    now = utcnow()
    audit = Audit(
        id=uuid4().hex[:12],
        title=title,
        framework=framework,
        audit_type=audit_type,
        start_date=start_date,
        end_date=end_date,
        status="planned",
        auditor_name=auditor_name,
        auditor_email=auditor_email,
        scope_notes=scope_notes,
        preparation_notes=preparation_notes,
        control_id=control_id,
        created_by=created_by,
        created_at=now,
        updated_at=now,
    )
    d = audit.to_dict()
    db = _get_db()
    try:
        placeholders = ", ".join(["?"] * len(_AUDIT_COLS))
        cols = ", ".join(_AUDIT_COLS)
        db.execute(f"INSERT INTO audits ({cols}) VALUES ({placeholders})", _audit_to_row(d))
        db.commit()
    finally:
        db.close()
    return d


def update_audit(
    audit_id: str,
    *,
    title: str | None = None,
    framework: str | None = None,
    audit_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    auditor_name: str | None = None,
    auditor_email: str | None = None,
    scope_notes: str | None = None,
    preparation_notes: str | None = None,
    control_id: str | None = None,
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM audits WHERE id = ?", (audit_id,)).fetchone()
        if not row:
            return None
        audit = dict(row)

        if title is not None:
            audit["title"] = title
        if framework is not None:
            audit["framework"] = framework
        if audit_type is not None:
            audit["audit_type"] = audit_type
        if start_date is not None:
            audit["start_date"] = start_date
        if end_date is not None:
            audit["end_date"] = end_date
        if status is not None:
            audit["status"] = status
        if auditor_name is not None:
            audit["auditor_name"] = auditor_name
        if auditor_email is not None:
            audit["auditor_email"] = auditor_email
        if scope_notes is not None:
            audit["scope_notes"] = scope_notes
        if preparation_notes is not None:
            audit["preparation_notes"] = preparation_notes
        if control_id is not None:
            audit["control_id"] = control_id

        audit["updated_at"] = utcnow()
        set_clause = ", ".join(f"{c} = ?" for c in _AUDIT_COLS[1:])
        db.execute(
            f"UPDATE audits SET {set_clause} WHERE id = ?",
            _audit_to_row(audit)[1:] + [audit["id"]],
        )
        db.commit()
        return audit
    finally:
        db.close()


def delete_audit(audit_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM audits WHERE id = ?", (audit_id,))
        db.execute("DELETE FROM evidence_requests WHERE audit_id = ?", (audit_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


def freeze_audit(audit_id: str) -> dict | None:
    return update_audit(audit_id, status="frozen")


# ─── Evidence Requests CRUD ────────────────


def list_requests(audit_id: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        if audit_id:
            rows = db.execute(
                "SELECT * FROM evidence_requests WHERE audit_id = ? ORDER BY created_at DESC",
                (audit_id,),
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM evidence_requests ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def get_request(request_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM evidence_requests WHERE id = ?", (request_id,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def create_request(
    audit_id: str,
    title: str,
    control_id: str = "",
    description: str = "",
    requested_by: str = "",
    assigned_to: str = "",
    evidence_notes: str = "",
    due_date: str = "",
) -> dict:
    now = utcnow()
    req = EvidenceRequest(
        id=uuid4().hex[:12],
        audit_id=audit_id,
        control_id=control_id,
        title=title,
        description=description,
        requested_by=requested_by,
        assigned_to=assigned_to,
        status="open",
        evidence_id="",
        evidence_notes=evidence_notes,
        due_date=due_date,
        created_at=now,
        updated_at=now,
    )
    d = req.to_dict()
    db = _get_db()
    try:
        placeholders = ", ".join(["?"] * len(_REQUEST_COLS))
        cols = ", ".join(_REQUEST_COLS)
        db.execute(f"INSERT INTO evidence_requests ({cols}) VALUES ({placeholders})", _request_to_row(d))
        db.commit()
    finally:
        db.close()
    return d


def update_request(
    request_id: str,
    *,
    title: str | None = None,
    control_id: str | None = None,
    description: str | None = None,
    requested_by: str | None = None,
    assigned_to: str | None = None,
    status: str | None = None,
    evidence_id: str | None = None,
    evidence_notes: str | None = None,
    due_date: str | None = None,
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM evidence_requests WHERE id = ?", (request_id,)).fetchone()
        if not row:
            return None
        req = dict(row)

        if title is not None:
            req["title"] = title
        if control_id is not None:
            req["control_id"] = control_id
        if description is not None:
            req["description"] = description
        if requested_by is not None:
            req["requested_by"] = requested_by
        if assigned_to is not None:
            req["assigned_to"] = assigned_to
        if status is not None:
            req["status"] = status
        if evidence_id is not None:
            req["evidence_id"] = evidence_id
        if evidence_notes is not None:
            req["evidence_notes"] = evidence_notes
        if due_date is not None:
            req["due_date"] = due_date

        req["updated_at"] = utcnow()
        set_clause = ", ".join(f"{c} = ?" for c in _REQUEST_COLS[1:])
        db.execute(
            f"UPDATE evidence_requests SET {set_clause} WHERE id = ?",
            _request_to_row(req)[1:] + [req["id"]],
        )
        db.commit()
        return req
    finally:
        db.close()


def delete_request(request_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM evidence_requests WHERE id = ?", (request_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


# ─── Stats ─────────────────────────────────


def get_stats() -> dict:
    db = _get_db()
    try:
        audits = [dict(r) for r in db.execute("SELECT * FROM audits").fetchall()]
        requests = [dict(r) for r in db.execute("SELECT * FROM evidence_requests").fetchall()]
    finally:
        db.close()

    total_audits = len(audits)
    total_requests = len(requests)
    by_status: dict[str, int] = {}
    by_framework: dict[str, int] = {}
    by_audit_type: dict[str, int] = {}
    for a in audits:
        s = a.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        f = a.get("framework", "") or "none"
        by_framework[f] = by_framework.get(f, 0) + 1
        t = a.get("audit_type", "") or "none"
        by_audit_type[t] = by_audit_type.get(t, 0) + 1
    request_statuses: dict[str, int] = {}
    for r in requests:
        s = r.get("status", "unknown")
        request_statuses[s] = request_statuses.get(s, 0) + 1
    return {
        "total_audits": total_audits,
        "total_evidence_requests": total_requests,
        "by_status": by_status,
        "by_framework": by_framework,
        "by_audit_type": by_audit_type,
        "request_statuses": request_statuses,
    }
