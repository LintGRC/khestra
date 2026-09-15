import json
import sqlite3
import os
from pathlib import Path
from uuid import uuid4

from .models import RiskItem, RiskComment, utcnow


DB_PATH: str | None = None
_RISKS_DB: str | None = None


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("RISKS_DB_PATH") or DB_PATH or "/tmp/khestra-risks.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS risks (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  category TEXT DEFAULT '',
  framework TEXT DEFAULT '',
  control_ids TEXT DEFAULT '[]',
  control_id TEXT DEFAULT '',
  system_id TEXT DEFAULT '',
  owner TEXT DEFAULT '',
  status TEXT DEFAULT 'identified',
  likelihood INTEGER DEFAULT 0,
  impact INTEGER DEFAULT 0,
  inherent_score INTEGER DEFAULT 0,
  residual_likelihood INTEGER DEFAULT 0,
  residual_impact INTEGER DEFAULT 0,
  residual_score INTEGER DEFAULT 0,
  treatment TEXT DEFAULT '',
  treatment_plan TEXT DEFAULT '',
  controls TEXT DEFAULT '',
  mitigation_evidence TEXT DEFAULT '[]',
  tags TEXT DEFAULT '[]',
  framework_metadata TEXT DEFAULT '{}',
  created_by TEXT DEFAULT '',
  review_date TEXT DEFAULT '',
  acceptance_expires TEXT DEFAULT '',
  control_owner TEXT DEFAULT '',
  comments TEXT DEFAULT '[]',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT '',
  closed_at TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_risks_framework ON risks(framework);
CREATE INDEX IF NOT EXISTS idx_risks_status ON risks(status);
CREATE INDEX IF NOT EXISTS idx_risks_category ON risks(category);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    cols = {r[1] for r in db.execute("PRAGMA table_info(risks)")}
    if "acceptance_expires" not in cols:
        db.execute("ALTER TABLE risks ADD COLUMN acceptance_expires TEXT DEFAULT ''")
    if "control_owner" not in cols:
        db.execute("ALTER TABLE risks ADD COLUMN control_owner TEXT DEFAULT ''")


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("control_ids", "mitigation_evidence", "tags", "framework_metadata", "comments"):
        val = d.get(col)
        if val is None:
            d[col] = [] if col != "framework_metadata" else {}
        elif isinstance(val, str):
            try:
                d[col] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                d[col] = [] if col != "framework_metadata" else {}
    return d


def _rows_to_list(rows: list[sqlite3.Row]) -> list[dict]:
    return [_row_to_dict(r) for r in rows]


def _migrate_from_json(data_dir: str) -> bool:
    json_path = Path(data_dir) / "risks.json"
    if not json_path.exists():
        return False
    try:
        with open(json_path) as f:
            old = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    old_risks = list(old.get("risks", {}).values()) if isinstance(old, dict) else []
    if not old_risks:
        return False
    db = _get_db()
    try:
        for r in old_risks:
            db.execute(
                "INSERT OR IGNORE INTO risks (id, title, description, category, framework, control_ids, control_id, "
                "system_id, owner, status, likelihood, impact, inherent_score, residual_likelihood, residual_impact, "
                "residual_score, treatment, treatment_plan, controls, mitigation_evidence, tags, framework_metadata, "
                "created_by, review_date, acceptance_expires, control_owner, comments, created_at, updated_at, closed_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    r.get("id"), r.get("title", ""), r.get("description", ""),
                    r.get("category", ""), r.get("framework", ""),
                    json.dumps(r.get("control_ids", [])), r.get("control_id", ""),
                    r.get("system_id", ""), r.get("owner", ""), r.get("status", "identified"),
                    r.get("likelihood", 0), r.get("impact", 0), r.get("inherent_score", 0),
                    r.get("residual_likelihood", 0), r.get("residual_impact", 0),
                    r.get("residual_score", 0), r.get("treatment", ""),
                    r.get("treatment_plan", ""), r.get("controls", ""),
                    json.dumps(r.get("mitigation_evidence", [])),
                    json.dumps(r.get("tags", [])),
                    json.dumps(r.get("framework_metadata", {})),
                    r.get("created_by", ""), r.get("review_date", ""),
                    r.get("acceptance_expires", ""), r.get("control_owner", ""),
                    json.dumps(r.get("comments", [])),
                    r.get("created_at", ""), r.get("updated_at", ""), r.get("closed_at", ""),
                ),
            )
        db.commit()
        return True
    finally:
        db.close()


def init_store(data_dir: str):
    global DB_PATH
    shared_dir = Path(__file__).resolve().parents[2] / "data"
    shared_dir.mkdir(parents=True, exist_ok=True)
    DB_PATH = os.environ.get("RISKS_DB_PATH") or str(shared_dir / "risks.db")
    db = _get_db()
    count = db.execute("SELECT COUNT(*) as c FROM risks").fetchone()["c"]
    migrated = False
    if count == 0:
        migrated = _migrate_from_json(data_dir)
    db.close()
    if count == 0 and not migrated:
        seed_risks(data_dir)


def list_risks(
    framework: str | None = None,
    category: str | None = None,
    status: str | None = None,
    owner: str | None = None,
    control_id: str | None = None,
) -> list[dict]:
    db = _get_db()
    try:
        parts = ["SELECT * FROM risks WHERE 1=1"]
        params = []
        if framework:
            parts.append("AND framework = ?")
            params.append(framework)
        if category:
            parts.append("AND category = ?")
            params.append(category)
        if status:
            parts.append("AND status = ?")
            params.append(status)
        if owner:
            parts.append("AND owner = ?")
            params.append(owner)
        if control_id:
            parts.append("AND (control_id = ? OR control_ids LIKE ?)")
            params.extend([control_id, f"%\"{control_id}\"%"])
        sql = " ".join(parts) + " ORDER BY created_at DESC"
        rows = db.execute(sql, params).fetchall()
        return _rows_to_list(rows)
    finally:
        db.close()


def get_risk(rid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM risks WHERE id = ?", (rid,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def get_risks_by_control(control_id: str) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT * FROM risks WHERE control_id = ? OR control_ids LIKE ?",
            (control_id, f"%\"{control_id}\"%"),
        ).fetchall()
        return _rows_to_list(rows)
    finally:
        db.close()


def create_risk(
    title: str,
    description: str = "",
    category: str = "",
    framework: str = "",
    control_ids: list[str] | None = None,
    system_id: str = "",
    owner: str = "",
    likelihood: int = 0,
    impact: int = 0,
    residual_likelihood: int = 0,
    residual_impact: int = 0,
    residual_score: int = 0,
    treatment: str = "",
    treatment_plan: str = "",
    mitigation_evidence: list[str] | None = None,
    tags: list[str] | None = None,
    framework_metadata: dict | None = None,
    created_by: str = "",
    status: str = "identified",
    review_date: str = "",
    acceptance_expires: str = "",
    control_owner: str = "",
    control_id: str = "",
    controls: str = "",
) -> dict:
    rid = uuid4().hex[:12]
    now = utcnow()
    inherent_score = likelihood * impact
    residual_score_val = residual_score or (residual_likelihood * residual_impact)
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO risks (id, title, description, category, framework, control_ids, control_id, "
            "system_id, owner, status, likelihood, impact, inherent_score, residual_likelihood, residual_impact, "
            "residual_score, treatment, treatment_plan, controls, mitigation_evidence, tags, framework_metadata, "
            "created_by, review_date, acceptance_expires, control_owner, comments, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                rid, title, description, category, framework,
                json.dumps(control_ids or []), control_id,
                system_id, owner, status, likelihood, impact, inherent_score,
                residual_likelihood, residual_impact, residual_score_val,
                treatment, treatment_plan, controls or treatment_plan,
                json.dumps(mitigation_evidence or []),
                json.dumps(tags or []),
                json.dumps(framework_metadata or {}),
                created_by or owner, review_date, acceptance_expires, control_owner,
                "[]", now, now,
            ),
        )
        db.commit()
    finally:
        db.close()
    return get_risk(rid) or {}


def update_risk(
    rid: str,
    *,
    title: str | None = None,
    description: str | None = None,
    category: str | None = None,
    framework: str | None = None,
    control_ids: list[str] | None = None,
    control_id: str | None = None,
    system_id: str | None = None,
    owner: str | None = None,
    status: str | None = None,
    likelihood: int | None = None,
    impact: int | None = None,
    residual_likelihood: int | None = None,
    residual_impact: int | None = None,
    residual_score: int | None = None,
    treatment: str | None = None,
    treatment_plan: str | None = None,
    controls: str | None = None,
    mitigation_evidence: list[str] | None = None,
    tags: list[str] | None = None,
    framework_metadata: dict | None = None,
    review_date: str | None = None,
    acceptance_expires: str | None = None,
    control_owner: str | None = None,
    changed_by: str = "",
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM risks WHERE id = ?", (rid,)).fetchone()
        if not row:
            return None
        current = dict(row)
        updates = {}
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if category is not None:
            updates["category"] = category
        if framework is not None:
            updates["framework"] = framework
        if control_ids is not None:
            updates["control_ids"] = json.dumps(control_ids)
        if control_id is not None:
            updates["control_id"] = control_id
        if system_id is not None:
            updates["system_id"] = system_id
        if owner is not None:
            updates["owner"] = owner
        if status is not None:
            updates["status"] = status
        if likelihood is not None:
            updates["likelihood"] = likelihood
        if impact is not None:
            updates["impact"] = impact
        if likelihood is not None or impact is not None:
            lh = likelihood if likelihood is not None else current["likelihood"]
            imp = impact if impact is not None else current["impact"]
            updates["inherent_score"] = lh * imp
        if residual_likelihood is not None:
            updates["residual_likelihood"] = residual_likelihood
        if residual_impact is not None:
            updates["residual_impact"] = residual_impact
        if residual_likelihood is not None or residual_impact is not None:
            rl = residual_likelihood if residual_likelihood is not None else current["residual_likelihood"]
            ri = residual_impact if residual_impact is not None else current["residual_impact"]
            updates["residual_score"] = rl * ri
        elif residual_score is not None:
            updates["residual_score"] = residual_score
        if treatment is not None:
            updates["treatment"] = treatment
        if treatment_plan is not None:
            updates["treatment_plan"] = treatment_plan
        if controls is not None:
            updates["controls"] = controls
        if mitigation_evidence is not None:
            updates["mitigation_evidence"] = json.dumps(mitigation_evidence)
        if tags is not None:
            updates["tags"] = json.dumps(tags)
        if framework_metadata is not None:
            updates["framework_metadata"] = json.dumps(framework_metadata)
        if review_date is not None:
            updates["review_date"] = review_date
        if acceptance_expires is not None:
            updates["acceptance_expires"] = acceptance_expires
        if control_owner is not None:
            updates["control_owner"] = control_owner

        updates["updated_at"] = utcnow()
        if not updates:
            return _row_to_dict(row)

        sets = ", ".join(f"{k} = ?" for k in updates)
        db.execute(f"UPDATE risks SET {sets} WHERE id = ?", (*updates.values(), rid))
        db.commit()
    finally:
        db.close()
    return get_risk(rid)


def delete_risk(rid: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT id FROM risks WHERE id = ?", (rid,)).fetchone()
        if not row:
            return False
        db.execute("DELETE FROM risks WHERE id = ?", (rid,))
        db.commit()
        return True
    finally:
        db.close()


def add_comment(rid: str, author: str, body: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT comments FROM risks WHERE id = ?", (rid,)).fetchone()
        if not row:
            return None
        comments = []
        try:
            comments = json.loads(row["comments"])
        except (json.JSONDecodeError, TypeError):
            comments = []
        comment = RiskComment(
            id=uuid4().hex[:12],
            author=author,
            body=body,
            created_at=utcnow(),
        )
        comments.append(comment.to_dict())
        db.execute("UPDATE risks SET comments = ?, updated_at = ? WHERE id = ?",
                   (json.dumps(comments), utcnow(), rid))
        db.commit()
        return comment.to_dict()
    finally:
        db.close()


def get_stats() -> dict:
    db = _get_db()
    try:
        rows = db.execute("SELECT * FROM risks").fetchall()
        items = _rows_to_list(rows)
        total = len(items)
        by_status: dict[str, int] = {}
        by_category: dict[str, int] = {}
        by_framework: dict[str, int] = {}
        by_treatment: dict[str, int] = {}
        for r in items:
            s = r.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
            c = r.get("category", "unknown")
            by_category[c] = by_category.get(c, 0) + 1
            f = r.get("framework", "unknown") or "cross-framework"
            by_framework[f] = by_framework.get(f, 0) + 1
            t = r.get("treatment", "unknown")
            by_treatment[t] = by_treatment.get(t, 0) + 1
        return {
            "total": total,
            "by_status": by_status,
            "by_category": by_category,
            "by_framework": by_framework,
            "by_treatment": by_treatment,
        }
    finally:
        db.close()


def seed_risks(data_dir: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        count = db.execute("SELECT COUNT(*) as c FROM risks").fetchone()["c"]
        if count > 0:
            return []
    finally:
        db.close()

    samples = [
        {"title": "Critical firmware vulnerability in enclave firewall", "description": "Firewall CVE-2026-0122 exposes CUI enclave to remote exploitation.", "category": "security", "framework": "CMMC Rev 2", "owner": "admin@tridentdefense.com", "control_owner": "M. Rivera — Network Ops", "likelihood": 4, "impact": 4, "residual_likelihood": 3, "residual_impact": 4, "treatment": "mitigate", "status": "in_treatment", "review_date": "2026-07-20", "control_ids": ["SI.L2-3.14.1", "SC.L2-3.13.1"]},
        {"title": "PII exposure via misconfigured S3 bucket", "description": "Customer PII in hr-data-backup bucket accessible without proper bucket policy.", "category": "security", "framework": "SOC 2", "owner": "admin@tridentdefense.com", "control_owner": "K. Patel — Cloud Infra", "likelihood": 4, "impact": 3, "residual_likelihood": 3, "residual_impact": 2, "treatment": "mitigate", "status": "in_treatment", "review_date": "2026-07-30", "control_ids": ["CC6.1", "CC6.6"]},
        {"title": "Third-party SOC 2 report expired — Acme Corp", "description": "No current assessment for vendor handling CUI data.", "category": "third_party", "framework": "SOC 2", "owner": "admin@tridentdefense.com", "control_owner": "J. Alvarez — Vendor Mgmt", "likelihood": 4, "impact": 3, "residual_likelihood": 2, "residual_impact": 2, "treatment": "transfer", "control_ids": ["CC9.2"]},
        {"title": "Privileged access not audited in secrets manager", "description": "Admin access to secrets manager has no audit trail since Apr 2026.", "category": "security", "framework": "CMMC Rev 2", "owner": "admin@tridentdefense.com", "control_owner": "T. Nguyen — IAM", "likelihood": 3, "impact": 4, "residual_likelihood": 3, "residual_impact": 2, "treatment": "mitigate", "review_date": "2026-08-25", "control_ids": ["AU.L2-3.3.1", "AC.L2-3.1.4"]},
        {"title": "No DR plan for critical SCADA systems", "description": "Manufacturing SCADA controllers lack disaster recovery documentation.", "category": "operational", "framework": "CMMC Rev 2", "owner": "admin@tridentdefense.com", "control_owner": "L. Gomez — OT Engineering", "likelihood": 3, "impact": 3, "residual_likelihood": 3, "residual_impact": 3, "treatment": "accept", "status": "in_treatment", "review_date": "2026-07-25", "control_ids": ["SI.L2-3.14.7", "PE.L2-3.10.2"]},
        {"title": "Security awareness training 60% incomplete", "description": "FY26 mandatory training not completed by majority of staff.", "category": "operational", "framework": "SOC 2", "owner": "admin@tridentdefense.com", "likelihood": 3, "impact": 3, "residual_likelihood": 2, "residual_impact": 2, "treatment": "mitigate", "control_ids": ["CC1.4"]},
        {"title": "Vendor risk assessment backlog — 12 overdue", "description": "Q2 2026 quarterly vendor reviews not conducted.", "category": "third_party", "framework": "CMMC Rev 2", "owner": "admin@tridentdefense.com", "control_owner": "J. Alvarez — Vendor Mgmt", "likelihood": 4, "impact": 2, "residual_likelihood": 2, "residual_impact": 2, "treatment": "mitigate", "review_date": "2026-08-15", "control_ids": ["RA.L2-3.11.1", "CC9.2"]},
        {"title": "Encryption key rotation policy lapsed", "description": "KMS keys for CUI encryption not rotated in 18 months.", "category": "security", "framework": "SOC 2", "owner": "admin@tridentdefense.com", "likelihood": 2, "impact": 3, "residual_likelihood": 1, "residual_impact": 2, "treatment": "mitigate", "review_date": "2026-08-12", "control_ids": ["CC6.1"]},
        {"title": "Legacy TLS 1.0 in staging environment", "description": "Non-prod API endpoints still accept TLS 1.0 connections.", "category": "security", "framework": "SOC 2", "owner": "admin@tridentdefense.com", "likelihood": 2, "impact": 3, "residual_likelihood": 1, "residual_impact": 2, "treatment": "mitigate", "control_ids": ["CC6.1", "SC.L1-b.1.x"]},
        {"title": "Badge access not revoked for ex-employees", "description": "Three former employees still have active badge access. Risk accepted on 2026-04-15 with mitigation via quarterly access reviews.", "category": "security", "framework": "CMMC Rev 2", "owner": "admin@tridentdefense.com", "control_owner": "H. Brooks — Facilities", "likelihood": 2, "impact": 2, "residual_likelihood": 2, "residual_impact": 2, "treatment": "accept", "status": "accepted", "acceptance_expires": "2026-04-15", "control_ids": ["PE.L2-3.10.1", "AC.L2-3.1.11"]},
        {"title": "Audit log retention only 90 days", "description": "Policy requires 12-month retention for CUI audit logs.", "category": "compliance", "framework": "SOC 2", "owner": "admin@tridentdefense.com", "likelihood": 2, "impact": 4, "residual_likelihood": 2, "residual_impact": 2, "treatment": "mitigate", "control_ids": ["CC7.2", "AU.L2-3.3.2"]},
        {"title": "Data retention policy not enforced on file shares", "description": "Outdated CUI documents retained beyond 5-year policy limit.", "category": "compliance", "framework": "CMMC Rev 2", "owner": "admin@tridentdefense.com", "likelihood": 1, "impact": 2, "residual_likelihood": 1, "residual_impact": 1, "treatment": "mitigate", "control_ids": ["MP.L2-3.8.1", "CC6.7"]},
        {"title": "Guest Wi-Fi not segmented from enclave", "description": "Physical network separation between guest and CUI enclave unvalidated. Accepted pending network refresh; re-review required.", "category": "security", "framework": "CMMC Rev 2", "owner": "admin@tridentdefense.com", "control_owner": "M. Rivera — Network Ops", "likelihood": 1, "impact": 1, "residual_likelihood": 1, "residual_impact": 1, "treatment": "accept", "status": "accepted", "acceptance_expires": "2027-02-01", "control_ids": ["SC.L1-b.1.xi", "AC.L1-b.1.iii"]},
        {"title": "Antimalware definitions outdated on 40 endpoints", "description": "Realtime protection enabled but signatures >7 days stale on fleet of engineering workstations.", "category": "security", "framework": "CMMC Rev 2", "owner": "admin@tridentdefense.com", "control_owner": "S. Chen — DevOps", "likelihood": 3, "impact": 3, "residual_likelihood": 2, "residual_impact": 2, "treatment": "mitigate", "status": "in_treatment", "review_date": "2026-08-10", "control_ids": ["SI.L2-3.14.2"]},
    ]

    results = []
    for data in samples:
        risk = create_risk(**data)
        if risk:
            results.append(risk)
    return results
