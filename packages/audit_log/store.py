import csv
import hashlib
import io
import json
import sqlite3
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone, timedelta


DB_PATH: str | None = None


def _compute_integrity_hash(entry: dict, prev_hash: str = "", details: dict | None = None) -> str:
    # Canonical details: all keys except the integrity metadata itself, sorted.
    meta = {"_integrity_hash", "_prev_hash", "_outcome"}
    canonical = ""
    if details:
        canonical = json.dumps(
            {k: v for k, v in sorted(details.items()) if k not in meta},
            sort_keys=True,
            default=str,
        )
    raw = "|".join([
        prev_hash,
        entry.get("timestamp", ""),
        entry.get("user_id", ""),
        entry.get("user_email", ""),
        entry.get("action", ""),
        entry.get("resource_type", ""),
        entry.get("resource_id", ""),
        entry.get("framework_id", ""),
        entry.get("outcome", "success"),
        canonical,
    ])
    return hashlib.sha256(raw.encode()).hexdigest()


def _latest_integrity_hash(db) -> str:
    row = db.execute(
        "SELECT details FROM audit_entries ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    if not row:
        return ""
    try:
        details = json.loads(row["details"])
    except (json.JSONDecodeError, TypeError):
        return ""
    return str(details.get("_integrity_hash") or "")


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("AUDIT_LOG_DB_PATH") or DB_PATH or "/tmp/khestra-audit.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS audit_entries (
  id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL,
  user_id TEXT DEFAULT '',
  user_email TEXT DEFAULT '',
  action TEXT NOT NULL DEFAULT '',
  resource_type TEXT NOT NULL DEFAULT '',
  resource_id TEXT DEFAULT '',
  framework_id TEXT DEFAULT '',
  details TEXT DEFAULT '{}',
  ip_address TEXT DEFAULT '',
  user_agent TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_audit_framework ON audit_entries(framework_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_entries(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_entries(resource_type, resource_id);
"""


def _seed_demo_events():
    events = [
        ("created", "policy", "pol001", "SOC2", {"title": "Data Protection Policy", "demo": True}),
        ("updated", "control", "CC6.1", "SOC2", {"field": "status", "old": "gap", "new": "met", "demo": True}),
        ("created", "vendor", "vend001", "AIGov", {"name": "OpenAI", "demo": True}),
        ("created", "system", "sys001", "AIGov", {"name": "LLM Inference Pipeline", "demo": True}),
        ("updated", "risk", "risk001", "CMMC", {"level": "medium", "field": "treatment", "demo": True}),
        ("deleted", "evidence", "evt001", "SOC2", {"filename": "old-screenshot.png", "demo": True}),
    ]
    db = _get_db()
    try:
        base = datetime.now(timezone.utc)
        for i, (action, rtype, rid, fw, details) in enumerate(events):
            eid = uuid4().hex[:12]
            ts = (base - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
            entry = {
                "timestamp": ts,
                "user_id": "",
                "user_email": "demo@khestra.dev",
                "action": action,
                "resource_type": rtype,
                "resource_id": rid,
                "framework_id": fw,
                "outcome": "success",
            }
            details["_integrity_hash"] = _compute_integrity_hash(entry)
            db.execute(
                "INSERT INTO audit_entries (id, timestamp, user_email, action, resource_type, resource_id, framework_id, details) "
                "VALUES (?, ?, 'demo@khestra.dev', ?, ?, ?, ?, ?)",
                (eid, ts, action, rtype, rid, fw, json.dumps(details)),
            )
        db.commit()
    finally:
        db.close()


def verify_chain(limit: int = 100000) -> dict:
    """Walk the audit chain in insertion order and verify every entry's hash.

    Entries predating the chain carry a self-contained hash (no _prev_hash);
    they form the chain's root. Every later entry must hash to its own fields
    plus the previous entry's stored hash. Returns the first invalid entry
    (if any) plus per-entry detail for the tail.
    """
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT rowid, id, timestamp, user_id, user_email, action, resource_type, "
            "resource_id, framework_id, details FROM audit_entries ORDER BY rowid ASC LIMIT ?",
            (limit,),
        ).fetchall()
        checked = 0
        prev_stored = ""
        invalid = []
        for r in rows:
            details = r["details"]
            if isinstance(details, str):
                try:
                    details = json.loads(details)
                except (json.JSONDecodeError, TypeError):
                    details = {}
            stored_hash = str(details.get("_integrity_hash") or "")
            entry_data = {
                "timestamp": r["timestamp"] or "",
                "user_id": r["user_id"] or "",
                "user_email": r["user_email"] or "",
                "action": r["action"] or "",
                "resource_type": r["resource_type"] or "",
                "resource_id": r["resource_id"] or "",
                "framework_id": r["framework_id"] or "",
                "outcome": str(details.get("_outcome") or "success"),
            }
            prev_hash = str(details.get("_prev_hash") or "")
            expected = _compute_integrity_hash(entry_data, prev_hash, details)
            if not stored_hash:
                invalid.append({"rowid": r["rowid"], "id": r["id"], "reason": "missing integrity hash"})
            elif stored_hash != expected:
                invalid.append({"rowid": r["rowid"], "id": r["id"], "reason": "hash mismatch (tampered or chain broken)"})
            elif prev_hash and prev_hash != prev_stored:
                invalid.append({"rowid": r["rowid"], "id": r["id"], "reason": "prev hash does not match preceding entry"})
            checked += 1
            prev_stored = stored_hash
        return {
            "valid": not invalid,
            "checked": checked,
            "first_invalid": invalid[0] if invalid else None,
            "invalid_count": len(invalid),
        }
    finally:
        db.close()


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = os.environ.get("AUDIT_LOG_DB_PATH") or str(Path(data_dir) / "audit_log.db")
    db = _get_db()
    db.executescript(_SCHEMA_SQL)
    count = db.execute("SELECT COUNT(*) as c FROM audit_entries").fetchone()["c"]
    db.close()
    if count == 0:
        _seed_demo_events()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_event(
    action: str,
    resource_type: str,
    resource_id: str = "",
    framework_id: str = "",
    user_id: str = "",
    user_email: str = "",
    details: dict | None = None,
    ip_address: str = "",
    user_agent: str = "",
    outcome: str = "success",
) -> dict:
    db = _get_db()
    try:
        eid = uuid4().hex[:12]
        now = _now()
        details = dict(details or {})
        details["_outcome"] = outcome
        prev_hash = _latest_integrity_hash(db)
        entry_data = {
            "timestamp": now,
            "user_id": user_id,
            "user_email": user_email,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "framework_id": framework_id,
            "outcome": outcome,
        }
        details["_integrity_hash"] = _compute_integrity_hash(entry_data, prev_hash, details)
        if prev_hash:
            details["_prev_hash"] = prev_hash
        entry = {
            "id": eid,
            "timestamp": now,
            "user_id": user_id,
            "user_email": user_email,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "framework_id": framework_id,
            "details": json.dumps(details),
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        db.execute(
            "INSERT INTO audit_entries (id, timestamp, user_id, user_email, action, resource_type, "
            "resource_id, framework_id, details, ip_address, user_agent) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (eid, now, user_id, user_email, action, resource_type, resource_id, framework_id,
             json.dumps(details), ip_address, user_agent),
        )
        db.commit()
        return entry
    finally:
        db.close()


def list_events(
    framework_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict]:
    db = _get_db()
    try:
        conditions = []
        params = []
        if framework_id:
            conditions.append("framework_id = ?")
            params.append(framework_id)
        if resource_type:
            conditions.append("resource_type = ?")
            params.append(resource_type)
        if resource_id:
            conditions.append("resource_id = ?")
            params.append(resource_id)
        where = ""
        if conditions:
            where = "WHERE " + " AND ".join(conditions)
        rows = db.execute(
            f"SELECT * FROM audit_entries {where} ORDER BY rowid DESC LIMIT ? OFFSET ?",
            (*params, limit, offset),
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if isinstance(d.get("details"), str):
                try:
                    d["details"] = json.loads(d["details"])
                except (json.JSONDecodeError, TypeError):
                    d["details"] = {}
            result.append(d)
        return result
    finally:
        db.close()


def export_events_csv(
    framework_id: str | None = None,
    resource_type: str | None = None,
) -> str:
    entries = list_events(
        framework_id=framework_id,
        resource_type=resource_type,
        limit=100000,
        offset=0,
    )
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "timestamp", "user_id", "user_email", "action", "resource_type",
        "resource_id", "framework_id", "outcome", "details", "ip_address", "user_agent",
    ])
    for e in entries:
        dtl = e.get("details", {})
        if isinstance(dtl, str):
            try:
                dtl = json.loads(dtl)
            except (json.JSONDecodeError, TypeError):
                dtl = {}
        outcome = dtl.pop("_outcome", "success")
        writer.writerow([
            e.get("timestamp", ""),
            e.get("user_id", ""),
            e.get("user_email", ""),
            e.get("action", ""),
            e.get("resource_type", ""),
            e.get("resource_id", ""),
            e.get("framework_id", ""),
            outcome,
            json.dumps(dtl),
            e.get("ip_address", ""),
            e.get("user_agent", ""),
        ])
    return buf.getvalue()
