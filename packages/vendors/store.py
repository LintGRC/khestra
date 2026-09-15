import json
import sqlite3
import os
import io
import csv
from pathlib import Path
from uuid import uuid4
from typing import Optional

from .models import (
    Vendor, VendorCertificate, utcnow,
)


DB_PATH: str | None = None


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("VENDOR_DB_PATH") or DB_PATH or "/tmp/khestra-vendors.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS vendors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL DEFAULT '',
  contact_name TEXT DEFAULT '',
  contact_email TEXT DEFAULT '',
  contact_phone TEXT DEFAULT '',
  website TEXT DEFAULT '',
  product_service TEXT DEFAULT '',
  category TEXT DEFAULT '',
  ai_service_type TEXT DEFAULT '',
  tier TEXT DEFAULT '',
  status TEXT DEFAULT 'pending',
  risk_score INTEGER,
  risk_level TEXT,
  access_token TEXT DEFAULT '',
  tags TEXT DEFAULT '[]',
  org_id TEXT DEFAULT '',
  workspace_id TEXT DEFAULT '',
  frameworks TEXT DEFAULT '[]',
  data_residency TEXT DEFAULT '[]',
  transfer_mechanism TEXT DEFAULT '',
  dpa_in_place INTEGER DEFAULT 0,
  certificates TEXT DEFAULT '[]',
  reminder_count INTEGER DEFAULT 0,
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS vendor_responses (
  id TEXT PRIMARY KEY,
  vendor_id TEXT NOT NULL,
  questionnaire_id TEXT DEFAULT 'default',
  status TEXT DEFAULT 'draft',
  answers TEXT DEFAULT '[]',
  created_at TEXT DEFAULT '',
  submitted_at TEXT
);

CREATE TABLE IF NOT EXISTS vendor_assessments (
  id TEXT PRIMARY KEY,
  vendor_id TEXT NOT NULL,
  response_id TEXT DEFAULT '',
  overall_score INTEGER DEFAULT 0,
  overall_level TEXT DEFAULT 'medium',
  category_scores TEXT DEFAULT '{}',
  findings TEXT DEFAULT '[]',
  summary TEXT DEFAULT '',
  created_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS vendor_remediations (
  id TEXT PRIMARY KEY,
  vendor_id TEXT NOT NULL,
  assessment_id TEXT DEFAULT '',
  description TEXT DEFAULT '',
  priority TEXT DEFAULT 'medium',
  status TEXT DEFAULT 'open',
  owner TEXT DEFAULT '',
  due_date TEXT DEFAULT '',
  created_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS vendor_activities (
  id TEXT PRIMARY KEY,
  vendor_id TEXT NOT NULL,
  action TEXT DEFAULT '',
  detail TEXT DEFAULT '',
  performed_by TEXT DEFAULT 'system',
  notes TEXT DEFAULT '',
  timestamp TEXT DEFAULT '',
  created_at TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_responses_vendor ON vendor_responses(vendor_id);
CREATE INDEX IF NOT EXISTS idx_assessments_vendor ON vendor_assessments(vendor_id);
CREATE INDEX IF NOT EXISTS idx_remediations_vendor ON vendor_remediations(vendor_id);
CREATE INDEX IF NOT EXISTS idx_activities_vendor ON vendor_activities(vendor_id);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    cmmc_cols = {
        "handles_cui": "INTEGER DEFAULT 0",
        "cmmc_level": "TEXT DEFAULT ''",
        "sprs_score": "INTEGER",
        "flow_down_clause_signed": "TEXT DEFAULT ''",
        "cui_categories": "TEXT DEFAULT '[]'",
        "last_assessment_date": "TEXT DEFAULT ''",
    }
    for col, dtype in cmmc_cols.items():
        try:
            db.execute(f"ALTER TABLE vendors ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass
    soc2_cols = {
        "soc_report_date": "TEXT DEFAULT ''",
        "review_date": "TEXT DEFAULT ''",
        "data_types": "TEXT DEFAULT '[]'",
    }
    for col, dtype in soc2_cols.items():
        try:
            db.execute(f"ALTER TABLE vendors ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass
    soc2_report_cols = {
        "soc_report_type": "TEXT DEFAULT ''",
        "soc_report_opinion": "TEXT DEFAULT ''",
        "soc_report_coverage_start": "TEXT DEFAULT ''",
        "soc_report_coverage_end": "TEXT DEFAULT ''",
        "next_review_due": "TEXT DEFAULT ''",
    }
    for col, dtype in soc2_report_cols.items():
        try:
            db.execute(f"ALTER TABLE vendors ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("tags", "frameworks", "data_residency", "certificates", "cui_categories", "category_scores", "findings", "data_types"):
        val = d.get(col)
        if val is None:
            d[col] = []
        elif isinstance(val, str):
            try:
                d[col] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                d[col] = []
    for col in ("dpa_in_place",):
        if col in d:
            d[col] = bool(d[col])
    # Never expose stored vendor API tokens in responses — presence is enough.
    if d.get("access_token"):
        d["has_access_token"] = True
    d.pop("access_token", None)
    return d


def _rows_to_list(rows: list[sqlite3.Row]) -> list[dict]:
    return [_row_to_dict(r) for r in rows]


def _migrate_from_json(data_dir: str):
    json_path = Path(data_dir) / "vendors.json"
    if not json_path.exists():
        return False
    try:
        with open(json_path) as f:
            old = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    old_vendors = list(old.get("vendors", {}).values()) if isinstance(old, dict) else list(old.values()) if isinstance(old, dict) else []
    if not old_vendors:
        return False
    db = _get_db()
    try:
        for v in old_vendors:
            db.execute(
                "INSERT OR IGNORE INTO vendors (id, name, contact_name, contact_email, contact_phone, website, "
                "product_service, category, ai_service_type, tier, status, risk_score, risk_level, access_token, "
                "tags, org_id, workspace_id, frameworks, data_residency, transfer_mechanism, dpa_in_place, "
                "certificates, reminder_count, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (v.get("id"), v.get("name", ""), v.get("contact_name", ""), v.get("contact_email", ""),
                 v.get("contact_phone", ""), v.get("website", ""), v.get("product_service", ""),
                 v.get("category", ""), v.get("ai_service_type", ""), v.get("tier", ""),
                 v.get("status", "pending"), v.get("risk_score"), v.get("risk_level"),
                 v.get("access_token", ""), json.dumps(v.get("tags", [])),
                 v.get("org_id", ""), v.get("workspace_id", ""), json.dumps(v.get("frameworks", [])),
                 json.dumps(v.get("data_residency", [])), v.get("transfer_mechanism", ""),
                 1 if v.get("dpa_in_place") else 0, json.dumps(v.get("certificates", [])),
                 v.get("reminder_count", 0), v.get("created_at", utcnow())),
            )
        db.commit()
        return True
    finally:
        db.close()


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = os.environ.get("VENDOR_DB_PATH") or str(Path(data_dir) / "vendors.db")
    db = _get_db()
    _ensure_schema(db)
    count = db.execute("SELECT COUNT(*) as c FROM vendors").fetchone()["c"]
    migrated = False
    if count == 0:
        migrated = _migrate_from_json(data_dir)
    db.close()
    if count == 0 and not migrated:
        seed_data(org_id="demo", workspace_id="demo")


def _log(vendor_id: str, action: str, notes: str = "", detail: str = "", performed_by: str = "system"):
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO vendor_activities (id, vendor_id, action, detail, performed_by, notes, timestamp, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (uuid4().hex[:12], vendor_id, action, detail or notes, performed_by, notes, utcnow(), utcnow()),
        )
        db.commit()
    finally:
        db.close()


# ─── Vendors ──────────────────────────────────


def list_vendors(org_id: str | None = None, framework_id: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        if org_id and framework_id:
            rows = db.execute(
                "SELECT * FROM vendors WHERE org_id = ?", (org_id,)
            ).fetchall()
        elif org_id:
            rows = db.execute(
                "SELECT * FROM vendors WHERE org_id = ? ORDER BY created_at DESC", (org_id,)
            ).fetchall()
        elif framework_id:
            rows = db.execute(
                "SELECT * FROM vendors ORDER BY created_at DESC"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM vendors ORDER BY created_at DESC"
            ).fetchall()

        items = _rows_to_list(rows)
        if framework_id:
            items = [v for v in items if framework_id in v.get("frameworks", [])]
        return items
    finally:
        db.close()


def get_vendor(vid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM vendors WHERE id = ?", (vid,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def create_vendor(
    name: str,
    contact_name: str = "",
    contact_email: str = "",
    contact_phone: str = "",
    website: str = "",
    product_service: str = "",
    category: str = "",
    ai_service_type: str = "",
    tier: str = "",
    tags: list[str] | None = None,
    org_id: str = "",
    workspace_id: str = "",
    frameworks: list[str] | None = None,
    data_residency: list[str] | None = None,
    transfer_mechanism: str = "",
    dpa_in_place: bool = False,
    handles_cui: bool = False,
    cmmc_level: str = "",
    sprs_score: int | None = None,
    flow_down_clause_signed: str = "",
    cui_categories: list[str] | None = None,
    last_assessment_date: str = "",
    soc_report_type: str = "",
    soc_report_opinion: str = "",
    soc_report_coverage_start: str = "",
    soc_report_coverage_end: str = "",
    next_review_due: str = "",
    review_date: str = "",
) -> dict:
    vid = uuid4().hex[:12]
    now = utcnow()
    db = _get_db()
    try:
        db.execute(
            """INSERT INTO vendors (id, name, contact_name, contact_email, contact_phone, website,
               product_service, category, ai_service_type, tier, status, access_token,
               tags, org_id, workspace_id, frameworks, data_residency, transfer_mechanism,
               dpa_in_place, handles_cui, cmmc_level, sprs_score, flow_down_clause_signed,
               cui_categories, last_assessment_date, soc_report_type, soc_report_opinion,
               soc_report_coverage_start, soc_report_coverage_end, next_review_due, review_date, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                vid, name, contact_name, contact_email, contact_phone, website,
                product_service, category, ai_service_type, tier, "pending", uuid4().hex,
                json.dumps(tags or []), org_id, workspace_id,
                json.dumps(frameworks or []), json.dumps(data_residency or []),
                transfer_mechanism, 1 if dpa_in_place else 0,
                1 if handles_cui else 0, cmmc_level, sprs_score, flow_down_clause_signed,
                json.dumps(cui_categories or []), last_assessment_date,
                soc_report_type, soc_report_opinion,
                soc_report_coverage_start, soc_report_coverage_end,
                next_review_due, review_date, now,
            ),
        )
        db.commit()
    finally:
        db.close()

    _log(vid, "created", f"Vendor {name} created")
    return get_vendor(vid) or {}


def update_vendor(vid: str, **kwargs) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM vendors WHERE id = ?", (vid,)).fetchone()
        if not row:
            return None
        current = dict(row)
        for k, val in kwargs.items():
            if val is not None and k != "id":
                if isinstance(val, list):
                    current[k] = json.dumps(val)
                elif isinstance(val, bool):
                    current[k] = 1 if val else 0
                else:
                    current[k] = val
        current["updated_at"] = utcnow()
        sets = ", ".join(f"{k} = ?" for k in kwargs if k != "id")
        if not sets:
            return _row_to_dict(row)
        vals = []
        for k in kwargs:
            if k == "id":
                continue
            v = kwargs[k]
            if v is not None:
                if isinstance(v, list):
                    vals.append(json.dumps(v))
                elif isinstance(v, bool):
                    vals.append(1 if v else 0)
                else:
                    vals.append(v)
            else:
                vals.append(None)
        vals.append(vid)
        db.execute(f"UPDATE vendors SET {sets}, updated_at = ? WHERE id = ?",
                   (*vals, utcnow(), vid))
        db.commit()
    finally:
        db.close()

    _log(vid, "updated", "Vendor updated")
    return get_vendor(vid)


def delete_vendor(vid: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT id FROM vendors WHERE id = ?", (vid,)).fetchone()
        if not row:
            return False
        db.execute("DELETE FROM vendors WHERE id = ?", (vid,))
        db.execute("DELETE FROM vendor_responses WHERE vendor_id = ?", (vid,))
        db.execute("DELETE FROM vendor_assessments WHERE vendor_id = ?", (vid,))
        db.execute("DELETE FROM vendor_remediations WHERE vendor_id = ?", (vid,))
        db.execute("DELETE FROM vendor_activities WHERE vendor_id = ?", (vid,))
        db.commit()
        return True
    finally:
        db.close()


# ─── Responses ────────────────────────────────


def get_response(response_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM vendor_responses WHERE id = ?", (response_id,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def get_response_by_vendor(vendor_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT * FROM vendor_responses WHERE vendor_id = ? ORDER BY created_at DESC",
            (vendor_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def list_responses(vendor_id: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        if vendor_id:
            rows = db.execute(
                "SELECT * FROM vendor_responses WHERE vendor_id = ? ORDER BY created_at DESC",
                (vendor_id,),
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM vendor_responses ORDER BY created_at DESC").fetchall()
        return _rows_to_list(rows)
    finally:
        db.close()


def save_draft_response(vendor_id: str, answers: list[dict], questionnaire_id: str = "default") -> dict:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT * FROM vendor_responses WHERE vendor_id = ? AND status = 'draft'",
            (vendor_id,),
        ).fetchone()
        if row:
            db.execute(
                "UPDATE vendor_responses SET answers = ?, updated_at = ? WHERE id = ?",
                (json.dumps(answers), utcnow(), row["id"]),
            )
            db.commit()
            return _row_to_dict(row)
        else:
            rid = uuid4().hex[:12]
            now = utcnow()
            db.execute(
                "INSERT INTO vendor_responses (id, vendor_id, questionnaire_id, status, answers, created_at) "
                "VALUES (?, ?, ?, 'draft', ?, ?)",
                (rid, vendor_id, questionnaire_id, json.dumps(answers), now),
            )
            db.commit()
            row = db.execute("SELECT * FROM vendor_responses WHERE id = ?", (rid,)).fetchone()
            return _row_to_dict(row) if row else {}
    finally:
        db.close()


def submit_response(vendor_id: str, answers: list[dict], questionnaire_id: str = "default") -> dict:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT * FROM vendor_responses WHERE vendor_id = ?",
            (vendor_id,),
        ).fetchone()
        now = utcnow()
        if row:
            db.execute(
                "UPDATE vendor_responses SET answers = ?, status = 'submitted', submitted_at = ? WHERE id = ?",
                (json.dumps(answers), now, row["id"]),
            )
            db.commit()
            new_row = db.execute("SELECT * FROM vendor_responses WHERE id = ?", (row["id"],)).fetchone()
            return _row_to_dict(new_row) if new_row else {}
        else:
            rid = uuid4().hex[:12]
            db.execute(
                "INSERT INTO vendor_responses (id, vendor_id, questionnaire_id, status, answers, created_at, submitted_at) "
                "VALUES (?, ?, ?, 'submitted', ?, ?, ?)",
                (rid, vendor_id, questionnaire_id, json.dumps(answers), now, now),
            )
            db.commit()
            new_row = db.execute("SELECT * FROM vendor_responses WHERE id = ?", (rid,)).fetchone()
            return _row_to_dict(new_row) if new_row else {}
    finally:
        db.close()


# ─── Assessments ──────────────────────────────


def get_assessment_by_vendor(vendor_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute(
            "SELECT * FROM vendor_assessments WHERE vendor_id = ? ORDER BY created_at DESC",
            (vendor_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def create_assessment(vendor_id: str, response_id: str, overall_score: int,
                      overall_level: str, category_scores: dict, findings: list[dict]) -> dict:
    aid = uuid4().hex[:12]
    now = utcnow()
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO vendor_assessments (id, vendor_id, response_id, overall_score, overall_level, "
            "category_scores, findings, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (aid, vendor_id, response_id, overall_score, overall_level,
             json.dumps(category_scores), json.dumps(findings),
             f"Score: {overall_score} ({overall_level})", now),
        )
        db.commit()
    finally:
        db.close()

    for f in findings:
        if f.get("severity") in ("high", "critical"):
            create_remediation(
                vendor_id=vendor_id,
                assessment_id=aid,
                description=f.get("description", ""),
                priority=f.get("severity", "high"),
            )

    update_vendor(vendor_id, risk_score=overall_score, risk_level=overall_level, status="assessed")
    _log(vendor_id, "assessed", f"Score: {overall_score} ({overall_level})")
    return get_assessment_by_vendor(vendor_id) or {}


# ─── Remediations ──────────────────────────────


def list_remediations(vendor_id: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        if vendor_id:
            rows = db.execute(
                "SELECT * FROM vendor_remediations WHERE vendor_id = ? ORDER BY created_at DESC",
                (vendor_id,),
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM vendor_remediations ORDER BY created_at DESC").fetchall()
        return _rows_to_list(rows)
    finally:
        db.close()


def update_remediation(rid: str, **kwargs) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM vendor_remediations WHERE id = ?", (rid,)).fetchone()
        if not row:
            return None
        sets = ", ".join(f"{k} = ?" for k in kwargs if k != "id")
        if sets:
            vals = [kwargs[k] for k in kwargs if k != "id"] + [rid]
            db.execute(f"UPDATE vendor_remediations SET {sets} WHERE id = ?", vals)
            db.commit()
        new = db.execute("SELECT * FROM vendor_remediations WHERE id = ?", (rid,)).fetchone()
        return _row_to_dict(new) if new else None
    finally:
        db.close()


def create_remediation(vendor_id: str, assessment_id: str, description: str = "",
                       priority: str = "medium", status: str = "open",
                       owner: str = "", due_date: str = "") -> dict:
    rid = uuid4().hex[:12]
    now = utcnow()
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO vendor_remediations (id, vendor_id, assessment_id, description, priority, status, owner, due_date, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (rid, vendor_id, assessment_id, description, priority, status, owner, due_date, now),
        )
        db.commit()
    finally:
        db.close()
    _log(vendor_id, "remediation_created", f"Remediation created: {description}")
    return {"id": rid, "vendor_id": vendor_id, "assessment_id": assessment_id,
            "description": description, "priority": priority, "status": status,
            "owner": owner, "due_date": due_date, "created_at": now}


# ─── Framework Linking ──────────────────────────


def link_framework(vid: str, framework_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT frameworks FROM vendors WHERE id = ?", (vid,)).fetchone()
        if not row:
            return None
        current = set()
        try:
            current = set(json.loads(row["frameworks"]))
        except (json.JSONDecodeError, TypeError):
            pass
        current.add(framework_id)
        db.execute("UPDATE vendors SET frameworks = ? WHERE id = ?",
                   (json.dumps(sorted(current)), vid))
        db.commit()
    finally:
        db.close()
    _log(vid, "framework_linked", f"Linked to {framework_id}")
    return get_vendor(vid)


def unlink_framework(vid: str, framework_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT frameworks FROM vendors WHERE id = ?", (vid,)).fetchone()
        if not row:
            return None
        current = []
        try:
            current = json.loads(row["frameworks"])
        except (json.JSONDecodeError, TypeError):
            pass
        current = [f for f in current if f != framework_id]
        db.execute("UPDATE vendors SET frameworks = ? WHERE id = ?",
                   (json.dumps(current), vid))
        db.commit()
    finally:
        db.close()
    _log(vid, "framework_unlinked", f"Unlinked from {framework_id}")
    return get_vendor(vid)


# ─── Seed ──────────────────────────────────────


def seed_data(name: str = "default", org_id: str = "", workspace_id: str = "", force: bool = False) -> int:
    db = _get_db()
    try:
        count = db.execute("SELECT COUNT(*) as c FROM vendors").fetchone()["c"]
        if count > 0:
            if not force:
                return 0
            if not os.environ.get("KHESTRA_ALLOW_SEED_DELETE"):
                raise RuntimeError("Set KHESTRA_ALLOW_SEED_DELETE=1 to force seed deletion of existing vendor data")
            db.executescript("DELETE FROM vendors; DELETE FROM vendor_responses; DELETE FROM vendor_assessments; DELETE FROM vendor_remediations; DELETE FROM vendor_activities;")
    finally:
        db.close()

    from .questionnaire import score_response

    samples = [
        {"name": "Acme AI Corp", "contact_name": "Jane",
         "contact_email": "jane@acme.ai", "product_service": "Customer support chatbot",
         "answers": [{"id": "q1", "value": "San Francisco, US"}, {"id": "q2", "value": "AI chatbot platform"}, {"id": "q3", "value": ""}, {"id": "q4", "value": "US Only"}, {"id": "q5", "value": "Confidential"}, {"id": "q6", "value": "SOC 2 Type II, ISO 27001"}, {"id": "q7", "value": "Type II"}, {"id": "q8", "value": "Yes"}]},
        {"name": "DataScale Inc", "contact_name": "Bob",
         "contact_email": "bob@datascale.io", "product_service": "Data labeling platform",
         "answers": [{"id": "q1", "value": "EU"}, {"id": "q2", "value": "Data labeling and annotation"}, {"id": "q3", "value": ""}, {"id": "q4", "value": "EU/EEA"}, {"id": "q5", "value": "Restricted"}, {"id": "q6", "value": "ISO 27001"}, {"id": "q7", "value": "Type I"}, {"id": "q8", "value": "No"}]},
        {"name": "NeuralPath AI", "contact_name": "Alice",
         "contact_email": "alice@neuralpath.ai", "product_service": "LLM fine-tuning pipeline",
         "answers": [{"id": "q1", "value": "Global"}, {"id": "q2", "value": "ML model training"}, {"id": "q3", "value": ""}, {"id": "q4", "value": "Global"}, {"id": "q5", "value": "PII"}, {"id": "q6", "value": "None"}, {"id": "q7", "value": "In Progress"}, {"id": "q8", "value": "Yes"}]},
    ]
    for d in samples:
        vid = uuid4().hex[:12]
        now = utcnow()
        db = _get_db()
        try:
            db.execute(
                "INSERT INTO vendors (id, name, contact_name, contact_email, product_service, status, access_token, org_id, workspace_id, created_at) "
                "VALUES (?, ?, ?, ?, ?, 'assessed', ?, ?, ?, ?)",
                (vid, d["name"], d.get("contact_name", ""), d.get("contact_email", ""),
                 d.get("product_service", ""), uuid4().hex, org_id, workspace_id, now),
            )
            db.commit()
        finally:
            db.close()

        # Create submitted questionnaire response
        rid = uuid4().hex[:12]
        db = _get_db()
        try:
            db.execute(
                "INSERT INTO vendor_responses (id, vendor_id, questionnaire_id, status, answers, created_at, submitted_at) "
                "VALUES (?, ?, 'default', 'submitted', ?, ?, ?)",
                (rid, vid, json.dumps(d["answers"]), now, now),
            )
            db.commit()
        finally:
            db.close()

        # Run assessment
        result = score_response(d["answers"])
        db = _get_db()
        try:
            db.execute(
                """INSERT INTO vendor_assessments (id, vendor_id, response_id, overall_score, overall_level,
                   category_scores, findings, summary, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (uuid4().hex[:12], vid, rid, result["overallScore"], result["overallLevel"],
                 json.dumps(result["categoryScores"]), json.dumps(result["findings"]),
                 result.get("summary", ""), now),
            )
            db.commit()
        finally:
            db.close()

        _log(vid, "created", f"Vendor {d['name']} created (seed)")
        _log(vid, "submitted", "Questionnaire submitted by vendor")
        _log(vid, "assessed", f"Assessment completed — score {result['overallScore']}/100 ({result['overallLevel']})")
    return len(samples)


# ─── CSV Export ────────────────────────────────


def export_vendors_csv(vendors: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "name", "status", "risk_score", "risk_level", "contact_email",
                 "contact_name", "category", "ai_service_type", "tier", "created_at"])
    for v in vendors:
        w.writerow([
            v.get("id", ""), v.get("name", ""), v.get("status", ""),
            v.get("risk_score", ""), v.get("risk_level", ""), v.get("contact_email", ""),
            v.get("contact_name", ""), v.get("category", ""), v.get("ai_service_type", ""),
            v.get("tier", ""), v.get("created_at", ""),
        ])
    return buf.getvalue()


# ─── Activities ────────────────────────────────


def list_activities(vendor_id: str) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT * FROM vendor_activities WHERE vendor_id = ? ORDER BY created_at DESC",
            (vendor_id,),
        ).fetchall()
        return _rows_to_list(rows)
    finally:
        db.close()
