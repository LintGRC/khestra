import json
import sqlite3
import os
from pathlib import Path
from threading import Lock
from uuid import uuid4
from datetime import datetime, timezone, timedelta


DB_PATH: str | None = None
_write_lock = Lock()
REGULATORY_DEADLINES = {"critical": 2, "high": 10, "medium": 15, "low": 15}

FAILURE_MODES = [
    "prompt_injection", "model_poisoning", "model_drift",
    "data_exfiltration", "systemic_bias", "security_breach",
    "agent_failure", "other",
]

STATUSES = ["triage", "investigation", "containment", "root_cause_analysis", "remediation", "closed"]

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".png", ".jpg", ".jpeg", ".txt", ".md", ".json", ".log"}
MAX_EVIDENCE_MB = 50


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("INCIDENTS_DB_PATH") or DB_PATH or "/tmp/khestra-incidents.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS incidents (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  failure_mode TEXT DEFAULT '',
  severity TEXT DEFAULT 'medium',
  status TEXT DEFAULT 'triage',
  model_id TEXT DEFAULT '',
  model_name TEXT DEFAULT '',
  system_id TEXT DEFAULT '',
  reporter_name TEXT DEFAULT '',
  source TEXT DEFAULT '',
  external_id TEXT DEFAULT '',
  control_id TEXT DEFAULT '',
  impact TEXT DEFAULT '{}',
  timeline TEXT DEFAULT '{}',
  regulatory_clock TEXT DEFAULT '{}',
  telemetry TEXT DEFAULT '{}',
  rca TEXT DEFAULT '{}',
  evidence TEXT DEFAULT '[]',
  corrective_actions TEXT DEFAULT '[]',
  regulatory_reports TEXT DEFAULT '[]',
  history TEXT DEFAULT '[]',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    try:
        db.execute("ALTER TABLE incidents ADD COLUMN control_id TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = os.environ.get("INCIDENTS_DB_PATH") or str(Path(data_dir) / "incidents.db")
    _get_db().close()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _id() -> str:
    return uuid4().hex[:12]


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("impact", "timeline", "regulatory_clock", "telemetry", "rca", "evidence", "corrective_actions", "regulatory_reports", "history"):
        if isinstance(d.get(col), str):
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                d[col] = {} if col in ("impact", "timeline", "regulatory_clock", "telemetry", "rca") else []
    return d


def _compute_regulatory_clock(severity: str) -> dict:
    days = REGULATORY_DEADLINES.get(severity, 15)
    types = {2: "widespread", 10: "serious_harm", 15: "standard"}
    labels = {2: "2-Day Clock (Widespread Infringement)", 10: "10-Day Clock (Serious Harm)", 15: "15-Day Clock (Standard Incident)"}
    return {
        "type": types.get(days, "standard"),
        "days": days,
        "label": labels.get(days, "15-Day Clock (Standard Incident)"),
        "deadline": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(),
        "notified": False,
        "notified_at": None,
    }


def _initial_timeline(now: str) -> dict:
    return {
        "reported_at": now,
        "triaged_at": None,
        "investigation_at": None,
        "contained_at": None,
        "rca_at": None,
        "remediation_at": None,
        "closed_at": None,
    }


def list_incidents(
    status: str | None = None,
    severity: str | None = None,
    failure_mode: str | None = None,
    control_id: str | None = None,
    q: str | None = None,
    limit: int = 100,
    offset: int = 0,
    overdue: bool = False,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[dict], int]:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if status:
            conditions.append("status = ?")
            params.append(status)
        if severity:
            conditions.append("severity = ?")
            params.append(severity)
        if failure_mode:
            conditions.append("failure_mode = ?")
            params.append(failure_mode)
        if control_id:
            conditions.append("control_id = ?")
            params.append(control_id)
        if q:
            conditions.append("(title LIKE ? OR description LIKE ? OR reporter_name LIKE ? OR model_name LIKE ?)")
            like = f"%{q}%"
            params.extend([like, like, like, like])
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        total = db.execute(f"SELECT COUNT(*) as c FROM incidents{where}", params).fetchone()["c"]
        all_rows = db.execute(f"SELECT * FROM incidents{where}", params).fetchall()
        items = [_row_to_dict(r) for r in all_rows]
        if overdue:
            now = _now()
            items = [i for i in items if i.get("regulatory_clock", {}).get("deadline", "") and not i["regulatory_clock"].get("notified") and i["regulatory_clock"]["deadline"] < now]
        allowed_sort = {"created_at", "updated_at", "severity", "status", "title", "failure_mode"}
        if sort_by not in allowed_sort:
            sort_by = "created_at"
        reverse = sort_order.lower() != "asc"
        sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        if sort_by == "severity":
            items.sort(key=lambda i: sev_order.get(i.get("severity", "low"), 99), reverse=reverse)
        else:
            items.sort(key=lambda i: str(i.get(sort_by, "") or "").lower(), reverse=reverse)
        return items[offset:offset + limit], len(items)
    finally:
        db.close()


def get_incident(iid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM incidents WHERE id = ?", (iid,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def create_incident(
    title: str,
    description: str = "",
    failure_mode: str = "",
    severity: str = "medium",
    model_id: str = "",
    model_name: str = "",
    system_id: str = "",
    reporter_name: str = "",
    impact_description: str = "",
    affected_inference_pct: float = 0,
    total_users_exposed: int = 0,
    downstream_applications: str = "",
    source: str = "",
    external_id: str = "",
    control_id: str = "",
) -> dict:
    iid = _id()
    now = _now()
    impact = {
        "description": impact_description,
        "affected_inference_pct": affected_inference_pct,
        "total_users_exposed": total_users_exposed,
        "downstream_applications": [s.strip() for s in downstream_applications.split(",") if s.strip()],
    }
    db = _get_db()
    try:
        db.execute(
            """INSERT INTO incidents
(id, title, description, failure_mode, severity, status, model_id, model_name, system_id, reporter_name, source, external_id, control_id,
 impact, timeline, regulatory_clock, evidence, corrective_actions, regulatory_reports, rca, telemetry, history, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, 'triage', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '[]', '[]', '[]', '{}', '{}', ?, ?, ?)""",
            (
                iid, title, description, failure_mode, severity,
                model_id, model_name, system_id, reporter_name, source, external_id, control_id,
                json.dumps(impact),
                json.dumps(_initial_timeline(now)),
                json.dumps(_compute_regulatory_clock(severity)),
                json.dumps([{"timestamp": now, "action": "reported", "detail": f"Incident reported by {reporter_name or 'unknown'}"}]),
                now, now,
            ),
        )
        db.commit()
    finally:
        db.close()
    return get_incident(iid) or {}


def update_incident(iid: str, data: dict) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT id FROM incidents WHERE id = ?", (iid,)).fetchone()
        if not row:
            return None
        now = _now()
        allowed = {"title", "description", "failure_mode", "severity", "status", "model_id", "model_name", "system_id", "reporter_name", "control_id"}
        updates: list[str] = []
        params: list[str] = []
        for k, v in data.items():
            if k in allowed and v is not None:
                updates.append(f"{k} = ?")
                params.append(v)
        if "severity" in data and data["severity"]:
            updates.append("regulatory_clock = ?")
            params.append(json.dumps(_compute_regulatory_clock(data["severity"])))
        if data.get("impact_description") is not None or data.get("affected_inference_pct") is not None or data.get("total_users_exposed") is not None or data.get("downstream_applications") is not None:
            current = get_incident(iid)
            imp = (current or {}).get("impact", {})
            if data.get("impact_description") is not None:
                imp["description"] = data["impact_description"]
            if data.get("affected_inference_pct") is not None:
                imp["affected_inference_pct"] = data["affected_inference_pct"]
            if data.get("total_users_exposed") is not None:
                imp["total_users_exposed"] = data["total_users_exposed"]
            if data.get("downstream_applications") is not None:
                imp["downstream_applications"] = [s.strip() for s in data["downstream_applications"].split(",") if s.strip()]
            updates.append("impact = ?")
            params.append(json.dumps(imp))
        updates.append("updated_at = ?")
        params.append(now)
        params.append(iid)
        db.execute(f"UPDATE incidents SET {', '.join(updates)} WHERE id = ?", params)
        db.commit()
    finally:
        db.close()
    return get_incident(iid)


def transition_incident(iid: str, new_status: str, detail: str = "", rca_data: dict | None = None) -> dict | None:
    if new_status not in STATUSES:
        return None
    db = _get_db()
    try:
        row = db.execute("SELECT id, status, timeline, history FROM incidents WHERE id = ?", (iid,)).fetchone()
        if not row:
            return None
        now = _now()
        timeline = json.loads(row["timeline"]) if isinstance(row["timeline"], str) else row["timeline"]
        timeline_key = f"{new_status}_at"
        timeline[timeline_key] = now
        history = json.loads(row["history"]) if isinstance(row["history"], str) else row["history"]
        history.append({"timestamp": now, "action": new_status, "detail": detail or f"Status changed to {new_status}"})
        db.execute(
            "UPDATE incidents SET status = ?, timeline = ?, history = ?, updated_at = ? WHERE id = ?",
            (new_status, json.dumps(timeline), json.dumps(history), now, iid),
        )
        if rca_data and new_status == "root_cause_analysis":
            rca = {
                "root_cause": rca_data.get("root_cause", ""),
                "contributing_factors": rca_data.get("contributing_factors", []),
                "lessons_learned": rca_data.get("lessons_learned", ""),
                "blast_radius": rca_data.get("blast_radius", ""),
            }
            db.execute("UPDATE incidents SET rca = ?, updated_at = ? WHERE id = ?", (json.dumps(rca), now, iid))
        db.commit()
    finally:
        db.close()
    return get_incident(iid)


def delete_incident(iid: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM incidents WHERE id = ?", (iid,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


def bulk_incident_ops(ids: list[str], action: str, value: str = "") -> list[dict]:
    results = []
    for iid in ids:
        if action == "delete":
            if delete_incident(iid):
                results.append({"id": iid, "deleted": True})
        else:
            inc = get_incident(iid)
            if not inc:
                continue
            now = _now()
            if action == "close":
                inc = transition_incident(iid, "closed", detail="Bulk close")
            elif action == "reopen":
                inc = transition_incident(iid, "triage", detail="Bulk reopen")
            elif action == "severity" and value:
                inc = update_incident(iid, {"severity": value})
            if inc:
                results.append(inc)
    return results


def notify_regulator(iid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT id, regulatory_clock, history FROM incidents WHERE id = ?", (iid,)).fetchone()
        if not row:
            return None
        now = _now()
        clock = json.loads(row["regulatory_clock"]) if isinstance(row["regulatory_clock"], str) else row["regulatory_clock"]
        clock["notified"] = True
        clock["notified_at"] = now
        history = json.loads(row["history"]) if isinstance(row["history"], str) else row["history"]
        history.append({"timestamp": now, "action": "regulator_notified", "detail": "Regulatory authority notified"})
        db.execute(
            "UPDATE incidents SET regulatory_clock = ?, history = ?, updated_at = ? WHERE id = ?",
            (json.dumps(clock), json.dumps(history), now, iid),
        )
        db.commit()
    finally:
        db.close()
    return get_incident(iid)


def add_evidence(iid: str, filename: str, file_data: bytes, label: str = "") -> dict | None:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    if len(file_data) > MAX_EVIDENCE_MB * 1024 * 1024:
        raise ValueError(f"File exceeds {MAX_EVIDENCE_MB}MB limit")
    db = _get_db()
    files_dir = Path(os.environ.get("EVIDENCE_FILES_DIR") or "/tmp/khestra-evidence-files")
    files_dir.mkdir(parents=True, exist_ok=True)
    eid = uuid4().hex[:8]
    stored_name = f"{eid}{ext}"
    (files_dir / stored_name).write_bytes(file_data)
    try:
        row = db.execute("SELECT evidence FROM incidents WHERE id = ?", (iid,)).fetchone()
        if not row:
            return None
        ev_list = json.loads(row["evidence"]) if isinstance(row["evidence"], str) else row["evidence"]
        entry = {"id": eid, "filename": filename, "label": label or filename, "size": len(file_data), "uploaded_at": _now()}
        ev_list.append(entry)
        db.execute("UPDATE incidents SET evidence = ?, updated_at = ? WHERE id = ?", (json.dumps(ev_list), _now(), iid))
        db.commit()
    finally:
        db.close()
    return entry


def get_evidence_file(iid: str, eid: str) -> tuple[dict, bytes | None] | None:
    inc = get_incident(iid)
    if not inc:
        return None
    for ev in inc.get("evidence", []):
        if ev["id"] == eid:
            ext = os.path.splitext(ev["filename"])[1].lower()
            path = Path(os.environ.get("EVIDENCE_FILES_DIR") or "/tmp/khestra-evidence-files") / f"{eid}{ext}"
            data = path.read_bytes() if path.exists() else None
            return ev, data
    return None


def delete_evidence(iid: str, eid: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT evidence FROM incidents WHERE id = ?", (iid,)).fetchone()
        if not row:
            return False
        ev_list = json.loads(row["evidence"]) if isinstance(row["evidence"], str) else row["evidence"]
        new_list = [e for e in ev_list if e["id"] != eid]
        if len(new_list) == len(ev_list):
            return False
        db.execute("UPDATE incidents SET evidence = ?, updated_at = ? WHERE id = ?", (json.dumps(new_list), _now(), iid))
        db.commit()
        for ev in ev_list:
            if ev["id"] == eid:
                ext = os.path.splitext(ev["filename"])[1].lower()
                path = Path(os.environ.get("EVIDENCE_FILES_DIR") or "/tmp/khestra-evidence-files") / f"{eid}{ext}"
                if path.exists():
                    path.unlink()
                break
    finally:
        db.close()
    return True


def add_corrective_action(iid: str, description: str, assigned_to: str = "", due_date: str = "") -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT corrective_actions FROM incidents WHERE id = ?", (iid,)).fetchone()
        if not row:
            return None
        actions = json.loads(row["corrective_actions"]) if isinstance(row["corrective_actions"], str) else row["corrective_actions"]
        action = {"id": uuid4().hex[:8], "description": description, "assigned_to": assigned_to, "due_date": due_date, "status": "pending", "completed_at": None}
        actions.append(action)
        db.execute("UPDATE incidents SET corrective_actions = ?, updated_at = ? WHERE id = ?", (json.dumps(actions), _now(), iid))
        db.commit()
    finally:
        db.close()
    return action


def update_corrective_action(iid: str, caid: str, data: dict) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT corrective_actions FROM incidents WHERE id = ?", (iid,)).fetchone()
        if not row:
            return None
        actions = json.loads(row["corrective_actions"]) if isinstance(row["corrective_actions"], str) else row["corrective_actions"]
        for action in actions:
            if action["id"] == caid:
                if "status" in data:
                    action["status"] = data["status"]
                    if data["status"] == "completed":
                        action["completed_at"] = _now()
                if "description" in data:
                    action["description"] = data["description"]
                if "assigned_to" in data:
                    action["assigned_to"] = data["assigned_to"]
                if "due_date" in data:
                    action["due_date"] = data["due_date"]
                db.execute("UPDATE incidents SET corrective_actions = ?, updated_at = ? WHERE id = ?", (json.dumps(actions), _now(), iid))
                db.commit()
                return action
    finally:
        db.close()
    return None


def save_telemetry(iid: str, telemetry: dict) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT id, history FROM incidents WHERE id = ?", (iid,)).fetchone()
        if not row:
            return None
        now = _now()
        snapshot = {
            "prompt": telemetry.get("prompt", ""),
            "response": telemetry.get("response", ""),
            "model_parameters": telemetry.get("model_parameters", {}),
            "anonymized_logs": telemetry.get("anonymized_logs", ""),
            "snapshot_taken_at": now,
        }
        history = json.loads(row["history"]) if isinstance(row["history"], str) else row["history"]
        history.append({"timestamp": now, "action": "telemetry_snapshot", "detail": "Runtime telemetry captured"})
        db.execute("UPDATE incidents SET telemetry = ?, history = ?, updated_at = ? WHERE id = ?", (json.dumps(snapshot), json.dumps(history), now, iid))
        db.commit()
    finally:
        db.close()
    return get_incident(iid)


def create_regulatory_report(iid: str, report_type: str, submitted_to: str = "", content: str = "") -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT regulatory_reports FROM incidents WHERE id = ?", (iid,)).fetchone()
        if not row:
            return None
        reports = json.loads(row["regulatory_reports"]) if isinstance(row["regulatory_reports"], str) else row["regulatory_reports"]
        report = {"id": uuid4().hex[:8], "report_type": report_type, "submitted_to": submitted_to, "content": content, "created_at": _now(), "submitted_at": None}
        reports.append(report)
        db.execute("UPDATE incidents SET regulatory_reports = ?, updated_at = ? WHERE id = ?", (json.dumps(reports), _now(), iid))
        db.commit()
    finally:
        db.close()
    return report


def get_stats() -> dict:
    db = _get_db()
    try:
        total = db.execute("SELECT COUNT(*) as c FROM incidents").fetchone()["c"]
        by_status = {r["status"]: r["c"] for r in db.execute("SELECT status, COUNT(*) as c FROM incidents GROUP BY status").fetchall()}
        by_severity = {r["severity"]: r["c"] for r in db.execute("SELECT severity, COUNT(*) as c FROM incidents GROUP BY severity").fetchall()}
        by_failure_mode = {r["failure_mode"]: r["c"] for r in db.execute("SELECT failure_mode, COUNT(*) as c FROM incidents GROUP BY failure_mode").fetchall()}
        all_incidents = [dict(r) for r in db.execute("SELECT id, regulatory_clock, status FROM incidents").fetchall()]
        now = _now()
        open_count = sum(1 for r in all_incidents if r.get("status") not in ("closed",))
        overdue = 0
        for r in all_incidents:
            clock = json.loads(r["regulatory_clock"]) if isinstance(r["regulatory_clock"], str) else r["regulatory_clock"]
            if clock.get("deadline") and not clock.get("notified") and clock["deadline"] < now:
                overdue += 1
        return {
            "total": total,
            "open": open_count,
            "overdue_regulatory": overdue,
            "by_status": by_status,
            "by_severity": by_severity,
            "by_failure_mode": by_failure_mode,
        }
    finally:
        db.close()


def auto_classify(iid: str) -> dict | None:
    inc = get_incident(iid)
    if not inc:
        return None
    imp = inc.get("impact", {})
    pct = imp.get("affected_inference_pct", 0)
    users = imp.get("total_users_exposed", 0)
    fm = inc.get("failure_mode", "")
    if fm in ("security_breach", "model_poisoning") or pct > 50 or users > 10000:
        new_sev = "critical"
    elif fm in ("data_exfiltration", "agent_failure") or pct > 20 or users > 1000:
        new_sev = "high"
    elif fm in ("model_drift", "systemic_bias") or pct > 5 or users > 100:
        new_sev = "medium"
    else:
        new_sev = "low"
    return update_incident(iid, {"severity": new_sev})


def migrate_from_json(json_path: str):
    path = Path(json_path)
    if not path.exists():
        return
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return
    if not isinstance(data, dict):
        return
    for iid, record in data.items():
        if not isinstance(record, dict):
            continue
        db = _get_db()
        try:
            existing = db.execute("SELECT id FROM incidents WHERE id = ?", (iid,)).fetchone()
            if existing:
                continue
            title = record.get("title", "")
            description = record.get("description", "")
            failure_mode = record.get("failure_mode", "")
            severity = record.get("severity", "medium")
            status = record.get("status", "triage")
            model_id = record.get("model_id", "")
            model_name = record.get("model_name", "")
            system_id = record.get("system_id", "")
            reporter_name = record.get("reporter_name", "")
            source = record.get("source", "")
            external_id = record.get("external_id", "")
            impact = record.get("impact", {})
            if isinstance(impact, str):
                try:
                    impact = json.loads(impact)
                except (json.JSONDecodeError, TypeError):
                    impact = {}
            if not isinstance(impact, dict):
                impact = {"description": str(impact)} if impact else {}
            description_impact = record.get("impact_description", "")
            if description_impact and not impact.get("description"):
                impact["description"] = description_impact
            if record.get("affected_inference_pct") is not None:
                impact.setdefault("affected_inference_pct", record["affected_inference_pct"])
            if record.get("total_users_exposed") is not None:
                impact.setdefault("total_users_exposed", record["total_users_exposed"])
            timeline = record.get("timeline", {})
            if isinstance(timeline, str):
                try:
                    timeline = json.loads(timeline)
                except (json.JSONDecodeError, TypeError):
                    timeline = {}
            regulatory_clock = record.get("regulatory_clock", {})
            if isinstance(regulatory_clock, str):
                try:
                    regulatory_clock = json.loads(regulatory_clock)
                except (json.JSONDecodeError, TypeError):
                    regulatory_clock = {}
            evidence = record.get("evidence", [])
            if isinstance(evidence, str):
                try:
                    evidence = json.loads(evidence)
                except (json.JSONDecodeError, TypeError):
                    evidence = []
            corrective_actions = record.get("corrective_actions", [])
            if isinstance(corrective_actions, str):
                try:
                    corrective_actions = json.loads(corrective_actions)
                except (json.JSONDecodeError, TypeError):
                    corrective_actions = []
            regulatory_reports = record.get("regulatory_reports", [])
            if isinstance(regulatory_reports, str):
                try:
                    regulatory_reports = json.loads(regulatory_reports)
                except (json.JSONDecodeError, TypeError):
                    regulatory_reports = []
            rca = record.get("rca", {})
            if isinstance(rca, str):
                try:
                    rca = json.loads(rca)
                except (json.JSONDecodeError, TypeError):
                    rca = {}
            telemetry = record.get("telemetry", {})
            if isinstance(telemetry, str):
                try:
                    telemetry = json.loads(telemetry)
                except (json.JSONDecodeError, TypeError):
                    telemetry = {}
            history = record.get("history", [])
            if isinstance(history, str):
                try:
                    history = json.loads(history)
                except (json.JSONDecodeError, TypeError):
                    history = []
            created_at = record.get("created_at", _now())
            updated_at = record.get("updated_at", created_at)
            control_id = record.get("control_id", "")
            db.execute(
                """INSERT OR IGNORE INTO incidents
(id, title, description, failure_mode, severity, status, model_id, model_name, system_id, reporter_name, source, external_id, control_id,
 impact, timeline, regulatory_clock, evidence, corrective_actions, regulatory_reports, rca, telemetry, history, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    iid, title, description, failure_mode, severity, status,
                    model_id, model_name, system_id, reporter_name, source, external_id, control_id,
                    json.dumps(impact), json.dumps(timeline), json.dumps(regulatory_clock),
                    json.dumps(evidence), json.dumps(corrective_actions), json.dumps(regulatory_reports),
                    json.dumps(rca), json.dumps(telemetry), json.dumps(history),
                    created_at, updated_at,
                ),
            )
            db.commit()
        finally:
            db.close()


def seed_incidents() -> list[dict]:
    samples = [
        {
            "title": "Prompt Injection / Jailbreaking Detected",
            "description": "User bypassed model guardrails using a crafted prompt, exposing internal system instructions.",
            "failure_mode": "prompt_injection",
            "severity": "high",
            "reporter_name": "Alice",
            "impact_description": "Potential unauthorized access to system prompts and training data boundaries.",
            "affected_inference_pct": 5.0,
            "total_users_exposed": 150,
            "downstream_applications": "chat-api, response-generator",
        },
        {
            "title": "Severe Model Hallucination / Drift",
            "description": "Model producing factually incorrect outputs with high confidence across multiple queries.",
            "failure_mode": "model_drift",
            "severity": "medium",
            "reporter_name": "Bob",
            "impact_description": "Misinformation risk for end users relying on model outputs for decision-making.",
            "affected_inference_pct": 12.0,
            "total_users_exposed": 500,
            "downstream_applications": "customer-support-bot",
        },
        {
            "title": "Systemic Bias / Discriminatory Output",
            "description": "Model consistently producing biased outputs against a protected demographic group.",
            "failure_mode": "systemic_bias",
            "severity": "medium",
            "reporter_name": "Carol",
            "impact_description": "Fairness and discrimination risk requiring ethics committee review.",
            "affected_inference_pct": 3.0,
            "total_users_exposed": 2000,
            "downstream_applications": "hr-screening-tool, resume-parser",
        },
    ]
    results = []
    db = _get_db()
    try:
        existing = db.execute("SELECT COUNT(*) as c FROM incidents").fetchone()["c"]
        if existing > 0:
            return []
        for s in samples:
            inc = create_incident(**s)
            if inc:
                results.append(inc)
    finally:
        db.close()
    return results
