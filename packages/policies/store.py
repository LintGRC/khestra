import json
import sqlite3
import os
from pathlib import Path
from uuid import uuid4
from typing import Optional

from .models import PolicyDocument, PolicyVersion, PolicyAttestation, PolicyMapping, utcnow


DB_PATH: str | None = None


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("POLICIES_DB_PATH") or DB_PATH or "/tmp/khestra-policies.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  content TEXT DEFAULT '',
  version INTEGER DEFAULT 1,
  status TEXT DEFAULT 'draft',
  owner TEXT DEFAULT '',
  framework_tags TEXT DEFAULT '[]',
  mapped_controls TEXT DEFAULT '{}',
  sections TEXT DEFAULT '[]',
  workspace_id TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS versions (
  id TEXT PRIMARY KEY,
  policy_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  content TEXT DEFAULT '',
  title TEXT DEFAULT '',
  description TEXT DEFAULT '',
  change_notes TEXT DEFAULT '',
  created_by TEXT DEFAULT '',
  created_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS attestations (
  id TEXT PRIMARY KEY,
  policy_id TEXT NOT NULL,
  user_name TEXT DEFAULT '',
  acknowledged INTEGER DEFAULT 0,
  date TEXT DEFAULT '',
  notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS mappings (
  id TEXT PRIMARY KEY,
  policy_id TEXT NOT NULL,
  framework TEXT DEFAULT '',
  control_id TEXT DEFAULT '',
  control_label TEXT DEFAULT '',
  mapped_at TEXT DEFAULT ''
);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    _migrate_schema(db)


def _migrate_schema(db: sqlite3.Connection):
    for col in ("approved_by", "approved_at", "rejection_notes", "review_cadence_days", "next_review_date"):
        try:
            db.execute(f"ALTER TABLE documents ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    try:
        db.execute("ALTER TABLE attestations ADD COLUMN user_id TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = os.environ.get("POLICIES_DB_PATH") or str(Path(data_dir) / "policies.db")
    _get_db().close()


def _now() -> str:
    return utcnow()


def _id() -> str:
    return uuid4().hex[:12]


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("framework_tags", "mapped_controls", "sections"):
        if isinstance(d.get(col), str):
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                d[col] = [] if col == "framework_tags" else {}
    return d


# ─── Documents ─────────────────────────────────────────


_FRAMEWORK_KEY_MAP = {
    "soc2": "soc2",
    "cmmc": "cmmc",
    "aigov": "aigov",
    "aigovernance": "aigov",
    "ai_governance": "aigov",
    "iso42001": "iso42001",
    "iso_42001": "iso42001",
}


def list_documents(framework_tag: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute("SELECT * FROM documents ORDER BY updated_at DESC").fetchall()
        docs = [_row_to_dict(r) for r in rows]
        if framework_tag:
            key = _FRAMEWORK_KEY_MAP.get(framework_tag.lower(), framework_tag.lower())
            docs = [
                d for d in docs
                if isinstance(d.get("mapped_controls"), dict)
                and key in d["mapped_controls"]
                and d["mapped_controls"][key]
            ]
        return docs
    finally:
        db.close()


def get_document(doc_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def create_document(
    title: str,
    description: str = "",
    content: str = "",
    owner: str = "",
    framework_tags: list[str] | None = None,
    mapped_controls: dict[str, list[str]] | None = None,
    workspace_id: str = "",
) -> dict:
    db = _get_db()
    try:
        now = _now()
        doc_id = _id()
        doc = PolicyDocument(
            id=doc_id, title=title, description=description, content=content,
            version=1, status="draft", owner=owner,
            framework_tags=framework_tags or [], mapped_controls=mapped_controls or {},
            workspace_id=workspace_id, created_at=now, updated_at=now,
        )
        d = doc.to_dict()
        db.execute(
            """INSERT INTO documents (id, title, description, content, version, status, owner,
               framework_tags, mapped_controls, sections, workspace_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (d["id"], d["title"], d["description"], d["content"],
             d["version"], d["status"], d["owner"],
             json.dumps(d["framework_tags"]), json.dumps(d["mapped_controls"]),
             json.dumps(d.get("sections", [])), d.get("workspace_id", ""),
             d["created_at"], d["updated_at"]),
        )
        _save_version(db, doc_id, 1, d, owner, "Initial version")
        db.commit()
        return d
    finally:
        db.close()


def update_document(
    doc_id: str, *, title: str | None = None, description: str | None = None,
    content: str | None = None, owner: str | None = None, status: str | None = None,
    framework_tags: list[str] | None = None, mapped_controls: dict[str, list[str]] | None = None,
    sections: list[dict] | None = None, review_cadence_days: int | None = None,
    next_review_date: str | None = None,
    change_notes: str = "", changed_by: str = "",
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            return None
        doc = _row_to_dict(row)
        if title is not None: doc["title"] = title
        if description is not None: doc["description"] = description
        if owner is not None: doc["owner"] = owner
        if status is not None: doc["status"] = status
        if framework_tags is not None: doc["framework_tags"] = framework_tags
        if mapped_controls is not None: doc["mapped_controls"] = mapped_controls
        if sections is not None: doc["sections"] = sections
        if review_cadence_days is not None: doc["review_cadence_days"] = review_cadence_days
        if next_review_date is not None: doc["next_review_date"] = next_review_date
        content_changed = content is not None
        if content is not None: doc["content"] = content
        doc["version"] += 1
        doc["updated_at"] = _now()
        db.execute(
            """UPDATE documents SET title=?, description=?, content=?, version=?, status=?, owner=?,
               framework_tags=?, mapped_controls=?, sections=?, updated_at=?,
               review_cadence_days=?, next_review_date=? WHERE id=?""",
            (doc["title"], doc["description"], doc["content"], doc["version"], doc["status"],
             doc["owner"], json.dumps(doc["framework_tags"]), json.dumps(doc["mapped_controls"]),
             json.dumps(doc.get("sections", [])), doc["updated_at"],
             str(doc.get("review_cadence_days", 365)), doc.get("next_review_date", ""),
             doc_id),
        )
        if content_changed:
            _save_version(db, doc_id, doc["version"], doc, changed_by or owner or "", change_notes or "Updated")
        db.commit()
        return doc
    finally:
        db.close()


def delete_document(doc_id: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT 1 FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            return False
        db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        db.execute("DELETE FROM versions WHERE policy_id = ?", (doc_id,))
        db.execute("DELETE FROM attestations WHERE policy_id = ?", (doc_id,))
        db.execute("DELETE FROM mappings WHERE policy_id = ?", (doc_id,))
        db.commit()
        return True
    finally:
        db.close()


# ─── Versions ──────────────────────────────────────────


def _save_version(db: sqlite3.Connection, policy_id: str, version: int, doc: dict, created_by: str, change_notes: str):
    vid = f"{policy_id}_v{version}"
    existing = db.execute("SELECT 1 FROM versions WHERE id = ?", (vid,)).fetchone()
    if existing:
        return
    pv = PolicyVersion(
        id=vid,
        policy_id=policy_id,
        version=version,
        content=doc.get("content", ""),
        title=doc.get("title", ""),
        description=doc.get("description", ""),
        change_notes=change_notes,
        created_by=created_by,
        created_at=_now(),
    )
    d = pv.to_dict()
    db.execute(
        """INSERT INTO versions (id, policy_id, version, content, title, description,
           change_notes, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (d["id"], d["policy_id"], d["version"], d["content"],
         d["title"], d["description"], d["change_notes"],
         d["created_by"], d["created_at"]),
    )


def list_versions(policy_id: str) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute("SELECT * FROM versions WHERE policy_id = ? ORDER BY version", (policy_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def get_version(policy_id: str, version: int) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM versions WHERE policy_id = ? AND version = ?", (policy_id, version)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def list_attestations(policy_id: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        if policy_id:
            rows = db.execute("SELECT * FROM attestations WHERE policy_id = ? ORDER BY date DESC", (policy_id,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM attestations ORDER BY date DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def create_attestation(policy_id: str, user_name: str, user_id: str = "", notes: str = "") -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT 1 FROM documents WHERE id = ?", (policy_id,)).fetchone()
        if not row:
            return None
        # prevent duplicate attestations from the same user
        if user_id:
            dup = db.execute(
                "SELECT id FROM attestations WHERE policy_id=? AND user_id=? AND acknowledged=1",
                (policy_id, user_id),
            ).fetchone()
            if dup:
                existing = db.execute("SELECT * FROM attestations WHERE id=?", (dup["id"],)).fetchone()
                return {"duplicate": True, "attestation": dict(existing)}
        att = PolicyAttestation(id=_id(), policy_id=policy_id, user_name=user_name, acknowledged=True, date=_now(), notes=notes)
        d = att.to_dict()
        d["user_id"] = user_id
        db.execute("INSERT INTO attestations (id, policy_id, user_name, user_id, acknowledged, date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (d["id"], d["policy_id"], d["user_name"], d.get("user_id", ""), 1 if d["acknowledged"] else 0, d["date"], d["notes"]))
        db.commit()
        return d
    finally:
        db.close()


def list_mappings(policy_id: str) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute("SELECT * FROM mappings WHERE policy_id = ?", (policy_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def create_mapping(policy_id: str, framework: str, control_id: str, control_label: str = "") -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT 1 FROM documents WHERE id = ?", (policy_id,)).fetchone()
        if not row:
            return None
        m = PolicyMapping(id=_id(), policy_id=policy_id, framework=framework, control_id=control_id, control_label=control_label, mapped_at=_now())
        d = m.to_dict()
        db.execute("INSERT INTO mappings (id, policy_id, framework, control_id, control_label, mapped_at) VALUES (?, ?, ?, ?, ?, ?)",
            (d["id"], d["policy_id"], d["framework"], d["control_id"], d["control_label"], d["mapped_at"]))
        db.commit()
        return d
    finally:
        db.close()


def delete_mapping(mapping_id: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT 1 FROM mappings WHERE id = ?", (mapping_id,)).fetchone()
        if not row:
            return False
        db.execute("DELETE FROM mappings WHERE id = ?", (mapping_id,))
        db.commit()
        return True
    finally:
        db.close()


# ─── Template listing ──────────────────────────────────


def add_builtin_templates():
    """Seed built-in policy templates for demo/pre-assessment use.

    Creates eight CMMC-aligned policy documents with approved status
    so they appear in the audit package export.
    """
    docs = [
        {
            "title": "Access Control Policy",
            "description": "Access control policy defining authorized users, processes, and devices for CUI systems",
            "mapped_controls": {"CMMC": ["AC.L2-3.1.1", "AC.L2-3.1.2", "AC.L2-3.1.3"]},
            "content": (
                "# Access Control Policy\n\n"
                "## Purpose\n"
                "Establish access control requirements for systems processing CUI.\n\n"
                "## Scope\n"
                "All users, processes, and devices accessing the CUI enclave.\n\n"
                "## Policy\n"
                "1. Access is granted based on least privilege principles.\n"
                "2. User accounts are reviewed quarterly.\n"
                "3. Privileged access requires separate approval.\n"
                "4. Session locks engage after 15 minutes of inactivity.\n"
                "5. Remote access requires multi-factor authentication.\n\n"
                "## Enforcement\n"
                "Access violations are logged and reported to the ISO.\n"
            ),
        },
        {
            "title": "Audit and Accountability Policy",
            "description": "Audit logging, review, and retention requirements",
            "mapped_controls": {"CMMC": ["AU.L2-3.3.1", "AU.L2-3.3.2", "AU.L2-3.3.3"]},
            "content": (
                "# Audit and Accountability Policy\n\n"
                "## Purpose\n"
                "Define audit logging requirements for CUI systems.\n\n"
                "## Scope\n"
                "All systems within the CUI enclave.\n\n"
                "## Policy\n"
                "1. Audit logs capture user identity, timestamp, action, and result.\n"
                "2. Logs are retained for 1 year (hot) and 7 years (cold).\n"
                "3. Log reviews occur weekly.\n"
                "4. Audit failures are alerted within 4 hours.\n"
                "5. Audit logs are protected from modification.\n"
            ),
        },
        {
            "title": "Incident Response Plan",
            "description": "Incident handling capability including preparation, detection, analysis, containment, recovery, and user response",
            "mapped_controls": {"CMMC": ["IR.L2-3.6.1", "IR.L2-3.6.2"]},
            "content": (
                "# Incident Response Plan\n\n"
                "## Purpose\n"
                "Establish incident handling capability for CUI systems.\n\n"
                "## Scope\n"
                "All CUI security incidents.\n\n"
                "## Policy\n"
                "1. Preparation: IR team trained quarterly.\n"
                "2. Detection: Monitoring tools cover endpoints, network, and cloud.\n"
                "3. Analysis: Incidents triaged within 1 hour.\n"
                "4. Containment: Affected systems isolated within 4 hours.\n"
                "5. Recovery: Systems restored from verified backups.\n"
                "6. User response: Users report incidents to the ISO immediately.\n"
            ),
        },
        {
            "title": "Configuration Management Baseline",
            "description": "Baseline configuration and system inventory requirements",
            "mapped_controls": {"CMMC": ["CM.L2-3.4.1", "CM.L2-3.4.2"]},
            "content": (
                "# Configuration Management Baseline\n\n"
                "## Purpose\n"
                "Define baseline configurations for CUI systems.\n\n"
                "## Scope\n"
                "All in-scope hardware and software.\n\n"
                "## Policy\n"
                "1. Baseline configurations are documented for each system type.\n"
                "2. Configuration changes follow the change management process.\n"
                "3. System inventory is maintained in the CMDB.\n"
                "4. Unnecessary ports, protocols, and services are disabled.\n"
                "5. Baseline deviations require ISO approval.\n"
            ),
        },
        {
            "title": "Media Protection Policy",
            "description": "Storage, access, transport, and sanitization of CUI media",
            "mapped_controls": {"CMMC": ["MP.L2-3.8.1", "MP.L2-3.8.2", "MP.L2-3.8.3"]},
            "content": (
                "# Media Protection Policy\n\n"
                "## Purpose\n"
                "Protect CUI on system media throughout its lifecycle.\n\n"
                "## Scope\n"
                "All media containing CUI.\n\n"
                "## Policy\n"
                "1. CUI media is stored in controlled environments.\n"
                "2. Access to CUI media is restricted to authorized personnel.\n"
                "3. Media sanitization follows NIST SP 800-88 guidelines.\n"
                "4. Transported media is protected via encryption.\n"
                "5. Removable media is controlled and logged.\n"
            ),
        },
        {
            "title": "Risk Assessment Policy",
            "description": "Periodic risk assessment and vulnerability scanning requirements",
            "mapped_controls": {"CMMC": ["RA.L2-3.11.1", "RA.L2-3.11.2", "RA.L2-3.11.3"]},
            "content": (
                "# Risk Assessment Policy\n\n"
                "## Purpose\n"
                "Define risk assessment and vulnerability scanning requirements.\n\n"
                "## Scope\n"
                "All CUI systems and applications.\n\n"
                "## Policy\n"
                "1. Risk assessments are conducted annually.\n"
                "2. Vulnerability scans are run monthly.\n"
                "3. Critical vulnerabilities are remediated within 15 days.\n"
                "4. High vulnerabilities are remediated within 30 days.\n"
                "5. Scan results are reviewed by the ISO.\n"
            ),
        },
        {
            "title": "Personnel Security Policy",
            "description": "Screening, termination, and transfer procedures for CUI access",
            "mapped_controls": {"CMMC": ["PS.L2-3.9.1", "PS.L2-3.9.2"]},
            "content": (
                "# Personnel Security Policy\n\n"
                "## Purpose\n"
                "Ensure personnel with CUI access are screened and access is terminated promptly.\n\n"
                "## Scope\n"
                "All personnel with access to CUI systems.\n\n"
                "## Policy\n"
                "1. Background screenings are completed before CUI access is granted.\n"
                "2. Access is revoked within 24 hours of termination.\n"
                "3. Transferred personnel have access re-approved.\n"
                "4. Exit interviews include account confirmation.\n"
            ),
        },
        {
            "title": "System and Communications Protection Policy",
            "description": "Boundary protection, cryptography, and network security requirements",
            "mapped_controls": {"CMMC": ["SC.L2-3.13.1", "SC.L2-3.13.11", "SC.L2-3.13.16"]},
            "content": (
                "# System and Communications Protection Policy\n\n"
                "## Purpose\n"
                "Define system boundary protection and cryptography requirements.\n\n"
                "## Scope\n"
                "All systems and communications within the CUI enclave.\n\n"
                "## Policy\n"
                "1. External boundaries are protected by firewalls and IDS.\n"
                "2. CUI in transit is encrypted using FIPS 140-2 validated methods.\n"
                "3. CUI at rest is encrypted using AES-256.\n"
                "4. Network segregation separates CUI from non-CUI traffic.\n"
                "5. Collaborative computing devices indicate active use.\n"
            ),
        },
    ]

    import logging as _logging
    _log = _logging.getLogger(__name__)
    existing = list_documents()
    if existing:
        _log.info("Templates already seeded (%d docs), skipping", len(existing))
        return

    for doc_data in docs:
        try:
            d = create_document(
                title=doc_data["title"],
                description=doc_data.get("description", ""),
                content=doc_data["content"],
                owner="Sam Rivera",
                framework_tags=["CMMC"],
                mapped_controls=doc_data.get("mapped_controls", {}),
            )
            doc_id = d["id"]
            update_document(doc_id, status="under_review", changed_by="Sam Rivera")
            approve_document(doc_id, approved_by="Jordan Lee")
        except Exception as exc:
            _log.warning("Failed to seed template %s: %s", doc_data["title"], exc)


def list_templates() -> list[dict]:
    from .templates import BUILTIN_TEMPLATES
    return BUILTIN_TEMPLATES


# ─── Approval Workflow ──────────────────────────────────


def submit_for_review(doc_id: str, submitted_by: str = "") -> dict | None:
    """Transition from draft → under_review."""
    db = _get_db()
    try:
        row = db.execute("SELECT status FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            return None
        status = row["status"]
        if status != "draft":
            raise ValueError(f"Cannot submit policy in '{status}' status (must be 'draft')")
        db.execute(
            "UPDATE documents SET status='under_review', updated_at=? WHERE id=?",
            (_now(), doc_id),
        )
        db.commit()
        return get_document(doc_id)
    finally:
        db.close()


def approve_document(doc_id: str, approved_by: str = "") -> dict | None:
    """Transition from under_review → approved. Sets approved_by, approved_at, next_review_date."""
    db = _get_db()
    try:
        row = db.execute(
            "SELECT status, review_cadence_days, updated_at FROM documents WHERE id=?",
            (doc_id,),
        ).fetchone()
        if not row:
            return None
        if row["status"] != "under_review":
            raise ValueError(f"Cannot approve policy in '{row['status']}' status (must be 'under_review')")
        from datetime import timedelta
        cadence = int(row["review_cadence_days"]) if row["review_cadence_days"] else 365
        now = _now()
        if cadence > 0:
            from datetime import datetime as _dt
            next_review = (_dt.now() + timedelta(days=cadence)).strftime("%Y-%m-%d")
        else:
            next_review = ""
        db.execute(
            "UPDATE documents SET status='approved', approved_by=?, approved_at=?, "
            "next_review_date=?, updated_at=? WHERE id=?",
            (approved_by, now, next_review, now, doc_id),
        )
        db.commit()
        return get_document(doc_id)
    finally:
        db.close()


def publish_document(doc_id: str) -> dict | None:
    """Transition from approved → published."""
    db = _get_db()
    try:
        row = db.execute("SELECT status FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            return None
        if row["status"] != "approved":
            raise ValueError(f"Cannot publish policy in '{row['status']}' status (must be 'approved')")
        db.execute(
            "UPDATE documents SET status='published', updated_at=? WHERE id=?",
            (_now(), doc_id),
        )
        db.commit()
        return get_document(doc_id)
    finally:
        db.close()


def reject_document(doc_id: str, rejection_notes: str = "", rejected_by: str = "") -> dict | None:
    """Transition from under_review → draft with rejection notes."""
    db = _get_db()
    try:
        row = db.execute("SELECT status FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            return None
        if row["status"] != "under_review":
            raise ValueError(f"Cannot reject policy in '{row['status']}' status (must be 'under_review')")
        db.execute(
            "UPDATE documents SET status='draft', rejection_notes=?, updated_at=? WHERE id=?",
            (rejection_notes, _now(), doc_id),
        )
        db.commit()
        return get_document(doc_id)
    finally:
        db.close()
