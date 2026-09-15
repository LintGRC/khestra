"""SQLite user store for local authentication — orgs, invitations, multi-tenant."""

from __future__ import annotations

import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from .password import hash_password as _hash, verify_password as _verify


DB_PATH: str | None = None


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("AUTH_DB_PATH") or DB_PATH or "/tmp/khestra-auth.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS auth_users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL DEFAULT '',
  password_hash TEXT NOT NULL DEFAULT '',
  role TEXT NOT NULL DEFAULT 'Executive',
  org_id TEXT NOT NULL DEFAULT '',
  is_org_owner INTEGER NOT NULL DEFAULT 0,
  is_msp INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT '',
  deactivated INTEGER NOT NULL DEFAULT 0,
  token_version INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orgs (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL DEFAULT '',
  slug TEXT NOT NULL UNIQUE,
  plan TEXT NOT NULL DEFAULT 'trial',
  status TEXT NOT NULL DEFAULT 'active',
  trial_ends_at TEXT NOT NULL DEFAULT '',
  stripe_customer_id TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS invitations (
  id TEXT PRIMARY KEY,
  org_id TEXT NOT NULL DEFAULT '',
  email TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'Assessor',
  token TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT '',
  expires_at TEXT NOT NULL DEFAULT ''
);
"""


_AUTH_USER_NEW_COLS = {
    "token_version": "INTEGER NOT NULL DEFAULT 0",
    "org_id": "TEXT NOT NULL DEFAULT ''",
    "is_org_owner": "INTEGER NOT NULL DEFAULT 0",
    "is_msp": "INTEGER NOT NULL DEFAULT 0",
    "reset_token": "TEXT DEFAULT ''",
    "reset_token_expires": "TEXT DEFAULT ''",
}


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    for col, dtype in _AUTH_USER_NEW_COLS.items():
        try:
            db.execute(f"ALTER TABLE auth_users ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = os.environ.get("AUTH_DB_PATH") or str(Path(data_dir) / "auth.db")
    db = _get_db()
    _ensure_schema(db)
    count = db.execute("SELECT COUNT(*) as c FROM auth_users").fetchone()["c"]
    db.close()
    if count == 0:
        _seed_admin(data_dir)


def _make_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))[:48] or "org"


def _seed_admin(data_dir: str):
    email = os.environ.get("CMMC_ADMIN_EMAIL", "admin@example.com").strip()
    password = os.environ.get("CMMC_ADMIN_PASSWORD", "").strip()
    generated = not password
    if generated:
        import secrets as _secrets
        password = _secrets.token_urlsafe(12)
    org = create_org(name="Default Organization")
    try:
        create_user(
            email=email,
            name="Admin",
            password=password,
            role="Organization Admin",
            org_id=org["id"],
            is_org_owner=True,
        )
    except ValueError:
        # Another service seeded the shared auth DB first; its credentials win.
        return
    if generated:
        auth_db = os.environ.get("AUTH_DB_PATH", "").strip()
        log_dir = Path(auth_db).parent if auth_db else Path(data_dir)
        log_path = log_dir / "auth_admin_credentials.txt"
        log_path.write_text(f"Email: {email}\nPassword: {password}\n")
        print(f"Admin password not set via CMMC_ADMIN_PASSWORD. Generated a random "
              f"password \u2014 saved to {log_path}")


_VALID_ROLES = ("Organization Admin", "Compliance Manager", "Assessor", "Engineer", "Auditor", "Executive")

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+$")


def _valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email))


def _validate_role(role: str) -> str:
    if role not in _VALID_ROLES:
        raise ValueError(f"Invalid role. Must be one of {_VALID_ROLES}")
    return role


def _validate_password(password: str) -> str:
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    return password


def create_user(
    email: str,
    name: str,
    password: str,
    role: str = "Executive",
    org_id: str = "",
    is_org_owner: bool = False,
    is_msp: bool = False,
) -> dict:
    _validate_role(role)
    _validate_password(password)
    email = email.lower().strip()
    if not _valid_email(email):
        raise ValueError("Invalid email address")
    uid = uuid4().hex[:12]
    now = _now()
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO auth_users (id, email, name, password_hash, role, org_id, is_org_owner, is_msp, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (uid, email, name.strip(), _hash(password), role, org_id, int(is_org_owner), int(is_msp), now),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"User with email '{email}' already exists")
    finally:
        db.close()
    return {
        "id": uid,
        "email": email,
        "name": name.strip(),
        "role": role,
        "org_id": org_id,
        "is_org_owner": int(is_org_owner),
        "is_msp": int(is_msp),
        "created_at": now,
    }


def authenticate(email: str, password: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT * FROM auth_users WHERE email = ? AND deactivated = 0",
            (email.lower().strip(),),
        ).fetchone()
        if not row:
            return None
        if not _verify(password, row["password_hash"]):
            return None
        return dict(row)
    finally:
        db.close()


def is_user_active(user_id: str) -> bool:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT deactivated FROM auth_users WHERE id = ?", (user_id,)
        ).fetchone()
        return row is not None and row["deactivated"] == 0
    finally:
        db.close()


def is_user_role(user_id: str, role: str) -> bool:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT role, deactivated FROM auth_users WHERE id = ?", (user_id,)
        ).fetchone()
        return row is not None and row["deactivated"] == 0 and row["role"] == role
    finally:
        db.close()


def get_user_current_role(user_id: str) -> str | None:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT role, deactivated FROM auth_users WHERE id = ?", (user_id,)
        ).fetchone()
        if row and row["deactivated"] == 0:
            return row["role"]
        return None
    finally:
        db.close()


def get_user(user_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM auth_users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def get_user_by_email(email: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT * FROM auth_users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def list_users() -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT id, email, name, role, org_id, is_org_owner, is_msp, created_at, deactivated FROM auth_users ORDER BY created_at"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def find_admin_user() -> dict | None:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT * FROM auth_users WHERE role = 'Organization Admin' AND deactivated = 0 ORDER BY created_at LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def update_user_role(user_id: str, new_role: str) -> dict | None:
    _validate_role(new_role)
    db = _get_db()
    try:
        db.execute("UPDATE auth_users SET role = ? WHERE id = ?", (new_role, user_id))
        db.commit()
        return get_user(user_id)
    finally:
        db.close()


def update_user_password(user_id: str, new_password: str) -> bool:
    _validate_password(new_password)
    db = _get_db()
    try:
        db.execute(
            "UPDATE auth_users SET password_hash = ?, token_version = token_version + 1 WHERE id = ?",
            (_hash(new_password), user_id),
        )
        db.commit()
        return db.total_changes > 0
    finally:
        db.close()


def generate_reset_token(email: str) -> str | None:
    db = _get_db()
    try:
        user = db.execute(
            "SELECT id FROM auth_users WHERE email = ? AND deactivated = 0",
            (email.lower().strip(),),
        ).fetchone()
        if not user:
            return None
        token = secrets.token_urlsafe(32)
        expires = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        db.execute(
            "UPDATE auth_users SET reset_token = ?, reset_token_expires = ? WHERE id = ?",
            (token, expires, user["id"]),
        )
        db.commit()
        return token
    finally:
        db.close()


def validate_reset_token(token: str) -> dict | None:
    db = _get_db()
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        row = db.execute(
            "SELECT id, email FROM auth_users WHERE reset_token = ? AND reset_token_expires > ? AND deactivated = 0",
            (token, now),
        ).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def reset_password_with_token(token: str, new_password: str) -> bool:
    _validate_password(new_password)
    user = validate_reset_token(token)
    if not user:
        return False
    db = _get_db()
    try:
        db.execute(
            "UPDATE auth_users SET password_hash = ?, reset_token = '', reset_token_expires = '', token_version = token_version + 1 WHERE id = ?",
            (_hash(new_password), user["id"]),
        )
        db.commit()
        return db.total_changes > 0
    finally:
        db.close()


def delete_user(user_id: str) -> bool:
    db = _get_db()
    try:
        db.execute("UPDATE auth_users SET deactivated = 1 WHERE id = ?", (user_id,))
        db.commit()
        return db.total_changes > 0
    finally:
        db.close()


def user_count() -> int:
    db = _get_db()
    try:
        return db.execute("SELECT COUNT(*) as c FROM auth_users WHERE deactivated = 0").fetchone()["c"]
    finally:
        db.close()


# ── Orgs ─────────────────────────────────────────────────────────────────


def create_org(name: str, slug: str = "") -> dict:
    slug = (slug or _make_slug(name)).strip().lower()
    if not slug:
        slug = "org"
    import secrets as _secrets
    while get_org_by_slug(slug):
        slug = _make_slug(name)[:40] + "-" + _secrets.token_hex(3)
    oid = uuid4().hex[:12]
    now = _now()
    from datetime import datetime, timedelta, timezone as _tz
    trial_ends = (datetime.now(_tz.utc) + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO orgs (id, name, slug, plan, status, trial_ends_at, created_at) VALUES (?, ?, ?, 'trial', 'active', ?, ?)",
            (oid, name.strip(), slug, trial_ends, now),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"Organization with slug '{slug}' already exists")
    finally:
        db.close()
    return {"id": oid, "name": name.strip(), "slug": slug, "plan": "trial", "status": "active", "trial_ends_at": trial_ends, "created_at": now}


def get_org(org_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM orgs WHERE id = ?", (org_id,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def get_org_by_slug(slug: str) -> dict | None:
    if not slug:
        return None
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM orgs WHERE slug = ?", (slug.strip().lower(),)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def list_users_by_org(org_id: str) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT id, email, name, role, org_id, is_org_owner, is_msp, created_at, deactivated FROM auth_users WHERE org_id = ? ORDER BY created_at",
            (org_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def count_users_by_org(org_id: str) -> int:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT COUNT(*) as c FROM auth_users WHERE org_id = ? AND deactivated = 0",
            (org_id,),
        ).fetchone()
        return row["c"] if row else 0
    finally:
        db.close()


def update_user_org(user_id: str, org_id: str) -> bool:
    db = _get_db()
    try:
        db.execute("UPDATE auth_users SET org_id = ? WHERE id = ?", (org_id, user_id))
        db.commit()
        return db.total_changes > 0
    finally:
        db.close()


def update_user_org_owner(user_id: str, is_owner: bool) -> bool:
    db = _get_db()
    try:
        db.execute("UPDATE auth_users SET is_org_owner = ? WHERE id = ?", (1 if is_owner else 0, user_id))
        db.commit()
        return db.total_changes > 0
    finally:
        db.close()


# ── Invitations ──────────────────────────────────────────────────────────


def create_invitation(org_id: str, email: str, role: str) -> dict:
    _validate_role(role)
    email = email.lower().strip()
    if not _valid_email(email):
        raise ValueError("Invalid email address")
    existing = get_user_by_email(email)
    if existing and existing.get("org_id") == org_id:
        raise ValueError(f"User with email '{email}' is already in this org")
    import secrets as _secrets
    token = _secrets.token_urlsafe(32)
    inv_id = uuid4().hex[:12]
    now = _now()
    from datetime import datetime, timedelta, timezone as _tz
    expires = (datetime.now(_tz.utc) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO invitations (id, org_id, email, role, token, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (inv_id, org_id, email, role, token, now, expires),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"Duplicate invitation for '{email}'")
    finally:
        db.close()
    return {"id": inv_id, "org_id": org_id, "email": email, "role": role, "token": token, "created_at": now, "expires_at": expires}


def get_invitation(token: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM invitations WHERE token = ?", (token,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def accept_invitation(token: str, name: str, password: str) -> dict:
    _validate_password(password)
    inv = get_invitation(token)
    if not inv:
        raise ValueError("Invalid or expired invitation token")
    from datetime import datetime, timezone as _tz
    expires = datetime.fromisoformat(inv["expires_at"].replace("Z", "+00:00"))
    if expires < datetime.now(_tz.utc):
        raise ValueError("Invitation has expired")
    existing = get_user_by_email(inv["email"])
    if existing:
        if existing["deactivated"] == 1:
            raise ValueError("User with this email is deactivated. Contact your admin.")
        update_user_org(existing["id"], inv["org_id"])
        update_user_role(existing["id"], inv["role"])
        user = get_user(existing["id"])
    else:
        user = create_user(
            email=inv["email"],
            name=name or inv["email"],
            password=password,
            role=inv["role"],
            org_id=inv["org_id"],
        )
    db = _get_db()
    try:
        db.execute("DELETE FROM invitations WHERE id = ?", (inv["id"],))
        db.commit()
    finally:
        db.close()
    return user


# ── Helpers ──────────────────────────────────────────────────────────────


def has_admin_privilege(user_id: str) -> bool:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT role, deactivated FROM auth_users WHERE id = ?", (user_id,)
        ).fetchone()
        return row is not None and row["deactivated"] == 0 and row["role"] in ("Organization Admin", "Compliance Manager")
    finally:
        db.close()


def is_org_admin(user_id: str) -> bool:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT role, deactivated FROM auth_users WHERE id = ?", (user_id,)
        ).fetchone()
        return row is not None and row["deactivated"] == 0 and row["role"] == "Organization Admin"
    finally:
        db.close()
