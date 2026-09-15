import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from .models import (
    FindingItem, CorrectiveAction,
    FINDING_SOURCES, FINDING_SEVERITIES, FINDING_STATUSES, ACTION_STATUSES,
    utcnow,
)


DB_PATH: str | None = None


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS findings (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  remediation TEXT DEFAULT '',
  source TEXT DEFAULT '',
  source_id TEXT DEFAULT '',
  severity TEXT DEFAULT 'medium',
  status TEXT DEFAULT 'open',
  owner TEXT DEFAULT '',
  framework TEXT DEFAULT '',
  control_ids TEXT DEFAULT '[]',
  evidence_ids TEXT DEFAULT '[]',
  tags TEXT DEFAULT '[]',
  created_by TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS actions (
  id TEXT PRIMARY KEY,
  finding_id TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  owner TEXT DEFAULT '',
  target_date TEXT DEFAULT '',
  status TEXT DEFAULT 'open',
  completed_at TEXT DEFAULT '',
  evidence_id TEXT DEFAULT '',
  notes TEXT DEFAULT '',
  created_by TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);
"""

_JSON_COLS = frozenset({"control_ids", "evidence_ids", "tags"})
_FINDING_COLS = [
    "id", "title", "description", "remediation", "source", "source_id",
    "severity", "status", "owner", "framework",
    "control_ids", "evidence_ids", "tags",
    "created_by", "created_at", "updated_at",
]
_ACTION_COLS = [
    "id", "finding_id", "title", "description", "owner",
    "target_date", "status", "completed_at", "evidence_id", "notes",
    "created_by", "created_at", "updated_at",
]


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = DB_PATH or "/tmp/khestra-findings.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    # Migration: remediation column on pre-existing findings tables.
    cols = {r[1] for r in db.execute("PRAGMA table_info(findings)").fetchall()}
    if "remediation" not in cols:
        db.execute("ALTER TABLE findings ADD COLUMN remediation TEXT DEFAULT ''")


def _finding_to_row(f: dict) -> list:
    vals = []
    for col in _FINDING_COLS:
        v = f.get(col, "")
        if col in _JSON_COLS and isinstance(v, list):
            v = json.dumps(v, default=str)
        vals.append(v)
    return vals


def _row_to_finding(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in _JSON_COLS:
        if isinstance(d.get(col), str):
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                d[col] = []
    return d


def _action_to_row(a: dict) -> list:
    return [a.get(col, "") for col in _ACTION_COLS]


def _row_to_action(row: sqlite3.Row) -> dict:
    return dict(row)


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = str(Path(data_dir) / "findings.db")

    old_json = Path(data_dir) / "findings.json"
    db_path = Path(DB_PATH)

    if not db_path.exists() and old_json.exists():
        _migrate_from_json(old_json)
    else:
        db = _get_db()
        db.close()


def _migrate_from_json(json_path: Path):
    raw = json.loads(json_path.read_text())
    findings = raw.get("findings", {})
    actions = raw.get("actions", {})
    db = _get_db()
    try:
        for f in findings.values():
            placeholders = ", ".join(["?"] * len(_FINDING_COLS))
            cols = ", ".join(_FINDING_COLS)
            db.execute(
                f"INSERT INTO findings ({cols}) VALUES ({placeholders})",
                _finding_to_row(f),
            )
        for a in actions.values():
            placeholders = ", ".join(["?"] * len(_ACTION_COLS))
            cols = ", ".join(_ACTION_COLS)
            db.execute(
                f"INSERT INTO actions ({cols}) VALUES ({placeholders})",
                _action_to_row(a),
            )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        for f in findings.values():
            try:
                placeholders = ", ".join(["?"] * len(_FINDING_COLS))
                cols = ", ".join(_FINDING_COLS)
                db.execute(
                    f"INSERT INTO findings ({cols}) VALUES ({placeholders})",
                    _finding_to_row(f),
                )
            except sqlite3.IntegrityError:
                pass
        for a in actions.values():
            try:
                placeholders = ", ".join(["?"] * len(_ACTION_COLS))
                cols = ", ".join(_ACTION_COLS)
                db.execute(
                    f"INSERT INTO actions ({cols}) VALUES ({placeholders})",
                    _action_to_row(a),
                )
            except sqlite3.IntegrityError:
                pass
        db.commit()
    finally:
        db.close()
    json_path.rename(json_path.with_suffix(json_path.suffix + ".migrated"))


# ─── Findings CRUD ─────────────────────────────


def list_findings(
    source: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    framework: str | None = None,
    owner: str | None = None,
    control_id: str | None = None,
) -> list[dict]:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if source:
            conditions.append("source = ?")
            params.append(source)
        if severity:
            conditions.append("severity = ?")
            params.append(severity)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if framework:
            conditions.append("(LOWER(framework) = LOWER(?) OR framework = '' OR framework IS NULL)")
            params.append(framework)
        if owner:
            conditions.append("owner = ?")
            params.append(owner)
        if control_id:
            conditions.append("EXISTS (SELECT 1 FROM json_each(control_ids) WHERE value = ?)")
            params.append(control_id)
        sql = "SELECT * FROM findings"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC"
        return [_row_to_finding(r) for r in db.execute(sql, params).fetchall()]
    finally:
        db.close()


def get_finding(finding_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM findings WHERE id = ?", (finding_id,)).fetchone()
        return _row_to_finding(row) if row else None
    finally:
        db.close()


def _coerce_finding_enum(value: str, allowed: list[str], default: str) -> str:
    if value not in allowed:
        return default
    return value


def create_finding(
    title: str,
    description: str = "",
    remediation: str = "",
    source: str = "",
    source_id: str = "",
    severity: str = "medium",
    status: str = "open",
    owner: str = "",
    framework: str = "",
    control_ids: list[str] | None = None,
    evidence_ids: list[str] | None = None,
    tags: list[str] | None = None,
    created_by: str = "",
) -> dict:
    severity = _coerce_finding_enum(severity, FINDING_SEVERITIES, "medium")
    status = _coerce_finding_enum(status, FINDING_STATUSES, "open")
    source = _coerce_finding_enum(source, FINDING_SOURCES, "")
    now = utcnow()
    finding = FindingItem(
        id=uuid4().hex[:12],
        title=title,
        description=description,
        remediation=remediation,
        source=source,
        source_id=source_id,
        severity=severity,
        status=status,
        owner=owner,
        framework=framework,
        control_ids=control_ids or [],
        evidence_ids=evidence_ids or [],
        tags=tags or [],
        created_by=created_by or owner,
        created_at=now,
        updated_at=now,
    )
    d = finding.to_dict()
    db = _get_db()
    try:
        placeholders = ", ".join(["?"] * len(_FINDING_COLS))
        cols = ", ".join(_FINDING_COLS)
        db.execute(f"INSERT INTO findings ({cols}) VALUES ({placeholders})", _finding_to_row(d))
        db.commit()
    finally:
        db.close()
    return d


def update_finding(
    finding_id: str,
    *,
    title: str | None = None,
    description: str | None = None,
    remediation: str | None = None,
    source: str | None = None,
    source_id: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    owner: str | None = None,
    framework: str | None = None,
    control_ids: list[str] | None = None,
    evidence_ids: list[str] | None = None,
    tags: list[str] | None = None,
    changed_by: str = "",
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM findings WHERE id = ?", (finding_id,)).fetchone()
        if not row:
            return None
        finding = _row_to_finding(row)

        if title is not None:
            finding["title"] = title
        if description is not None:
            finding["description"] = description
        if remediation is not None:
            finding["remediation"] = remediation
        if source is not None:
            finding["source"] = source if source in FINDING_SOURCES else finding.get("source", "")
        if source_id is not None:
            finding["source_id"] = source_id
        if severity is not None:
            finding["severity"] = severity if severity in FINDING_SEVERITIES else finding.get("severity", "medium")
        if status is not None:
            old_status = finding.get("status", "")
            finding["status"] = status if status in FINDING_STATUSES else finding.get("status", "open")
        if owner is not None:
            finding["owner"] = owner
        if framework is not None:
            finding["framework"] = framework
        if control_ids is not None:
            finding["control_ids"] = control_ids
        if evidence_ids is not None:
            finding["evidence_ids"] = evidence_ids
        if tags is not None:
            finding["tags"] = tags

        finding["updated_at"] = utcnow()
        set_clause = ", ".join(f"{c} = ?" for c in _FINDING_COLS[1:])
        db.execute(
            f"UPDATE findings SET {set_clause} WHERE id = ?",
            _finding_to_row(finding)[1:] + [finding["id"]],
        )
        db.commit()
        return finding
    finally:
        db.close()


def delete_finding(finding_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM findings WHERE id = ?", (finding_id,))
        db.execute("DELETE FROM actions WHERE finding_id = ?", (finding_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


# ─── Corrective Actions CRUD ──────────────────


def list_actions(finding_id: str) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT * FROM actions WHERE finding_id = ? ORDER BY created_at DESC",
            (finding_id,),
        ).fetchall()
        return [_row_to_action(r) for r in rows]
    finally:
        db.close()


def get_action(action_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM actions WHERE id = ?", (action_id,)).fetchone()
        return _row_to_action(row) if row else None
    finally:
        db.close()


def create_action(
    finding_id: str,
    title: str,
    description: str = "",
    owner: str = "",
    target_date: str = "",
    status: str = "open",
    evidence_id: str = "",
    notes: str = "",
    created_by: str = "",
) -> dict | None:
    status = _coerce_finding_enum(status, ACTION_STATUSES, "open")
    db = _get_db()
    try:
        exists = db.execute("SELECT 1 FROM findings WHERE id = ?", (finding_id,)).fetchone()
        if not exists:
            return None
        now = utcnow()
        action = CorrectiveAction(
            id=uuid4().hex[:12],
            finding_id=finding_id,
            title=title,
            description=description,
            owner=owner,
            target_date=target_date,
            status=status,
            evidence_id=evidence_id,
            notes=notes,
            created_by=created_by or owner,
            created_at=now,
            updated_at=now,
        )
        d = action.to_dict()
        placeholders = ", ".join(["?"] * len(_ACTION_COLS))
        cols = ", ".join(_ACTION_COLS)
        db.execute(f"INSERT INTO actions ({cols}) VALUES ({placeholders})", _action_to_row(d))
        db.commit()
        return d
    finally:
        db.close()


def update_action(
    action_id: str,
    *,
    title: str | None = None,
    description: str | None = None,
    owner: str | None = None,
    target_date: str | None = None,
    status: str | None = None,
    completed_at: str | None = None,
    evidence_id: str | None = None,
    notes: str | None = None,
    changed_by: str = "",
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM actions WHERE id = ?", (action_id,)).fetchone()
        if not row:
            return None
        action = _row_to_action(row)

        if title is not None:
            action["title"] = title
        if description is not None:
            action["description"] = description
        if owner is not None:
            action["owner"] = owner
        if target_date is not None:
            action["target_date"] = target_date
        if status is not None:
            old_status = action.get("status", "")
            action["status"] = status if status in ACTION_STATUSES else action.get("status", "open")
        if completed_at is not None:
            action["completed_at"] = completed_at
        if evidence_id is not None:
            action["evidence_id"] = evidence_id
        if notes is not None:
            action["notes"] = notes

        action["updated_at"] = utcnow()
        set_clause = ", ".join(f"{c} = ?" for c in _ACTION_COLS[1:])
        db.execute(
            f"UPDATE actions SET {set_clause} WHERE id = ?",
            _action_to_row(action)[1:] + [action["id"]],
        )
        db.commit()
        return action
    finally:
        db.close()


def delete_action(action_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM actions WHERE id = ?", (action_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


# ─── Stats ────────────────────────────────────


def by_severity() -> dict[str, int]:
    db = _get_db()
    try:
        result: dict[str, int] = {}
        for r in db.execute("SELECT severity, COUNT(*) as c FROM findings GROUP BY severity"):
            result[r["severity"]] = r["c"]
        return result
    finally:
        db.close()


def by_status() -> dict[str, int]:
    db = _get_db()
    try:
        result: dict[str, int] = {}
        for r in db.execute("SELECT status, COUNT(*) as c FROM findings GROUP BY status"):
            result[r["status"]] = r["c"]
        return result
    finally:
        db.close()


def by_framework() -> dict[str, int]:
    db = _get_db()
    try:
        result: dict[str, int] = {}
        for r in db.execute("SELECT framework, COUNT(*) as c FROM findings GROUP BY framework"):
            result[r["framework"]] = r["c"]
        return result
    finally:
        db.close()


def by_source() -> dict[str, int]:
    db = _get_db()
    try:
        result: dict[str, int] = {}
        for r in db.execute("SELECT source, COUNT(*) as c FROM findings GROUP BY source"):
            result[r["source"]] = r["c"]
        return result
    finally:
        db.close()
