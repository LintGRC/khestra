import json
import sqlite3
import os
import io
import csv
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone


DB_PATH: str | None = None


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("ASSETS_DB_PATH") or DB_PATH or "/tmp/khestra-assets.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL DEFAULT '',
  type TEXT DEFAULT '',
  owner TEXT DEFAULT '',
  description TEXT DEFAULT '',
  environment TEXT DEFAULT '',
  data_classification TEXT DEFAULT '',
  handles_cui INTEGER DEFAULT 0,
  location TEXT DEFAULT '',
  framework_tags TEXT DEFAULT '[]',
  workspace_id TEXT DEFAULT '',
  org_id TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT '',
  criticality TEXT DEFAULT ''
);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    for col, dtype in {"criticality": "TEXT DEFAULT ''"}.items():
        try:
            db.execute(f"ALTER TABLE assets ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = os.environ.get("ASSETS_DB_PATH") or str(Path(data_dir) / "assets.db")
    db = _get_db()
    _ensure_schema(db)
    count = db.execute("SELECT COUNT(*) as c FROM assets").fetchone()["c"]
    db.close()
    if count == 0:
        _seed_demo_assets()


def _seed_demo_assets():
    assets = [
        {"name": "APEX-LT-042", "type": "ENDPOINT", "owner": "it@company.com", "environment": "production", "data_classification": "confidential", "handles_cui": True, "location": "us-east-1"},
        {"name": "APEX-LT-017", "type": "ENDPOINT", "owner": "it@company.com", "environment": "production", "data_classification": "restricted", "handles_cui": True, "location": "us-east-1"},
        {"name": "MacBook-Pro-ISO", "type": "ENDPOINT", "owner": "eng@company.com", "environment": "production", "data_classification": "confidential", "handles_cui": False, "location": "remote"},
        {"name": "APEX-VM-DEV01", "type": "CLOUD", "owner": "devops@company.com", "environment": "development", "data_classification": "internal", "handles_cui": False, "location": "us-west-2"},
        {"name": "Contractor-LT-Temp", "type": "ENDPOINT", "owner": "procurement@company.com", "environment": "production", "data_classification": "restricted", "handles_cui": True, "location": "remote"},
    ]
    db = _get_db()
    try:
        for a in assets:
            aid = uuid4().hex[:12]
            now = _now()
            db.execute(
                "INSERT INTO assets (id, name, type, owner, description, environment, "
                "data_classification, handles_cui, location, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (aid, a["name"], a["type"], a["owner"], "",
                 a["environment"], a["data_classification"],
                 1 if a["handles_cui"] else 0, a["location"], now),
            )
        db.commit()
    finally:
        db.close()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("framework_tags",):
        if isinstance(d.get(col), str):
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                d[col] = []
    for col in ("handles_cui",):
        if col in d:
            d[col] = bool(d[col])
    return d


def list_assets() -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute("SELECT * FROM assets ORDER BY created_at DESC").fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def get_asset(aid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM assets WHERE id = ?", (aid,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def get_asset_by_name(name: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM assets WHERE name = ?", (name,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def create_asset(
    name: str,
    type: str = "",
    owner: str = "",
    description: str = "",
    environment: str = "",
    data_classification: str = "",
    handles_cui: bool = False,
    location: str = "",
    framework_tags: list[str] | None = None,
    workspace_id: str = "",
    org_id: str = "",
    criticality: str = "",
) -> dict:
    aid = uuid4().hex[:12]
    now = _now()
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO assets (id, name, type, owner, description, environment, "
            "data_classification, handles_cui, location, framework_tags, workspace_id, org_id, created_at, criticality) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (aid, name, type, owner, description, environment,
             data_classification, 1 if handles_cui else 0, location,
             json.dumps(framework_tags or []), workspace_id, org_id, now, criticality),
        )
        db.commit()
    finally:
        db.close()
    return get_asset(aid) or {}


def update_asset(aid: str, **kwargs) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM assets WHERE id = ?", (aid,)).fetchone()
        if not row:
            return None
        now = _now()
        sets = []
        vals = []
        for k, v in kwargs.items():
            if v is not None and k != "id":
                if isinstance(v, list):
                    sets.append(f"{k} = ?")
                    vals.append(json.dumps(v))
                elif isinstance(v, bool):
                    sets.append(f"{k} = ?")
                    vals.append(1 if v else 0)
                else:
                    sets.append(f"{k} = ?")
                    vals.append(v)
        if not sets:
            return _row_to_dict(row)
        sets.append("updated_at = ?")
        vals.append(now)
        vals.append(aid)
        db.execute(f"UPDATE assets SET {', '.join(sets)} WHERE id = ?", vals)
        db.commit()
    finally:
        db.close()
    return get_asset(aid)


def delete_asset(aid: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("SELECT id FROM assets WHERE id = ?", (aid,))
        if not cur.fetchone():
            return False
        db.execute("DELETE FROM assets WHERE id = ?", (aid,))
        db.commit()
        return True
    finally:
        db.close()


def import_csv(file_content: bytes) -> int:
    text = file_content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    count = 0
    db = _get_db()
    try:
        for row in reader:
            name = row.get("name", "").strip()
            if not name:
                continue
            aid = uuid4().hex[:12]
            now = _now()
            handles_cui = row.get("handles_cui", "").strip().lower() in ("yes", "true", "1", "y")
            db.execute(
                "INSERT INTO assets (id, name, type, owner, description, environment, "
                "data_classification, handles_cui, location, created_at, criticality) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (aid, name, row.get("type", ""), row.get("owner", ""),
                 row.get("description", ""), row.get("environment", ""),
                 row.get("data_classification", ""), 1 if handles_cui else 0,
                 row.get("location", ""), now, row.get("criticality", "")),
            )
            count += 1
        db.commit()
    finally:
        db.close()
    return count


def export_csv(assets: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["name", "type", "owner", "description", "environment",
                 "data_classification", "handles_cui", "location", "criticality"])
    for a in assets:
        w.writerow([
            a.get("name", ""), a.get("type", ""), a.get("owner", ""),
            a.get("description", ""), a.get("environment", ""),
            a.get("data_classification", ""),
            "Yes" if a.get("handles_cui") else "No", a.get("location", ""),
            a.get("criticality", ""),
        ])
    return buf.getvalue()
