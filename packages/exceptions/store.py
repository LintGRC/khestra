import csv
import io
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Optional

from .models import (
    ExceptionItem, ExceptionComment, Attachment, ExceptionHistoryEntry,
    utcnow, build_enriched,
)
from .framework_registry import get as get_framework_config


DB_PATH: str | None = None
UPLOADS_DIR: str | None = None


_COLUMNS = [
    "id",
    "title",
    "description",
    "org_id",
    "workspace_id",
    "framework",
    "control_id",
    "control_reference",
    "status",
    "risk_level",
    "likelihood",
    "impact",
    "compensating_controls",
    "risk_acceptance",
    "owner",
    "created_by",
    "approved_by",
    "expiry_date",
    "expiry_days",
    "approval_notes",
    "notes",
    "model_id",
    "risk_assessment",
    "extension_log",
    "relationships",
    "comments",
    "attachments",
    "history",
    "milestones",
    "created_at",
    "updated_at",
]

_JSON_COLS = frozenset({
    "risk_assessment",
    "extension_log",
    "relationships",
    "comments",
    "attachments",
    "history",
    "milestones",
})

_JSON_DEFAULTS: dict[str, dict | list] = {
    "risk_assessment": {},
    "extension_log": [],
    "relationships": {},
    "comments": [],
    "attachments": [],
    "history": [],
    "milestones": [],
}

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS exceptions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  org_id TEXT DEFAULT '',
  workspace_id TEXT DEFAULT '',
  framework TEXT DEFAULT '',
  control_id TEXT DEFAULT '',
  control_reference TEXT DEFAULT '',
  status TEXT DEFAULT 'open',
  risk_level TEXT DEFAULT 'medium',
  likelihood INTEGER DEFAULT 0,
  impact INTEGER DEFAULT 0,
  compensating_controls TEXT DEFAULT '',
  risk_acceptance TEXT DEFAULT '',
  owner TEXT DEFAULT '',
  created_by TEXT DEFAULT '',
  approved_by TEXT DEFAULT '',
  expiry_date TEXT DEFAULT '',
  expiry_days INTEGER DEFAULT 0,
  approval_notes TEXT DEFAULT '',
  notes TEXT DEFAULT '',
  model_id TEXT DEFAULT '',
  risk_assessment TEXT DEFAULT '{}',
  extension_log TEXT DEFAULT '[]',
  relationships TEXT DEFAULT '{}',
  comments TEXT DEFAULT '[]',
  attachments TEXT DEFAULT '[]',
  history TEXT DEFAULT '[]',
  milestones TEXT DEFAULT '[]',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);
"""


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = DB_PATH or "/tmp/khestra-exceptions.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)


def _dict_to_row(exc: dict) -> list:
    vals = []
    for col in _COLUMNS:
        v = exc.get(col, _JSON_DEFAULTS.get(col, ""))
        if col in _JSON_COLS and isinstance(v, (dict, list)):
            v = json.dumps(v, default=str)
        vals.append(v)
    return vals


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in _JSON_COLS:
        if isinstance(d.get(col), str):
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                d[col] = _JSON_DEFAULTS[col]
    return d


def _read_exc(db: sqlite3.Connection, eid: str) -> dict | None:
    row = db.execute("SELECT * FROM exceptions WHERE id = ?", (eid,)).fetchone()
    return _row_to_dict(row) if row else None


def _write_exc(db: sqlite3.Connection, exc: dict):
    set_clause = ", ".join(f"{c} = ?" for c in _COLUMNS[1:])
    db.execute(
        f"UPDATE exceptions SET {set_clause} WHERE id = ?",
        _dict_to_row(exc)[1:] + [exc["id"]],
    )


def _insert_exc(db: sqlite3.Connection, exc: dict):
    placeholders = ", ".join(["?"] * len(_COLUMNS))
    cols = ", ".join(_COLUMNS)
    db.execute(f"INSERT INTO exceptions ({cols}) VALUES ({placeholders})", _dict_to_row(exc))


def _id() -> str:
    return uuid4().hex[:12]


def _add_history(exc: dict, action: str, changed_by: str, notes: str):
    now = utcnow()
    entry = ExceptionHistoryEntry(
        id=_id(),
        timestamp=now,
        action=action,
        notes=notes,
    )
    d = entry.to_dict()
    d["detail"] = notes
    d["performed_by"] = changed_by
    exc.setdefault("history", []).append(d)


# ─── Init & Migration ──────────────────────────


def init_store(data_dir: str, uploads_dir: str | None = None):
    global DB_PATH, UPLOADS_DIR
    DB_PATH = str(Path(data_dir) / "exceptions.db")
    UPLOADS_DIR = uploads_dir or os.path.join(data_dir, "exception_uploads")
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    db_path = Path(DB_PATH)
    old_json = Path(data_dir) / "exceptions.json"

    if not db_path.exists() and old_json.exists():
        _migrate_from_json(old_json)
    else:
        db = _get_db()
        db.close()


def _migrate_from_json(json_path: Path):
    raw = json.loads(json_path.read_text())
    if "exceptions" in raw and isinstance(raw.get("exceptions"), dict):
        store = raw["exceptions"]
    else:
        store = raw

    if not store:
        json_path.rename(json_path.with_suffix(json_path.suffix + ".migrated"))
        return

    db = _get_db()
    try:
        for exc in store.values():
            exc.setdefault("milestones", [])
            _insert_exc(db, exc)
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        for exc in store.values():
            exc.setdefault("milestones", [])
            try:
                _insert_exc(db, exc)
            except sqlite3.IntegrityError:
                pass
        db.commit()
    finally:
        db.close()

    json_path.rename(json_path.with_suffix(json_path.suffix + ".migrated"))


# ─── Framework Validation ──────────────────────────


def validate_transition(exc: dict, to_status: str) -> bool:
    framework = exc.get("framework", "default")
    cfg = get_framework_config(framework)
    return cfg.validate_transition(exc.get("status", ""), to_status)


def get_allowed_transitions(exc: dict) -> list[str]:
    framework = exc.get("framework", "default")
    cfg = get_framework_config(framework)
    return cfg.allowed_transitions(exc.get("status", ""))


# ─── Lifecycle Events ─────────────────────────────


def append_extension(eid: str, new_expiry_days: int, reason: str = "",
                     changed_by: str = "") -> dict | None:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
        if not exc:
            return None
        old_days = exc.get("expiry_days", 0)
        old_date = exc.get("expiry_date", "")
        now = utcnow()
        entry = {
            "old_expiry_days": old_days,
            "new_expiry_days": new_expiry_days,
            "old_expiry_date": old_date,
            "reason": reason,
            "changed_by": changed_by or exc.get("owner", ""),
            "timestamp": now,
        }
        exc.setdefault("extension_log", []).append(entry)
        exc["expiry_days"] = max(1, new_expiry_days)
        exc["updated_at"] = now
        _add_history(exc, "extended", changed_by, reason or f"Extended by {new_expiry_days} days")
        _write_exc(db, exc)
        db.commit()
        return exc
    finally:
        db.close()


def update_risk(eid: str, risk_assessment: dict, changed_by: str = "") -> dict | None:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
        if not exc:
            return None
        likelihood = risk_assessment.get("likelihood", exc.get("likelihood", 1))
        impact = risk_assessment.get("impact", exc.get("impact", 1))
        score = risk_assessment.get("score", 0) or (likelihood * impact)
        ra = {
            "method": risk_assessment.get("method", "likelihood_impact"),
            "likelihood": likelihood,
            "impact": impact,
            "score": score,
            "residual": risk_assessment.get("residual", ""),
            "rationale": risk_assessment.get("rationale", ""),
        }
        exc["risk_assessment"] = ra
        exc["likelihood"] = likelihood
        exc["impact"] = impact
        now = utcnow()
        exc["updated_at"] = now
        _add_history(exc, "risk_updated", changed_by, "Risk assessment updated")
        _write_exc(db, exc)
        db.commit()
        return exc
    finally:
        db.close()


# ─── CRUD ──────────────────────────────────────────


def list_exceptions(
    org_id: str | None = None,
    workspace_id: str | None = None,
    framework: str | None = None,
    control_id: str | None = None,
    status: str | None = None,
    owner: str | None = None,
) -> list[dict]:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if org_id:
            conditions.append("org_id = ?")
            params.append(org_id)
        if workspace_id:
            conditions.append("workspace_id = ?")
            params.append(workspace_id)
        if framework:
            conditions.append("framework = ?")
            params.append(framework)
        if control_id:
            conditions.append("control_id = ?")
            params.append(control_id)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if owner:
            conditions.append("owner = ?")
            params.append(owner)
        sql = "SELECT * FROM exceptions"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC"
        rows = db.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def get_exception(eid: str) -> dict | None:
    db = _get_db()
    try:
        return _read_exc(db, eid)
    finally:
        db.close()


def create_exception(
    title: str,
    description: str = "",
    org_id: str = "",
    workspace_id: str = "",
    framework: str = "",
    control_id: str = "",
    control_reference: str = "",
    risk_level: str = "medium",
    likelihood: int = 0,
    impact: int = 0,
    compensating_controls: str = "",
    risk_acceptance: str = "",
    owner: str = "",
    created_by: str = "",
    expiry_date: str = "",
    expiry_days: int = 0,
    notes: str = "",
    model_id: str = "",
) -> dict:
    now = utcnow()
    eid = _id()
    exc = ExceptionItem(
        id=eid,
        title=title,
        description=description,
        org_id=org_id,
        workspace_id=workspace_id,
        framework=framework,
        control_id=control_id,
        control_reference=control_reference,
        status="open",
        risk_level=risk_level,
        likelihood=likelihood,
        impact=impact,
        compensating_controls=compensating_controls,
        risk_acceptance=risk_acceptance,
        owner=owner,
        created_by=created_by or owner,
        expiry_date=expiry_date,
        expiry_days=expiry_days,
        notes=notes,
        model_id=model_id,
        created_at=now,
        updated_at=now,
    ).to_dict()
    _add_history(exc, "created", created_by or owner, "Exception created")

    db = _get_db()
    try:
        _insert_exc(db, exc)
        db.commit()
    finally:
        db.close()
    return exc


def update_exception(
    eid: str,
    *,
    title: str | None = None,
    description: str | None = None,
    framework: str | None = None,
    control_id: str | None = None,
    control_reference: str | None = None,
    status: str | None = None,
    risk_level: str | None = None,
    likelihood: int | None = None,
    impact: int | None = None,
    compensating_controls: str | None = None,
    risk_acceptance: str | None = None,
    owner: str | None = None,
    approved_by: str | None = None,
    expiry_date: str | None = None,
    expiry_days: int | None = None,
    model_id: str | None = None,
    notes: str | None = None,
    risk_assessment: dict | None = None,
    relationships: dict | None = None,
    changed_by: str = "",
) -> dict | None:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
        if not exc:
            return None

        changes = []
        if title is not None:
            exc["title"] = title
        if description is not None:
            exc["description"] = description
        if framework is not None:
            exc["framework"] = framework
        if control_id is not None:
            exc["control_id"] = control_id
        if control_reference is not None:
            exc["control_reference"] = control_reference
        if status is not None:
            old_status = exc.get("status", "")
            exc["status"] = status
            changes.append(f"status: {old_status} -> {status}")
            if status == "approved":
                exc["approved_by"] = approved_by or changed_by
        if risk_level is not None:
            exc["risk_level"] = risk_level
        if likelihood is not None:
            exc["likelihood"] = likelihood
        if impact is not None:
            exc["impact"] = impact
        if compensating_controls is not None:
            exc["compensating_controls"] = compensating_controls
        if risk_acceptance is not None:
            exc["risk_acceptance"] = risk_acceptance
        if owner is not None:
            exc["owner"] = owner
        if approved_by is not None:
            exc["approved_by"] = approved_by
        if expiry_date is not None:
            exc["expiry_date"] = expiry_date
        if expiry_days is not None:
            exc["expiry_days"] = expiry_days
        if model_id is not None:
            exc["model_id"] = model_id
        if notes is not None:
            exc["notes"] = notes
        if risk_assessment is not None:
            likelihood_val = risk_assessment.get("likelihood", exc.get("likelihood", 1))
            impact_val = risk_assessment.get("impact", exc.get("impact", 1))
            score = risk_assessment.get("score", 0) or (likelihood_val * impact_val)
            ra = {
                "method": risk_assessment.get("method", "likelihood_impact"),
                "likelihood": likelihood_val,
                "impact": impact_val,
                "score": score,
                "residual": risk_assessment.get("residual", ""),
                "rationale": risk_assessment.get("rationale", ""),
            }
            exc["risk_assessment"] = ra
            exc["likelihood"] = likelihood_val
            exc["impact"] = impact_val
        if relationships is not None:
            existing = exc.get("relationships") or {}
            for k, v in relationships.items():
                if isinstance(v, list):
                    existing[k] = list(set(existing.get(k, []) + v))
                else:
                    existing[k] = v
            exc["relationships"] = existing

        exc["updated_at"] = utcnow()
        notes_str = ", ".join(changes) if changes else "Updated"
        _add_history(exc, "updated", changed_by or exc.get("owner", ""), notes_str)

        _write_exc(db, exc)
        db.commit()
        return exc
    finally:
        db.close()


def delete_exception(eid: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM exceptions WHERE id = ?", (eid,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


# ─── Comments ──────────────────────────────────────


def add_comment(eid: str, author: str, body: str) -> dict | None:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
        if not exc:
            return None
        comment = ExceptionComment(
            id=_id(),
            author=author,
            body=body,
            created_at=utcnow(),
        )
        exc.setdefault("comments", []).append(comment.to_dict())
        _add_history(exc, "comment_added", author, body[:80])
        _write_exc(db, exc)
        db.commit()
        return comment.to_dict()
    finally:
        db.close()


# ─── Extend / Review (AI Gov lifecycle) ──────────


def extend_exception(eid: str, expiry_days: int, approval_notes: str = "", changed_by: str = "") -> dict | None:
    return append_extension(eid, expiry_days, reason=approval_notes, changed_by=changed_by)


def review_exception(eid: str, outcome: str, notes: str = "", changed_by: str = "") -> dict | None:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
        if not exc:
            return None
        if outcome == "close":
            exc["status"] = "closed"
        elif outcome == "extend":
            exc["status"] = "open"
        elif outcome == "escalate":
            exc["status"] = "open"
        elif outcome == "reject":
            exc["status"] = "rejected"
        else:
            exc["status"] = outcome
        if notes:
            exc["approval_notes"] = notes
        exc["updated_at"] = utcnow()
        _add_history(exc, f"review_{outcome}", changed_by, notes)
        _write_exc(db, exc)
        db.commit()
        return exc
    finally:
        db.close()


# ─── Milestones / POA&M ──────────────────────────


def _auto_check_completion(exc: dict):
    milestones = exc.get("milestones", [])
    if not milestones:
        return
    all_completed = all(m.get("status") == "completed" for m in milestones)
    if all_completed and exc.get("status") not in ("closed", "rejected"):
        exc["status"] = "closed"
        _add_history(exc, "auto_closed", "system", "All milestones completed")


def add_milestone(eid: str, description: str, target_date: str = "",
                  owner: str = "", changed_by: str = "") -> dict | None:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
        if not exc:
            return None
        now = utcnow()
        mid = _id()
        milestone = {
            "id": mid,
            "description": description,
            "target_date": target_date,
            "completion_date": "",
            "status": "not_started",
            "owner": owner,
            "evidence": "",
            "created_at": now,
            "updated_at": now,
        }
        exc.setdefault("milestones", []).append(milestone)
        exc["updated_at"] = now
        _add_history(exc, "milestone_added", changed_by, description[:80])
        _write_exc(db, exc)
        db.commit()
        return milestone
    finally:
        db.close()


def update_milestone(eid: str, mid: str, *,
                     description: str | None = None,
                     target_date: str | None = None,
                     status: str | None = None,
                     owner: str | None = None,
                     evidence: str | None = None,
                     completion_date: str | None = None,
                     changed_by: str = "") -> dict | None:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
        if not exc:
            return None
        for m in exc.get("milestones", []):
            if m["id"] == mid:
                if description is not None:
                    m["description"] = description
                if target_date is not None:
                    m["target_date"] = target_date
                if owner is not None:
                    m["owner"] = owner
                if evidence is not None:
                    m["evidence"] = evidence
                if completion_date is not None:
                    m["completion_date"] = completion_date
                if status is not None:
                    old_status = m.get("status", "")
                    m["status"] = status
                    m["updated_at"] = utcnow()
                    if status == "completed" and not m.get("completion_date"):
                        m["completion_date"] = utcnow()[:10]
                exc["updated_at"] = utcnow()
                _add_history(exc, f"milestone_{status or 'updated'}", changed_by, m.get("description", "")[:80])
                _auto_check_completion(exc)
                _write_exc(db, exc)
                db.commit()
                return m
        return None
    finally:
        db.close()


def delete_milestone(eid: str, mid: str, changed_by: str = "") -> bool:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
        if not exc:
            return False
        ms = exc.get("milestones", [])
        for i, m in enumerate(ms):
            if m["id"] == mid:
                ms.pop(i)
                exc["updated_at"] = utcnow()
                _add_history(exc, "milestone_deleted", changed_by, m.get("description", "")[:80])
                _write_exc(db, exc)
                db.commit()
                return True
        return False
    finally:
        db.close()


# ─── Reminders ─────────────────────────────────────


def get_reminders() -> dict:
    db = _get_db()
    try:
        rows = db.execute("SELECT * FROM exceptions").fetchall()
        items = [_row_to_dict(r) for r in rows]
    finally:
        db.close()

    now = datetime.now(timezone.utc)
    expired, urgent, upcoming = [], [], []
    for exc in items:
        if exc.get("status") in ("closed", "rejected"):
            continue
        built = build_enriched(exc)
        if built.get("is_expired"):
            expired.append(built)
        elif built.get("days_left", 999) <= 7:
            urgent.append(built)
        elif built.get("days_left", 999) <= 30:
            upcoming.append(built)
    return {"expired": expired, "urgent": urgent, "upcoming": upcoming}


def get_reminder(eid: str) -> dict | None:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
    finally:
        db.close()
    if not exc:
        return None
    built = build_enriched(exc)
    return {"message": f"Exception '{built['title']}' expires in {built.get('days_left', 0)} days. Risk level: {built['risk_level']}"}


# ─── Attachments ─────────────────────────────────


def upload_attachment(eid: str, filename: str, data: bytes) -> dict | None:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
        if not exc:
            return None
        if len(data) > 10 * 1024 * 1024:
            return None
        fid = _id()
        ext = os.path.splitext(filename or "file")[1]
        stored = f"{fid}{ext}"
        with open(os.path.join(UPLOADS_DIR, stored), "wb") as f:
            f.write(data)
        att = Attachment(id=fid, filename=filename or stored, stored_as=stored, uploaded_at=utcnow())
        exc.setdefault("attachments", []).append(att.to_dict())
        _write_exc(db, exc)
        db.commit()
        return att.to_dict()
    finally:
        db.close()


def get_attachment(eid: str, fid: str) -> tuple[bytes | None, str | None]:
    db = _get_db()
    try:
        exc = _read_exc(db, eid)
    finally:
        db.close()
    if not exc:
        return None, None
    for att in exc.get("attachments", []):
        if att["id"] == fid:
            path = os.path.join(UPLOADS_DIR, att["stored_as"])
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return f.read(), att["filename"]
            return None, None
    return None, None


# ─── CSV Export ───────────────────────────────────


def export_csv() -> str:
    db = _get_db()
    try:
        rows = db.execute("SELECT * FROM exceptions").fetchall()
        items = [build_enriched(_row_to_dict(r)) for r in rows]
    finally:
        db.close()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "title", "framework", "risk_score", "risk_level", "status", "owner", "expires_at", "created_at"])
    for e in items:
        w.writerow([e.get("id"), e.get("title"), e.get("framework"), e.get("risk_score"), e.get("risk_level"), e.get("status"), e.get("owner"), e.get("expires_at"), e.get("created_at")])
    return buf.getvalue()


# ─── Seed ─────────────────────────────────────────


def seed_data() -> int:
    db = _get_db()
    try:
        count = db.execute("SELECT COUNT(*) as c FROM exceptions").fetchone()["c"]
        if count > 0:
            return 0
        now_ts = utcnow()
        samples = [
            {"title": "MFA not supported on legacy payroll server", "description": "Legacy SunOS server does not support SAML/OIDC", "framework": "SOC2", "control_reference": "CC6.1", "likelihood": 3, "impact": 5, "owner": "ops@company.com", "expiry_days": 30, "compensating_controls": "IP allowlisting, SIEM logging, monthly access review", "status": "open"},
            {"title": "No SSO for LMS platform", "description": "Vendor only supports username/password", "framework": "ISO 27001", "control_reference": "A.8.5", "likelihood": 2, "impact": 3, "owner": "it@company.com", "expiry_days": 90, "compensating_controls": "MFA enforced at app level, quarterly access review", "status": "approved"},
        ]
        for s in samples:
            eid = _id()
            record = {
                "id": eid, "title": s["title"], "description": s["description"],
                "framework": s["framework"], "control_reference": s.get("control_reference", ""),
                "likelihood": s["likelihood"], "impact": s["impact"], "owner": s["owner"],
                "expiry_days": s["expiry_days"], "compensating_controls": s["compensating_controls"],
                "status": s.get("status", "open"), "approval_notes": "", "model_id": "",
                "comments": [], "attachments": [], "notes": "",
                "history": [{"timestamp": now_ts, "action": "created", "notes": "Seeded"}],
                "created_at": now_ts, "updated_at": now_ts, "created_by": "", "approved_by": "",
                "org_id": "", "workspace_id": "", "control_id": "", "expiry_date": "",
                "risk_level": "", "risk_acceptance": "",
                "milestones": [],
            }
            _insert_exc(db, record)
        db.commit()
        return len(samples)
    finally:
        db.close()


# ─── Stats ─────────────────────────────────────────


def get_stats(org_id: str | None = None) -> dict:
    items = list_exceptions(org_id=org_id)
    total = len(items)
    by_status: dict[str, int] = {}
    by_risk: dict[str, int] = {}
    for e in items:
        s = e.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        built = build_enriched(e)
        r = built.get("risk_level", "unknown")
        by_risk[r] = by_risk.get(r, 0) + 1

    expired = sum(1 for e in items if build_enriched(e).get("is_expired"))
    expiring_soon = sum(1 for e in items if 0 < build_enriched(e).get("days_left", 999) <= 7)

    return {
        "total": total,
        "open": by_status.get("open", 0) + by_status.get("approved", 0),
        "pending_approval": by_status.get("pending_approval", 0),
        "approved": by_status.get("approved", 0),
        "rejected": by_status.get("rejected", 0),
        "expired": expired,
        "expiring_soon": expiring_soon,
        "closed": by_status.get("closed", 0),
        "by_status": by_status,
        "by_risk": by_risk,
    }
