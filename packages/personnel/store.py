import sqlite3
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

DB_PATH: str | None = None


def get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("PERSONNEL_DB_PATH") or DB_PATH or "/tmp/khestra-personnel.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    return db

def _get_db() -> sqlite3.Connection:
    return get_db()


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS personnel (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL DEFAULT '',
  email TEXT DEFAULT '',
  role TEXT DEFAULT '',
  department TEXT DEFAULT '',
  status TEXT DEFAULT 'active',
  frameworks TEXT DEFAULT '[]',
  org_id TEXT DEFAULT '',
  workspace_id TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT '',
  mfa_status TEXT DEFAULT '',
  last_login TEXT DEFAULT '',
  is_privileged INTEGER DEFAULT 0,
  external_id TEXT DEFAULT '',
  phone TEXT DEFAULT '',
  location TEXT DEFAULT '',
  manager TEXT DEFAULT '',
  employee_id TEXT DEFAULT '',
  provider TEXT DEFAULT '',
  raw_attributes TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL DEFAULT ''
);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    for col, dtype in {
        "mfa_status": "TEXT DEFAULT ''",
        "last_login": "TEXT DEFAULT ''",
        "is_privileged": "INTEGER DEFAULT 0",
        "external_id": "TEXT DEFAULT ''",
        "phone": "TEXT DEFAULT ''",
        "location": "TEXT DEFAULT ''",
        "manager": "TEXT DEFAULT ''",
        "employee_id": "TEXT DEFAULT ''",
        "provider": "TEXT DEFAULT ''",
        "raw_attributes": "TEXT DEFAULT '{}'",
    }.items():
        try:
            db.execute(f"ALTER TABLE personnel ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("frameworks", "raw_attributes"):
        val = d.get(col)
        if isinstance(val, str):
            try:
                import json
                d[col] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                d[col] = {} if col == "raw_attributes" else []
    if "is_privileged" in d and not isinstance(d["is_privileged"], bool):
        d["is_privileged"] = bool(d["is_privileged"])
    return d


def _rows_to_list(rows: list[sqlite3.Row]) -> list[dict]:
    return [_row_to_dict(r) for r in rows]


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = os.environ.get("PERSONNEL_DB_PATH") or str(Path(data_dir) / "personnel.db")
    db = _get_db()
    _ensure_schema(db)
    count = db.execute("SELECT COUNT(*) as c FROM personnel").fetchone()["c"]
    db.close()
    if count == 0:
        seed_data(org_id="demo", workspace_id="demo")


def list_personnel(org_id: str | None = None, framework_id: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        if org_id:
            rows = db.execute("SELECT * FROM personnel WHERE org_id = ? ORDER BY created_at DESC", (org_id,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM personnel ORDER BY created_at DESC").fetchall()
        items = _rows_to_list(rows)
        if framework_id:
            items = [p for p in items if framework_id in p.get("frameworks", [])]
        return items
    finally:
        db.close()


def get_person(pid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM personnel WHERE id = ?", (pid,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


_PERSONNEL_COLS = (
    "id", "name", "email", "role", "department", "status",
    "frameworks", "org_id", "workspace_id", "created_at",
    "external_id", "phone", "location", "manager", "employee_id",
    "provider", "raw_attributes", "mfa_status", "last_login",
    "is_privileged",
)


def create_person(
    name: str,
    email: str = "",
    role: str = "",
    department: str = "",
    status: str = "active",
    org_id: str = "",
    workspace_id: str = "",
    frameworks: list[str] | None = None,
    external_id: str = "",
    phone: str = "",
    location: str = "",
    manager: str = "",
    employee_id: str = "",
    provider: str = "",
    raw_attributes: str | dict | None = None,
    mfa_status: str = "",
    last_login: str = "",
    is_privileged: bool = False,
) -> dict:
    pid = uuid4().hex[:12]
    now = _utcnow()
    db = _get_db()
    try:
        cols = (
            "id", "name", "email", "role", "department", "status",
            "frameworks", "org_id", "workspace_id", "created_at",
            "external_id", "phone", "location", "manager", "employee_id",
            "provider", "raw_attributes", "mfa_status", "last_login",
            "is_privileged",
        )
        vals = (
            pid, name, email, role, department, status,
            _json(frameworks or []), org_id, workspace_id, now,
            external_id, phone, location, manager, employee_id,
            provider, _json(raw_attributes or {}),
            mfa_status, last_login, 1 if is_privileged else 0,
        )
        placeholders = ", ".join("?" for _ in cols)
        db.execute(f"INSERT INTO personnel ({', '.join(cols)}) VALUES ({placeholders})", vals)
        db.commit()
    finally:
        db.close()
    return get_person(pid) or {}


def update_person(pid: str, **kwargs) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM personnel WHERE id = ?", (pid,)).fetchone()
        if not row:
            return None
        current = dict(row)
        for k, val in kwargs.items():
            if val is not None and k != "id":
                if isinstance(val, list) or isinstance(val, dict):
                    current[k] = _json(val)
                elif isinstance(val, bool):
                    current[k] = 1 if val else 0
                else:
                    current[k] = val
        current["updated_at"] = _utcnow()
        sets = ", ".join(f"{k} = ?" for k in kwargs if k != "id")
        if not sets:
            return _row_to_dict(row)
        vals = []
        for k in kwargs:
            if k == "id":
                continue
            v = kwargs[k]
            if v is not None:
                if isinstance(v, list) or isinstance(v, dict):
                    vals.append(_json(v))
                elif isinstance(v, bool):
                    vals.append(1 if v else 0)
                else:
                    vals.append(v)
            else:
                vals.append(None)
        db.execute(f"UPDATE personnel SET {sets}, updated_at = ? WHERE id = ?",
                   (*vals, _utcnow(), pid))
        db.commit()
    finally:
        db.close()
    return get_person(pid)


def delete_person(pid: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT id FROM personnel WHERE id = ?", (pid,)).fetchone()
        if not row:
            return False
        db.execute("DELETE FROM personnel WHERE id = ?", (pid,))
        db.commit()
        return True
    finally:
        db.close()


def mark_missing_as_inactive(provider: str, org_id: str, seen_external_ids: set[str]) -> int:
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT id, external_id FROM personnel WHERE provider = ? AND org_id = ? AND external_id != ''",
            (provider, org_id),
        ).fetchall()
        to_deactivate = [r["id"] for r in rows if r["external_id"] not in seen_external_ids]
        if not to_deactivate:
            return 0
        placeholders = ", ".join("?" for _ in to_deactivate)
        now = _utcnow()
        db.execute(
            f"UPDATE personnel SET status = 'inactive', updated_at = ? WHERE id IN ({placeholders})",
            (now, *to_deactivate),
        )
        db.commit()
        return len(to_deactivate)
    finally:
        db.close()


def seed_data(org_id: str = "", workspace_id: str = "") -> int:
    db = _get_db()
    try:
        count = db.execute("SELECT COUNT(*) as c FROM personnel").fetchone()["c"]
        if count > 0:
            return 0
    finally:
        db.close()

    samples = [
        {"name": "Alice Chen", "email": "alice@example.com", "role": "Security Engineer", "department": "Engineering", "fw": ["SOC2"], "phone": "+1-555-0101", "location": "Seattle, WA"},
        {"name": "Bob Martinez", "email": "bob@example.com", "role": "Compliance Officer", "department": "Compliance", "fw": ["SOC2"], "phone": "+1-555-0102", "location": "Austin, TX"},
        {"name": "Carol Williams", "email": "carol@example.com", "role": "Engineering Manager", "department": "Engineering", "fw": ["CMMC"], "phone": "+1-555-0103", "location": "Portland, OR"},
        {"name": "David Kim", "email": "david@example.com", "role": "Data Protection Officer", "department": "Legal", "fw": ["AIGov"], "phone": "+1-555-0104", "location": "Chicago, IL"},
        {"name": "Eva Johansson", "email": "eva@example.com", "role": "AI Ethics Lead", "department": "Governance", "fw": ["AIGov"], "phone": "+1-555-0105", "location": "New York, NY"},
        {"name": "Sam Rivera", "email": "srivera@trident.onmicrosoft.com", "role": "IT Security Lead / ISO", "department": "Security", "fw": ["CMMC", "SOC2"], "mfa": "enabled", "priv": True, "phone": "+1-937-555-0101", "location": "Dayton, OH"},
        {"name": "Alex Kim", "email": "akim@trident.onmicrosoft.com", "role": "Systems Administrator", "department": "Engineering", "fw": ["CMMC", "SOC2"], "mfa": "enabled", "priv": True, "phone": "+1-937-555-0102", "location": "Dayton, OH"},
        {"name": "Jordan Lee", "email": "jlee@trident.onmicrosoft.com", "role": "VP Operations", "department": "Executive", "fw": ["CMMC", "SOC2"], "mfa": "enabled", "priv": False, "phone": "+1-937-555-0103", "location": "Dayton, OH"},
    ]
    count = 0
    for d in samples:
        pid = uuid4().hex[:12]
        now = _utcnow()
        db = _get_db()
        try:
            cols = (
                "id", "name", "email", "role", "department", "status",
                "frameworks", "org_id", "workspace_id", "created_at",
                "phone", "location", "mfa_status", "is_privileged",
            )
            vals = (
                pid, d["name"], d["email"], d["role"], d["department"], "active",
                _json(d["fw"]), org_id, workspace_id, now,
                d.get("phone", ""), d.get("location", ""),
                d.get("mfa", ""), 1 if d.get("priv") else 0,
            )
            placeholders = ", ".join("?" for _ in cols)
            db.execute(f"INSERT INTO personnel ({', '.join(cols)}) VALUES ({placeholders})", vals)
            db.commit()
            count += 1
        finally:
            db.close()
    return count


def _json(val) -> str:
    import json
    return json.dumps(val)
