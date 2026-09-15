import json
import sqlite3
from pathlib import Path
from uuid import uuid4
from typing import Optional

from .models import Org, User, OrgMembership, utcnow


DB_PATH: str | None = None


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS orgs (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL DEFAULT '',
  slug TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  created_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL DEFAULT '',
  name TEXT NOT NULL DEFAULT '',
  oid TEXT DEFAULT '',
  default_role TEXT DEFAULT 'Viewer',
  created_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS memberships (
  id TEXT PRIMARY KEY,
  org_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'Member',
  joined_at TEXT DEFAULT ''
);
"""

_ORG_COLS = ["id", "name", "slug", "description", "created_at"]
_USER_COLS = ["id", "email", "name", "oid", "default_role", "created_at"]
_MEMBERSHIP_COLS = ["id", "org_id", "user_id", "role", "joined_at"]


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = DB_PATH or "/tmp/khestra-orgs.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    for col in ("oid",):
        try:
            db.execute("ALTER TABLE users ADD COLUMN oid TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass


def _obj_to_row(cols: list[str], obj: dict) -> list:
    return [obj.get(col, "") for col in cols]


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = str(Path(data_dir) / "orgs.db")

    old_json = Path(data_dir) / "orgs.json"
    db_path = Path(DB_PATH)

    if not db_path.exists() and old_json.exists():
        _migrate_from_json(old_json)
    else:
        db = _get_db()
        db.close()


def _migrate_from_json(json_path: Path):
    raw = json.loads(json_path.read_text())
    orgs = raw.get("orgs", {})
    users = raw.get("users", {})
    memberships = raw.get("memberships", {})
    db = _get_db()
    try:
        def _insert(table, cols, items):
            placeholders = ", ".join(["?"] * len(cols))
            cols_str = ", ".join(cols)
            for item in items.values():
                db.execute(f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})", _obj_to_row(cols, item))

        _insert("orgs", _ORG_COLS, orgs)
        _insert("users", _USER_COLS, users)
        _insert("memberships", _MEMBERSHIP_COLS, memberships)
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        for item in orgs.values():
            try:
                cols_str = ", ".join(_ORG_COLS)
                placeholders = ", ".join(["?"] * len(_ORG_COLS))
                db.execute(f"INSERT INTO orgs ({cols_str}) VALUES ({placeholders})", _obj_to_row(_ORG_COLS, item))
            except sqlite3.IntegrityError:
                pass
        for item in users.values():
            try:
                cols_str = ", ".join(_USER_COLS)
                placeholders = ", ".join(["?"] * len(_USER_COLS))
                db.execute(f"INSERT INTO users ({cols_str}) VALUES ({placeholders})", _obj_to_row(_USER_COLS, item))
            except sqlite3.IntegrityError:
                pass
        for item in memberships.values():
            try:
                cols_str = ", ".join(_MEMBERSHIP_COLS)
                placeholders = ", ".join(["?"] * len(_MEMBERSHIP_COLS))
                db.execute(f"INSERT INTO memberships ({cols_str}) VALUES ({placeholders})", _obj_to_row(_MEMBERSHIP_COLS, item))
            except sqlite3.IntegrityError:
                pass
        db.commit()
    finally:
        db.close()
    json_path.rename(json_path.with_suffix(json_path.suffix + ".migrated"))


# ─── Orgs ─────────────────────────────────────────


def list_orgs() -> list[dict]:
    db = _get_db()
    try:
        return [dict(r) for r in db.execute("SELECT * FROM orgs").fetchall()]
    finally:
        db.close()


def get_org(org_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM orgs WHERE id = ?", (org_id,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def get_org_by_slug(slug: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM orgs WHERE slug = ?", (slug,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def create_org(name: str, slug: str | None = None, description: str = "") -> dict:
    if not slug:
        slug = name.lower().replace(" ", "-").replace("_", "-")
    db = _get_db()
    try:
        existing = db.execute("SELECT 1 FROM orgs WHERE slug = ?", (slug,)).fetchone()
        if existing:
            raise ValueError(f"Org slug '{slug}' already exists")
        org = Org(
            id=uuid4().hex[:12],
            name=name,
            slug=slug,
            description=description,
            created_at=utcnow(),
        )
        d = org.to_dict()
        cols_str = ", ".join(_ORG_COLS)
        placeholders = ", ".join(["?"] * len(_ORG_COLS))
        db.execute(f"INSERT INTO orgs ({cols_str}) VALUES ({placeholders})", _obj_to_row(_ORG_COLS, d))
        db.commit()
        return d
    finally:
        db.close()


def update_org(org_id: str, *, name: str | None = None, slug: str | None = None, description: str | None = None) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM orgs WHERE id = ?", (org_id,)).fetchone()
        if not row:
            return None
        org = dict(row)
        if name is not None:
            org["name"] = name
        if slug is not None:
            dup = db.execute("SELECT 1 FROM orgs WHERE slug = ? AND id != ?", (slug, org_id)).fetchone()
            if dup:
                raise ValueError(f"Org slug '{slug}' already exists")
            org["slug"] = slug
        if description is not None:
            org["description"] = description
        set_clause = ", ".join(f"{c} = ?" for c in _ORG_COLS[1:])
        db.execute(f"UPDATE orgs SET {set_clause} WHERE id = ?", _obj_to_row(_ORG_COLS, org)[1:] + [org["id"]])
        db.commit()
        return org
    finally:
        db.close()


def delete_org(org_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM orgs WHERE id = ?", (org_id,))
        db.execute("DELETE FROM memberships WHERE org_id = ?", (org_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


# ─── Users ─────────────────────────────────────────


def list_users() -> list[dict]:
    db = _get_db()
    try:
        return [dict(r) for r in db.execute("SELECT * FROM users").fetchall()]
    finally:
        db.close()


def get_user(user_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def get_user_by_oid(oid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM users WHERE oid = ?", (oid,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def get_user_by_email(email: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def create_user(email: str, name: str, oid: str = "", default_role: str = "Viewer") -> dict:
    user = User(
        id=uuid4().hex[:12],
        email=email,
        name=name,
        oid=oid,
        default_role=default_role,
        created_at=utcnow(),
    )
    d = user.to_dict()
    db = _get_db()
    try:
        cols_str = ", ".join(_USER_COLS)
        placeholders = ", ".join(["?"] * len(_USER_COLS))
        db.execute(f"INSERT INTO users ({cols_str}) VALUES ({placeholders})", _obj_to_row(_USER_COLS, d))
        db.commit()
    finally:
        db.close()
    return d


def upsert_user(email: str, name: str, oid: str = "", default_role: str = "Viewer") -> dict:
    existing = get_user_by_email(email)
    if existing:
        return update_user(existing["id"], name=name, oid=oid, default_role=default_role) or existing
    existing_oid = get_user_by_oid(oid) if oid else None
    if existing_oid:
        return update_user(existing_oid["id"], name=name, email=email, default_role=default_role) or existing_oid
    return create_user(email, name, oid, default_role)


def update_user(user_id: str, *, name: str | None = None, email: str | None = None, oid: str | None = None, default_role: str | None = None) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return None
        u = dict(row)
        if name is not None:
            u["name"] = name
        if email is not None:
            u["email"] = email
        if oid is not None:
            u["oid"] = oid
        if default_role is not None:
            u["default_role"] = default_role
        set_clause = ", ".join(f"{c} = ?" for c in _USER_COLS[1:])
        db.execute(f"UPDATE users SET {set_clause} WHERE id = ?", _obj_to_row(_USER_COLS, u)[1:] + [u["id"]])
        db.commit()
        return u
    finally:
        db.close()


def delete_user(user_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.execute("DELETE FROM memberships WHERE user_id = ?", (user_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


# ─── Memberships ──────────────────────────────────


def list_memberships(org_id: str | None = None, user_id: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if org_id:
            conditions.append("org_id = ?")
            params.append(org_id)
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        sql = "SELECT * FROM memberships"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        return [dict(r) for r in db.execute(sql, params).fetchall()]
    finally:
        db.close()


def add_membership(org_id: str, user_id: str, role: str = "Member") -> dict:
    db = _get_db()
    try:
        org_exists = db.execute("SELECT 1 FROM orgs WHERE id = ?", (org_id,)).fetchone()
        if not org_exists:
            raise ValueError(f"Org {org_id} not found")
        user_exists = db.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user_exists:
            raise ValueError(f"User {user_id} not found")
        existing = db.execute(
            "SELECT * FROM memberships WHERE org_id = ? AND user_id = ?",
            (org_id, user_id),
        ).fetchone()
        if existing:
            return dict(existing)
        m = OrgMembership(
            id=uuid4().hex[:12],
            org_id=org_id,
            user_id=user_id,
            role=role,
            joined_at=utcnow(),
        )
        d = m.to_dict()
        cols_str = ", ".join(_MEMBERSHIP_COLS)
        placeholders = ", ".join(["?"] * len(_MEMBERSHIP_COLS))
        db.execute(f"INSERT INTO memberships ({cols_str}) VALUES ({placeholders})", _obj_to_row(_MEMBERSHIP_COLS, d))
        db.commit()
        return d
    finally:
        db.close()


def update_membership(membership_id: str, role: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM memberships WHERE id = ?", (membership_id,)).fetchone()
        if not row:
            return None
        db.execute("UPDATE memberships SET role = ? WHERE id = ?", (role, membership_id))
        db.commit()
        m = dict(row)
        m["role"] = role
        return m
    finally:
        db.close()


def remove_membership(membership_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM memberships WHERE id = ?", (membership_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


def get_user_orgs(user_id: str) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT o.*, m.role, m.id AS membership_id FROM orgs o "
            "JOIN memberships m ON m.org_id = o.id "
            "WHERE m.user_id = ?",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()
