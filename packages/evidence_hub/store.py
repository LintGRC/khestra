import csv
import hashlib
import io
import json
import mimetypes
import os
import re
import sqlite3
import sys
import zipfile
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone


DB_PATH: str | None = None
FILES_DIR: str | None = None

# Canonical evidence framework ids as used by the UI (evidence hub page
# filters, auditor ZIP buttons). Collector attach and older data wrote
# lowercase crosswalk keys / aliases; normalize both at write and read so
# framework-scoped views agree across apps.
CANONICAL_FRAMEWORK_IDS = {"CMMC", "SOC2", "AIGov", "ISO27001"}

FRAMEWORK_ID_ALIASES: dict[str, str] = {
    "cmmc": "CMMC",
    "soc2": "SOC2",
    "aigov": "AIGov",
    "iso27001": "ISO27001",
    "ISO 27001": "ISO27001",
    "AIGOV": "AIGov",
}

# Reverse: evidence canonical id -> CHECK_TO_FRAMEWORKS key.
CROSSWALK_KEY_FOR_EVIDENCE_ID: dict[str, str] = {
    "CMMC": "cmmc",
    "SOC2": "soc2",
    "AIGov": "aigov",
    "AIGOV": "aigov",
    "ISO27001": "iso27001",
    "ISO 27001": "iso27001",
}


def canonical_framework_id(framework_id: str) -> str:
    """Map any framework id spelling used across apps to the canonical one."""
    return FRAMEWORK_ID_ALIASES.get(framework_id, framework_id)


def _migrate_framework_ids(db: sqlite3.Connection) -> None:
    """One-time remap of legacy framework_id spellings in evidence_mappings."""
    for alias, canonical in FRAMEWORK_ID_ALIASES.items():
        db.execute(
            "UPDATE evidence_mappings SET framework_id = ? WHERE framework_id = ?",
            (canonical, alias),
        )
    db.commit()


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("EVIDENCE_DB_PATH") or DB_PATH or "/tmp/khestra-evidence.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL DEFAULT '',
  filename TEXT DEFAULT '',
  description TEXT DEFAULT '',
  tags TEXT DEFAULT '[]',
  uploaded_by TEXT DEFAULT '',
  uploaded_at TEXT DEFAULT '',
  framework_tags TEXT DEFAULT '[]',
  sha256 TEXT DEFAULT '',
  file_size INTEGER DEFAULT 0,
  mime_type TEXT DEFAULT '',
  review_status TEXT DEFAULT 'pending',
  reviewer TEXT DEFAULT '',
  review_comment TEXT DEFAULT '',
  reviewed_at TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT '',
  auto_status TEXT DEFAULT '',
  auto_summary TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS evidence_mappings (
  id TEXT PRIMARY KEY,
  evidence_id TEXT NOT NULL,
  framework_id TEXT NOT NULL DEFAULT '',
  control_id TEXT NOT NULL DEFAULT '',
  mapped_at TEXT DEFAULT '',
  mapped_by TEXT DEFAULT '',
  UNIQUE(evidence_id, framework_id, control_id)
);

CREATE INDEX IF NOT EXISTS idx_mappings_evidence ON evidence_mappings(evidence_id);
CREATE INDEX IF NOT EXISTS idx_mappings_framework ON evidence_mappings(framework_id);

CREATE TABLE IF NOT EXISTS evidence_requests (
  id TEXT PRIMARY KEY,
  framework_id TEXT NOT NULL DEFAULT '',
  control_id TEXT NOT NULL DEFAULT '',
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  assigned_to TEXT DEFAULT '',
  due_date TEXT DEFAULT '',
  status TEXT DEFAULT 'open',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS evidence_access_log (
  id TEXT PRIMARY KEY,
  evidence_id TEXT NOT NULL DEFAULT '',
  action TEXT NOT NULL DEFAULT '',
  performed_by TEXT DEFAULT '',
  performed_at TEXT DEFAULT '',
  ip_address TEXT DEFAULT '',
  metadata TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_access_log_evidence ON evidence_access_log(evidence_id, performed_at);
"""


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    text_cols = ("sha256", "mime_type", "review_status", "reviewer", "review_comment", "reviewed_at")
    for col in text_cols:
        try:
            db.execute(f"ALTER TABLE evidence ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    for col in ("file_size",):
        try:
            db.execute(f"ALTER TABLE evidence ADD COLUMN {col} INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
    for col in ("evidence_type", "display_title", "evidence_version"):
        try:
            db.execute(f"ALTER TABLE evidence ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    for col in ("valid_until",):
        try:
            db.execute(f"ALTER TABLE evidence ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    for col in ("framework_id",):
        try:
            db.execute(f"ALTER TABLE evidence_requests ADD COLUMN {col} TEXT NOT NULL DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    for col in ("auto_status", "auto_summary"):
        try:
            db.execute(f"ALTER TABLE evidence ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    for col in ("period_covered", "archived_at"):
        try:
            db.execute(f"ALTER TABLE evidence ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    try:
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_evidence_collector_period "
            "ON evidence (filename, period_covered, archived_at)"
        )
    except sqlite3.OperationalError:
        pass
    for col in ("preparer", "reviewer", "approver", "review_due_date", "remediation_instructions", "review_began_at", "approval_date"):
        try:
            db.execute(f"ALTER TABLE evidence ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass


def _files_dir() -> Path:
    global FILES_DIR
    d = os.environ.get("EVIDENCE_FILES_DIR") or FILES_DIR or "/tmp/khestra-evidence-files"
    Path(d).mkdir(parents=True, exist_ok=True)
    return Path(d)


def init_store(data_dir: str):
    global DB_PATH, FILES_DIR
    DB_PATH = os.environ.get("EVIDENCE_DB_PATH") or str(Path(data_dir) / "evidence.db")
    FILES_DIR = os.environ.get("EVIDENCE_FILES_DIR") or str(Path(data_dir) / "evidence_files")
    db = _get_db()
    try:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            print(f"WARNING: Evidence DB integrity check failed: {integrity}", file=sys.stderr)
    except Exception:
        pass
    count = db.execute("SELECT COUNT(*) as c FROM evidence").fetchone()["c"]
    _migrate_framework_ids(db)
    db.close()
    if count == 0:
        _seed_demo()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


STALE_DAYS = 90
EXPIRED_DAYS = 180
# Keep one collector artifact per period day; archive periods older than this window.
PERIOD_RETENTION_DAYS = int(os.environ.get("EVIDENCE_PERIOD_RETENTION_DAYS", "90"))
# Hard-delete soft-archived collector rows after this many days past archived_at.
ARCHIVE_DELETE_DAYS = int(os.environ.get("EVIDENCE_ARCHIVE_DELETE_DAYS", "180"))


def _period_day(value: str = "") -> str:
    if not value:
        return ""
    s = value.strip()
    if "T" in s:
        return s.split("T", 1)[0][:10]
    if " " in s:
        return s.split(" ", 1)[0][:10]
    return s[:10]


def _is_collector_row(e: dict) -> bool:
    uploaded_by = e.get("uploaded_by") or ""
    tags = e.get("tags") or []
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            tags = []
    return uploaded_by.startswith("collector:") or "collector" in tags


def _freshness_score(upload_date_str: str = "", valid_until_str: str = "") -> str:
    if valid_until_str:
        try:
            vu = datetime.strptime(valid_until_str.split("T")[0].split(" ")[0], "%Y-%m-%d")
            days_to_expiry = (vu - datetime.now()).days
            if days_to_expiry < 0:
                return "expired"
            if days_to_expiry <= 30:
                return "stale"
            return "fresh"
        except (ValueError, IndexError):
            pass
    if not upload_date_str:
        return "never"
    try:
        dt = datetime.strptime(upload_date_str.split("T")[0].split(" ")[0], "%Y-%m-%d")
    except (ValueError, IndexError):
        return "unknown"
    days = (datetime.now() - dt).days
    if days <= STALE_DAYS:
        return "fresh"
    if days <= EXPIRED_DAYS:
        return "stale"
    return "expired"


def _evidence_provenance(e: dict) -> tuple[str, str]:
    """Derive (source_check, provider) from collector evidence tags.

    Collector rows are tagged ["collector", <connector_id>, <check_id>]
    at ingest (see soc2_collectors/attach.py); manual uploads return "".
    """
    tags = e.get("tags") or []
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            tags = []
    if not tags or tags[0] != "collector" or len(tags) < 3:
        return "", ""
    connector = str(tags[1]) or ""
    check = str(tags[2]) or ""
    provider = connector.replace("-", " ").replace("_", " ").title() if connector else ""
    return check, provider


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in ("tags", "framework_tags"):
        if isinstance(d.get(col), str):
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                d[col] = []
    d["source_check"], d["provider"] = _evidence_provenance(d)
    return d


def _seed_demo():
    db = _get_db()
    try:
        now = _now()

        # Original seed records — upgraded with file content and CMMC mappings
        original_seed = [
            {
                "name": "AWS IAM Screenshot",
                "filename": "cloud-iam-config.png",
                "mime_type": "image/png",
                "content": "[SCREENSHOT] AWS IAM Console — MFA enforcement enabled for all users. Password policy: 14 char, 90-day rotation.",
                "tags": ["access-control", "aws"],
                "evidence_type": "screenshot",
                "display_title": "AWS IAM MFA Configuration",
                "evidence_version": "1.0",
                "mappings": [("SOC2", "CC6.1"), ("CMMC", "AC.L2-3.1.1")],
            },
            {
                "name": "InfoSec Policy v3.2",
                "filename": "infosec-policy-v3.2.pdf",
                "mime_type": "application/pdf",
                "content": (
                    "TRIDENT DEFENSE SYSTEMS — Information Security Policy v3.2\n"
                    "Effective: 2026-01-01\n\n"
                    "1. Purpose: Establish security requirements for CUI and corporate systems.\n"
                    "2. Scope: All Trident employees, contractors, and systems.\n"
                    "3. Policy: Access control, incident response, encryption, training, audits.\n"
                    "4. Enforcement: ISO authority; violations subject to disciplinary action.\n"
                    "Approved: Jordan Lee, VP Operations | Reviewed: Sam Rivera, ISO"
                ),
                "tags": ["policy", "security"],
                "evidence_type": "policy",
                "display_title": "Information Security Policy",
                "evidence_version": "3.2",
                "mappings": [("SOC2", "CC5.2"), ("CMMC", "AC.L2-3.1.1")],
            },
            {
                "name": "SOC 2 Report 2024",
                "filename": "soc2-report-2024.pdf",
                "mime_type": "application/pdf",
                "content": (
                    "SOC 2 TYPE II REPORT — Trident Defense Systems\n"
                    "Report period: January 1, 2024 – December 31, 2024\n"
                    "Trust Service Criteria: Security, Availability, Confidentiality\n\n"
                    "Opinion: Unqualified (clean)\n"
                    "Control categories: 100% operating effectively\n"
                    "Exceptions: None noted\n"
                    "Auditor: Northline Assurance LLC\n"
                    "Applicable to CMMC inheritance claims: Yes"
                ),
                "tags": ["audit", "soc2"],
                "evidence_type": "audit_report",
                "display_title": "SOC 2 Type II Report 2024",
                "evidence_version": "2024",
                "mappings": [("SOC2", "CC1.1")],
            },
        ]
        for item in original_seed:
            data = item["content"].encode("utf-8")
            ev = upload_evidence_file(
                name=item["name"],
                file_data=data,
                filename=item["filename"],
                tags=item["tags"],
                uploaded_by="demo@khestra.dev",
                mime_type=item["mime_type"],
                evidence_type=item.get("evidence_type", ""),
                display_title=item.get("display_title", ""),
                evidence_version=item.get("evidence_version", ""),
            )
            eid = ev.get("id", "")
            if eid:
                for fw_id, ctrl_id in item["mappings"]:
                    map_evidence(eid, fw_id, ctrl_id, mapped_by="demo@khestra.dev")

        # CMMC-specific seed evidence with real file content
        cmmc_seed = [
            {
                "name": "Entra ID Audit Log Configuration",
                "filename": "audit-log-config.pdf",
                "mime_type": "application/pdf",
                "content": (
                    "Microsoft Entra ID — Audit Log Configuration\n"
                    "Tenant: Trident Defense Systems GCC\n\n"
                    "Audit log retention: 180 days\n"
                    "Audited events: Sign-in, Role changes, Group membership, Directory changes\n"
                    "Forwarding: SIEM workspace via Azure Event Hub\n"
                    "Last verified: 2026-06-25\n"
                    "Compliant with AU.L2-3.3.1: Yes"
                ),
                "tags": ["audit", "cmmc"],
                "evidence_type": "config_export",
                "display_title": "Entra ID Audit Log Export",
                "evidence_version": "2026-06",
                "mappings": [("CMMC", "AU.L2-3.3.1"), ("CMMC", "AU.L2-3.3.2")],
            },
            {
                "name": "Conditional Access Policy Export",
                "filename": "ca-policy-export.pdf",
                "mime_type": "application/pdf",
                "content": (
                    "Microsoft Entra ID — Conditional Access Policies\n"
                    "Tenant: Trident Defense Systems GCC\n\n"
                    "CA-MFA-ALL-CUI: Require MFA for all CUI apps — Enabled\n"
                    "CA-MFA-PRIV: Require MFA for privileged roles — Enabled\n"
                    "CA-BLOCK-LEGACY: Block legacy authentication — Enabled\n"
                    "CA-COMPLIANT-DEVICE: Require compliant device — Enabled\n"
                    "Last modified: 2026-05-15\n"
                    "Compliant with AC.L2-3.1.1, AC.L2-3.1.3: Yes"
                ),
                "tags": ["access-control", "cmmc", "mfa"],
                "evidence_type": "config_export",
                "display_title": "Conditional Access Policy Export",
                "evidence_version": "2026-05",
                "mappings": [("CMMC", "AC.L2-3.1.1"), ("CMMC", "AC.L2-3.1.3")],
            },
            {
                "name": "Intune Compliance Report June-2026",
                "filename": "compliance-report-june-2026.pdf",
                "mime_type": "application/pdf",
                "content": (
                    "Microsoft Intune — Device Compliance Report\n"
                    "Organization: Trident Defense Systems\n"
                    "Report date: 2026-06-30\n\n"
                    "Total devices: 45\n"
                    "Compliant: 42 (93%)\n"
                    "Non-compliant: 3\n\n"
                    "BitLocker: 45/45 enabled\n"
                    "Defender: 45/45 active\n"
                    "OS patch: 42/45 current\n"
                    "Firewall: 45/45 enabled\n"
                    "Compliant with CM.L2-3.4.1: Yes"
                ),
                "tags": ["configuration", "cmmc", "intune"],
                "evidence_type": "config_export",
                "display_title": "Intune Device Compliance Report",
                "evidence_version": "2026-06",
                "mappings": [("CMMC", "CM.L2-3.4.1")],
            },
            {
                "name": "Incident Response Test Report Q2-2026",
                "filename": "ir-test-report-q2-2026.pdf",
                "mime_type": "application/pdf",
                "content": (
                    "TRIDENT DEFENSE SYSTEMS — Incident Response Tabletop Exercise\n"
                    "Date: 2026-05-20\n"
                    "Scenario: CUI data exfiltration via compromised SharePoint account\n\n"
                    "Participants: Sam Rivera (ISO), Alex Kim (SysAdmin), MSP SOC lead\n"
                    "Detection time: 4 minutes (Defender alert)\n"
                    "Containment time: 12 minutes\n"
                    "Eradication time: 45 minutes\n"
                    "Lessons learned: Improve communication template for DFARS 7012 notification\n"
                    "Compliant with IR.L2-3.6.1: Yes"
                ),
                "tags": ["incident-response", "cmmc"],
                "evidence_type": "audit_report",
                "display_title": "IR Tabletop Exercise Report",
                "evidence_version": "Q2-2026",
                "mappings": [("CMMC", "IR.L2-3.6.1"), ("CMMC", "IR.L2-3.6.3")],
            },
            {
                "name": "Vulnerability Scan Summary June-2026",
                "filename": "vuln-scan-summary-june-2026.pdf",
                "mime_type": "application/pdf",
                "content": (
                    "Tenable.io — Vulnerability Scan Summary\n"
                    "Target: Trident CUI Enclave\n"
                    "Scan date: 2026-06-15\n\n"
                    "Critical: 0\n"
                    "High: 2 (KB5048652 missing on 2 endpoints)\n"
                    "Medium: 5\n"
                    "Low: 16\n\n"
                    "Remediation: Patches approved for July maintenance window\n"
                    "Compliant with RA.L2-3.11.2: Yes"
                ),
                "tags": ["vulnerability", "cmmc", "scan"],
                "evidence_type": "scan_report",
                "display_title": "Monthly Vulnerability Scan Report",
                "evidence_version": "2026-06",
                "mappings": [("CMMC", "RA.L2-3.11.2")],
            },
        ]
        for item in cmmc_seed:
            data = item["content"].encode("utf-8")
            ev = upload_evidence_file(
                name=item["name"],
                file_data=data,
                filename=item["filename"],
                description=item.get("description", ""),
                tags=item["tags"],
                uploaded_by="demo@khestra.dev",
                mime_type=item["mime_type"],
                evidence_type=item.get("evidence_type", ""),
                display_title=item.get("display_title", ""),
                evidence_version=item.get("evidence_version", ""),
            )
            eid = ev.get("id", "")
            if eid:
                for fw_id, ctrl_id in item["mappings"]:
                    map_evidence(eid, fw_id, ctrl_id, mapped_by="demo@khestra.dev")

        db.commit()
    finally:
        db.close()


def list_evidence(
    framework_id: str | None = None,
    control_id: str | None = None,
    *,
    view: str = "latest",
    limit: int | None = None,
    offset: int = 0,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict]:
    """List evidence with growth-aware views.

    view:
      - latest: one collector row per (control, filename) + all manuals (default for Hub)
      - by_period: one collector row per (control, filename, period_covered day)
      - archived: soft-archived collector history only
      - all: every non-archived row (no dedupe)
    """
    view = (view or "latest").lower().strip()
    if view not in ("latest", "by_period", "archived", "all"):
        view = "latest"
    if framework_id:
        framework_id = canonical_framework_id(framework_id)

    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if framework_id:
            conditions.append("m.framework_id = ?")
            params.append(framework_id)
        if control_id:
            conditions.append("m.control_id = ?")
            params.append(control_id)
        if date_from:
            conditions.append("e.uploaded_at >= ?")
            params.append(date_from)
        if date_to:
            conditions.append("e.uploaded_at <= ?")
            params.append(date_to + "T23:59:59Z")

        if view == "archived":
            conditions.append("(e.archived_at IS NOT NULL AND e.archived_at != '')")
        else:
            conditions.append("(e.archived_at IS NULL OR e.archived_at = '')")

        if framework_id or control_id:
            sql = (
                "SELECT DISTINCT e.* FROM evidence e "
                "JOIN evidence_mappings m ON e.id = m.evidence_id WHERE "
                + " AND ".join(conditions)
                + " ORDER BY e.uploaded_at DESC, e.created_at DESC"
            )
            rows = db.execute(sql, params).fetchall()
        else:
            archived_cond = conditions[-1] if conditions else "(e.archived_at IS NULL OR e.archived_at = '')"
            sql = f"SELECT * FROM evidence e WHERE {archived_cond} ORDER BY e.uploaded_at DESC, e.created_at DESC"
            rows = db.execute(sql).fetchall()

        result = [_row_to_dict(r) for r in rows]
        eids = [item["id"] for item in result]
        if eids:
            placeholders = ",".join(["?"] * len(eids))
            mapping_rows = db.execute(
                f"SELECT * FROM evidence_mappings WHERE evidence_id IN ({placeholders})", eids
            ).fetchall()
            mapping_map: dict[str, list[dict]] = {}
            for mr in mapping_rows:
                mrow = dict(mr)
                mapping_map.setdefault(mrow["evidence_id"], []).append(mrow)
            for item in result:
                item["mappings"] = mapping_map.get(item["id"], [])
                if not item.get("period_covered"):
                    item["period_covered"] = _period_day(
                        item.get("evidence_version") or item.get("uploaded_at") or ""
                    )
        else:
            for item in result:
                item["mappings"] = []
                if not item.get("period_covered"):
                    item["period_covered"] = _period_day(
                        item.get("evidence_version") or item.get("uploaded_at") or ""
                    )
    finally:
        db.close()

    if view in ("latest", "by_period") and result:
        result = _dedupe_collector_view(result, view=view, control_id=control_id)

    if offset:
        result = result[offset:]
    if limit is not None and limit >= 0:
        result = result[:limit]
    return result


def _dedupe_collector_view(items: list[dict], *, view: str, control_id: str | None) -> list[dict]:
    """Keep manuals as-is; collapse collectors by period and/or filename."""
    manuals: list[dict] = []
    collectors: list[dict] = []
    for e in items:
        if _is_collector_row(e):
            collectors.append(e)
        else:
            manuals.append(e)

    seen: set[str] = set()
    kept: list[dict] = []
    for e in collectors:
        period = _period_day(e.get("period_covered") or e.get("evidence_version") or e.get("uploaded_at") or "")
        filename = e.get("filename") or ""
        if control_id:
            scope = control_id
        else:
            maps = e.get("mappings") or []
            scope = ",".join(sorted(f"{m.get('framework_id')}:{m.get('control_id')}" for m in maps)) or "_"
        if view == "latest":
            key = f"{scope}|{filename}"
        else:
            key = f"{scope}|{filename}|{period}"
        if key in seen:
            continue
        seen.add(key)
        kept.append(e)

    out = kept + manuals
    out.sort(key=lambda x: x.get("uploaded_at") or x.get("created_at") or "", reverse=True)
    return out


def prune_collector_periods(
    framework_id: str,
    control_id: str,
    filename: str,
    *,
    period_covered: str = "",
) -> dict:
    """After a collector attach: keep one row per period day; archive older periods.

    - Same day re-runs: keep newest for (control, filename, period), soft-archive rest.
    - Periods older than PERIOD_RETENTION_DAYS: soft-archive (queryable via view=archived).
    - Manual uploads are never touched.
    """
    from datetime import timedelta

    framework_id = canonical_framework_id(framework_id)
    period = _period_day(period_covered)
    now = _now()
    cutoff = (datetime.now(timezone.utc).date() - timedelta(days=PERIOD_RETENTION_DAYS)).isoformat()

    db = _get_db()
    same_period_archived = 0
    old_period_archived = 0
    try:
        rows = db.execute(
            """
            SELECT e.* FROM evidence e
            JOIN evidence_mappings m ON e.id = m.evidence_id
            WHERE m.framework_id = ? AND m.control_id = ? AND e.filename = ?
              AND (e.archived_at IS NULL OR e.archived_at = '')
            ORDER BY e.uploaded_at DESC, e.created_at DESC
            """,
            (framework_id, control_id, filename),
        ).fetchall()
        items = [_row_to_dict(r) for r in rows]
        collectors = [e for e in items if _is_collector_row(e)]

        by_period: dict[str, list[dict]] = {}
        for e in collectors:
            p = _period_day(e.get("period_covered") or e.get("evidence_version") or e.get("uploaded_at") or "") or period
            by_period.setdefault(p, []).append(e)

        for p, group in by_period.items():
            for dup in group[1:]:
                db.execute(
                    "UPDATE evidence SET archived_at = ? WHERE id = ? AND (archived_at IS NULL OR archived_at = '')",
                    (now, dup["id"]),
                )
                same_period_archived += 1
            if p and p < cutoff:
                keep = group[0]
                db.execute(
                    "UPDATE evidence SET archived_at = ? WHERE id = ? AND (archived_at IS NULL OR archived_at = '')",
                    (now, keep["id"]),
                )
                old_period_archived += 1

        db.commit()
    finally:
        db.close()
    return {
        "same_period_archived": same_period_archived,
        "old_period_archived": old_period_archived,
        "period_retention_days": PERIOD_RETENTION_DAYS,
        "cutoff": cutoff,
    }


def purge_expired_archives(older_than_days: int | None = None, hard_delete: bool = False) -> dict:
    """Purge soft-archived collector evidence past ARCHIVE_DELETE_DAYS.

    By default moves files to a _trash directory so they can be recovered.
    Pass hard_delete=True to permanently delete files and DB rows.
    Trash files older than 30 days are deleted automatically.
    """
    from datetime import timedelta

    days = older_than_days if older_than_days is not None else ARCHIVE_DELETE_DAYS
    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    deleted = 0
    db = _get_db()
    trash_dir = _files_dir() / "_trash"
    try:
        rows = db.execute(
            """
            SELECT id, filename FROM evidence
            WHERE archived_at IS NOT NULL AND archived_at != '' AND archived_at < ?
            """,
            (cutoff,),
        ).fetchall()
        for row in rows:
            eid = row["id"]
            ext = Path(row["filename"] or "").suffix
            stored = _files_dir() / f"{eid}{ext}"
            if stored.exists():
                if hard_delete:
                    try:
                        stored.unlink()
                    except OSError:
                        pass
                else:
                    trash_dir.mkdir(parents=True, exist_ok=True)
                    stored.rename(trash_dir / f"{eid}{ext}")
            db.execute("DELETE FROM evidence_mappings WHERE evidence_id = ?", (eid,))
            db.execute("DELETE FROM evidence WHERE id = ?", (eid,))
            deleted += 1
        db.commit()
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        # cleanup trash older than 30 days
        if trash_dir.exists():
            trash_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            for f in trash_dir.iterdir():
                if f.is_file():
                    try:
                        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                        if mtime < trash_cutoff:
                            f.unlink()
                    except OSError:
                        pass
    finally:
        db.close()
    return {"deleted": deleted, "cutoff": cutoff, "archive_delete_days": days, "hard_delete": hard_delete}


def collector_period_summary(
    framework_id: str,
    control_id: str,
) -> list[dict]:
    """Slim per-filename period trail for Control Detail (non-archived by_period)."""
    items = list_evidence(framework_id=framework_id, control_id=control_id, view="by_period")
    by_fn: dict[str, list[dict]] = {}
    for e in items:
        if not _is_collector_row(e):
            continue
        fn = e.get("filename") or ""
        by_fn.setdefault(fn, []).append(e)

    out: list[dict] = []
    for fn, group in by_fn.items():
        periods = []
        for e in group:
            periods.append(
                {
                    "period_covered": e.get("period_covered")
                    or _period_day(e.get("evidence_version") or e.get("uploaded_at") or ""),
                    "hub_id": e.get("id"),
                    "upload_date": e.get("uploaded_at"),
                    "status": e.get("auto_status") or "",
                    "sha256": e.get("sha256") or "",
                    "display_title": e.get("display_title") or e.get("name") or fn,
                }
            )
        periods.sort(key=lambda p: p.get("period_covered") or "", reverse=True)
        out.append(
            {
                "filename": fn,
                "count": len(periods),
                "oldest": periods[-1]["period_covered"] if periods else "",
                "newest": periods[0]["period_covered"] if periods else "",
                "periods": periods,
            }
        )
    out.sort(key=lambda x: x.get("newest") or "", reverse=True)
    for entry in out:
        entry["coverage"] = _coverage_analysis(entry)
    return out


def _coverage_analysis(entry: dict) -> dict:
    """Analyze coverage continuity for a per-filename period trail."""
    periods = entry.get("periods", [])
    sorted_dates = sorted(
        p["period_covered"] for p in periods if p.get("period_covered")
    )
    if len(sorted_dates) < 2:
        return {
            "total_days": len(sorted_dates),
            "days_collected": len(sorted_dates),
            "gaps": [],
            "is_continuous": True,
        }
    gaps = []
    for i in range(1, len(sorted_dates)):
        from datetime import datetime as _dt
        prev = _dt.strptime(sorted_dates[i - 1], "%Y-%m-%d")
        curr = _dt.strptime(sorted_dates[i], "%Y-%m-%d")
        diff = (curr - prev).days
        if diff > 1:
            gaps.append({
                "from": sorted_dates[i - 1],
                "to": sorted_dates[i],
                "days_missed": diff - 1,
            })
    return {
        "total_days": (datetime.strptime(sorted_dates[-1], "%Y-%m-%d") - datetime.strptime(sorted_dates[0], "%Y-%m-%d")).days + 1,
        "days_collected": len(sorted_dates),
        "gaps": gaps,
        "is_continuous": len(gaps) == 0,
    }


def check_coverage_gaps(framework_id: str, control_id: str, *, days: int = 90) -> dict:
    """Check whether evidence for a control covers N contiguous days.

    Returns coverage analysis across all filenames combined.
    """
    summary = collector_period_summary(framework_id, control_id)
    all_periods: set[str] = set()
    for entry in summary:
        for p in entry.get("periods", []):
            pc = p.get("period_covered")
            if pc:
                all_periods.add(pc)
    sorted_dates = sorted(all_periods)
    if len(sorted_dates) < 2:
        return {
            "framework_id": framework_id,
            "control_id": control_id,
            "requested_days": days,
            "span_days": 0,
            "days_collected": len(sorted_dates),
            "gaps": [],
            "is_continuous": False,
        }
    from datetime import timedelta as _td
    span_end = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
    span_start = span_end - _td(days=days)
    gaps = []
    in_window = [d for d in sorted_dates if datetime.strptime(d, "%Y-%m-%d") >= span_start]
    for i in range(1, len(in_window)):
        prev = datetime.strptime(in_window[i - 1], "%Y-%m-%d")
        curr = datetime.strptime(in_window[i], "%Y-%m-%d")
        diff = (curr - prev).days
        if diff > 1:
            gaps.append({
                "from": in_window[i - 1],
                "to": in_window[i],
                "days_missed": diff - 1,
            })
    return {
        "framework_id": framework_id,
        "control_id": control_id,
        "requested_days": days,
        "span_days": (datetime.strptime(in_window[-1], "%Y-%m-%d") - datetime.strptime(in_window[0], "%Y-%m-%d")).days + 1 if len(in_window) >= 2 else 0,
        "days_collected": len(in_window),
        "gaps": gaps,
        "is_continuous": len(gaps) == 0 and len(in_window) >= days,
    }


def get_evidence(eid: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM evidence WHERE id = ?", (eid,)).fetchone()
        if not row:
            return None
        item = _row_to_dict(row)
        item["mappings"] = _get_mappings(eid, db)
        return item
    finally:
        db.close()


def _get_mappings(eid: str, db: sqlite3.Connection | None = None) -> list[dict]:
    close = db is None
    if db is None:
        db = _get_db()
    try:
        rows = db.execute("SELECT * FROM evidence_mappings WHERE evidence_id = ?", (eid,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        if close:
            db.close()


def create_evidence(name: str, filename: str = "", description: str = "", tags: list[str] | None = None, uploaded_by: str = "", valid_until: str = "") -> dict:
    eid = uuid4().hex
    now = _now()
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO evidence (id, name, filename, description, tags, uploaded_by, uploaded_at, created_at, valid_until) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (eid, name, filename, description, json.dumps(tags or []), uploaded_by, now, now, valid_until),
        )
        db.commit()
    finally:
        db.close()
    return get_evidence(eid) or {}


_ALLOWED_EXTENSIONS = frozenset({".pdf", ".png", ".jpg", ".jpeg", ".json", ".conf", ".txt", ".csv", ".docx", ".xlsx", ".md", ".log"})
_MAX_UPLOAD_MB = 50


def upload_evidence_file(name: str, file_data: bytes, filename: str, description: str = "", tags: list[str] | None = None, uploaded_by: str = "", mime_type: str = "", evidence_type: str = "", display_title: str = "", evidence_version: str = "", valid_until: str = "", auto_status: str = "", auto_summary: str = "", review_status: str = "pending", period_covered: str = "") -> dict:
    ext = Path(filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValueError(f"Extension '{ext}' not allowed")
    if len(file_data) > _MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"File exceeds {_MAX_UPLOAD_MB} MB limit")
    guessed_type, _ = mimetypes.guess_type(filename)
    if guessed_type and mime_type and guessed_type != mime_type:
        mime_type = guessed_type
    elif guessed_type and not mime_type:
        mime_type = guessed_type
    eid = uuid4().hex
    now = _now()
    sha = hashlib.sha256(file_data).hexdigest()
    file_size = len(file_data)
    ext = Path(filename).suffix
    stored_name = f"{eid}{ext}"
    tmp = _files_dir() / f".{stored_name}.tmp"
    dest = _files_dir() / stored_name
    tmp.write_bytes(file_data)
    period = _period_day(period_covered or evidence_version or now)
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO evidence (id, name, filename, description, tags, uploaded_by, uploaded_at, sha256, file_size, mime_type, created_at, evidence_type, display_title, evidence_version, valid_until, auto_status, auto_summary, review_status, reviewer, reviewed_at, period_covered, archived_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (eid, name, filename, description, json.dumps(tags or []), uploaded_by, now, sha, file_size, mime_type, now, evidence_type, display_title or name, evidence_version or period, valid_until, auto_status, auto_summary, review_status, "system:collector" if review_status == "approved" else "", now if review_status == "approved" else "", period, ""),
        )
        db.commit()
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise
    try:
        os.replace(tmp, dest)
    except Exception:
        # rollback DB if file rename fails after commit
        db2 = _get_db()
        try:
            db2.execute("DELETE FROM evidence WHERE id = ?", (eid,))
            db2.commit()
        finally:
            db2.close()
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise
    finally:
        db.close()
    return get_evidence(eid) or {}


def delete_evidence(eid: str) -> bool:
    db = _get_db()
    try:
        row = db.execute("SELECT id, filename FROM evidence WHERE id = ?", (eid,)).fetchone()
        if not row:
            return False
        db.execute("DELETE FROM evidence WHERE id = ?", (eid,))
        db.execute("DELETE FROM evidence_mappings WHERE evidence_id = ?", (eid,))
        db.commit()
        ext = Path(row["filename"]).suffix
        stored = _files_dir() / f"{eid}{ext}"
        if stored.exists():
            stored.unlink()
    finally:
        db.close()
    return True


def get_evidence_file_path(eid: str) -> Path | None:
    db = _get_db()
    try:
        row = db.execute("SELECT filename FROM evidence WHERE id = ?", (eid,)).fetchone()
        if not row:
            return None
        ext = Path(row["filename"]).suffix
        path = _files_dir() / f"{eid}{ext}"
        return path if path.exists() else None
    finally:
        db.close()


def resolve_evidence_bytes_from_hub(
    framework_id: str,
    control_id: str,
    filename: str,
) -> bytes | None:
    """Read a workspace evidence entry's bytes from the hub store.

    Fallback for workspace entries that carry metadata but no retrievable
    bytes (data_bytes stripped / restored_evidence empty) — collector
    attachments live in the hub as `{eid}{ext}` files. Matches the latest
    hub row by (framework, control, filename) and returns its file bytes.
    """
    if not filename:
        return None
    try:
        rows = list_evidence(framework_id=framework_id, control_id=control_id, view="latest") or []
    except Exception:
        return None
    for row in rows:
        if row.get("filename") != filename:
            continue
        path = get_evidence_file_path(str(row.get("id") or ""))
        if path is None:
            continue
        try:
            return path.read_bytes()
        except OSError:
            continue
    return None


def review_evidence(eid: str, status: str, reviewer: str = "", comment: str = "") -> dict | None:
    valid = ("approved", "rejected", "pending")
    if status not in valid:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid}")
    db = _get_db()
    try:
        row = db.execute("SELECT id FROM evidence WHERE id = ?", (eid,)).fetchone()
        if not row:
            return None
        db.execute(
            "UPDATE evidence SET review_status = ?, reviewer = ?, review_comment = ?, reviewed_at = ? WHERE id = ?",
            (status, reviewer, comment, _now(), eid),
        )
        db.commit()
    finally:
        db.close()
    return get_evidence(eid)


def bulk_review_evidence(eids: list[str], status: str, reviewer: str = "", comment: str = "") -> int:
    valid = ("approved", "rejected", "pending")
    if status not in valid:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid}")
    if not eids:
        return 0
    db = _get_db()
    try:
        placeholders = ",".join("?" for _ in eids)
        cur = db.execute(
            f"UPDATE evidence SET review_status = ?, reviewer = ?, review_comment = ?, reviewed_at = ? WHERE id IN ({placeholders})",
            [status, reviewer, comment, _now()] + eids,
        )
        db.commit()
        return cur.rowcount
    finally:
        db.close()


def map_evidence(eid: str, framework_id: str, control_id: str, mapped_by: str = "") -> dict:
    framework_id = canonical_framework_id(framework_id)
    db = _get_db()
    try:
        existing = db.execute(
            "SELECT id FROM evidence_mappings WHERE evidence_id = ? AND framework_id = ? AND control_id = ?",
            (eid, framework_id, control_id),
        ).fetchone()
        if existing:
            return {"id": existing["id"], "evidence_id": eid, "framework_id": framework_id, "control_id": control_id, "status": "already_mapped"}
        mid = uuid4().hex
        now = _now()
        db.execute(
            "INSERT INTO evidence_mappings (id, evidence_id, framework_id, control_id, mapped_at, mapped_by) VALUES (?, ?, ?, ?, ?, ?)",
            (mid, eid, framework_id, control_id, now, mapped_by),
        )
        db.commit()
    finally:
        db.close()
    return {"id": mid, "evidence_id": eid, "framework_id": framework_id, "control_id": control_id, "status": "created"}


def get_stats() -> dict:
    db = _get_db()
    try:
        total_evidence = db.execute("SELECT COUNT(*) as c FROM evidence").fetchone()["c"]
        total_mappings = db.execute("SELECT COUNT(*) as c FROM evidence_mappings").fetchone()["c"]
        total_file_size = db.execute("SELECT COALESCE(SUM(file_size), 0) as s FROM evidence").fetchone()["s"]
        review_counts = {
            r["review_status"]: r["c"]
            for r in db.execute("SELECT review_status, COUNT(*) as c FROM evidence GROUP BY review_status").fetchall()
        }
        fw_rows = db.execute(
            "SELECT m.framework_id, COUNT(DISTINCT m.evidence_id) as evidence_count, COUNT(DISTINCT m.control_id) as control_count, COUNT(*) as mapping_count FROM evidence_mappings m GROUP BY m.framework_id"
        ).fetchall()
        by_framework = {}
        for r in fw_rows:
            by_framework[r["framework_id"]] = {
                "evidence_count": r["evidence_count"],
                "control_count": r["control_count"],
                "mapping_count": r["mapping_count"],
            }
        recent = db.execute("SELECT id, name, filename, uploaded_at, uploaded_by FROM evidence ORDER BY created_at DESC LIMIT 10").fetchall()
        open_requests = db.execute("SELECT COUNT(*) as c FROM evidence_requests WHERE status = 'open'").fetchone()["c"]
        return {
            "total_evidence": total_evidence,
            "total_mappings": total_mappings,
            "total_file_size": total_file_size,
            "open_requests": open_requests,
            "by_review_status": dict(review_counts),
            "by_framework": by_framework,
            "recent_uploads": [dict(r) for r in recent],
        }
    finally:
        db.close()


def get_freshness_stats(framework_id: str | None = None) -> dict:
    db = _get_db()
    try:
        if framework_id:
            framework_id = canonical_framework_id(framework_id)
            rows = db.execute(
                "SELECT e.uploaded_at, e.valid_until FROM evidence e JOIN evidence_mappings m ON e.id = m.evidence_id WHERE m.framework_id = ?",
                (framework_id,),
            ).fetchall()
        else:
            rows = db.execute("SELECT uploaded_at, valid_until FROM evidence").fetchall()
        counts = {"fresh": 0, "stale": 0, "expired": 0, "never": 0, "unknown": 0}
        for r in rows:
            f = _freshness_score(r["uploaded_at"] or "", r["valid_until"] or "")
            counts[f] = counts.get(f, 0) + 1
        return counts
    finally:
        db.close()


def get_overdue_requests(framework_id: str | None = None) -> list[dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    db = _get_db()
    try:
        if framework_id:
            framework_id = canonical_framework_id(framework_id)
            rows = db.execute(
                "SELECT * FROM evidence_requests WHERE status = 'open' AND due_date != '' AND due_date < ? AND framework_id = ? ORDER BY due_date ASC",
                (today, framework_id),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM evidence_requests WHERE status = 'open' AND due_date != '' AND due_date < ? ORDER BY due_date ASC",
                (today,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def _csv_safe(val: str) -> str:
    if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + val
    return val


def export_audit_package(
    framework_id: str | None = None,
    *,
    control_id: str | None = None,
    include_archived: bool = False,
) -> bytes:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        fw_filter = canonical_framework_id(framework_id.strip()) if framework_id and framework_id.strip() else None
        ctrl_filter = control_id.strip().upper() if control_id and control_id.strip() else None
        if fw_filter:
            conditions.append("m.framework_id = ?")
            params.append(fw_filter)
        if ctrl_filter:
            conditions.append("m.control_id = ?")
            params.append(ctrl_filter)
        archived_cond = "(e.archived_at IS NULL OR e.archived_at = '')"
        if conditions or ctrl_filter:
            sql = "SELECT DISTINCT e.* FROM evidence e JOIN evidence_mappings m ON e.id = m.evidence_id"
            if ctrl_filter and not any("control_id" in c for c in conditions):
                conditions.append("m.control_id = ?")
                params.append(ctrl_filter)
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
                if not include_archived:
                    sql += " AND " + archived_cond
            else:
                sql += " WHERE " + archived_cond
            sql += " ORDER BY e.created_at DESC"
            rows = db.execute(sql, params).fetchall()
        elif include_archived:
            rows = db.execute("SELECT * FROM evidence ORDER BY created_at DESC").fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM evidence WHERE archived_at IS NULL OR archived_at = '' ORDER BY created_at DESC"
            ).fetchall()
        items = [_row_to_dict(r) for r in rows]
        for item in items:
            item["mappings"] = _get_mappings(item["id"], db)
            if not item.get("period_covered"):
                item["period_covered"] = _period_day(
                    item.get("evidence_version") or item.get("uploaded_at") or ""
                )
        # Prefer one row per collection period so ZIPs don't balloon with same-day re-runs
        items = _dedupe_collector_view(items, view="by_period", control_id=None)
    finally:
        db.close()

    buf = io.BytesIO()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest = {
            "generated_at": now,
            "framework_filter": framework_id or "all",
            "control_filter": control_id or "all",
            "total_evidence": len(items),
            "items": [
                {
                    "id": e["id"],
                    "name": e["name"],
                    "filename": e["filename"],
                    "sha256": e["sha256"],
                    "file_size": e["file_size"],
                    "mime_type": e["mime_type"],
                    "uploaded_by": e["uploaded_by"],
                    "uploaded_at": e["uploaded_at"],
                    "review_status": e.get("review_status", "pending"),
                    "source_check": e.get("source_check", ""),
                    "provider": e.get("provider", ""),
                    "mappings": [
                        {"framework_id": m["framework_id"], "control_id": m["control_id"]}
                        for m in (e.get("mappings") or [])
                    ],
                }
                for e in items
            ],
        }
        total_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        manifest["manifest_hash"] = total_hash
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf, quoting=csv.QUOTE_ALL)
        writer.writerow(["evidence_id", "name", "filename", "sha256", "source_check", "provider", "framework_id", "control_id", "uploaded_at", "review_status"])
        for e in items:
            for m in (e.get("mappings") or []):
                writer.writerow([
                    _csv_safe(e["id"]),
                    _csv_safe(e["name"]),
                    _csv_safe(e["filename"]),
                    _csv_safe(e.get("sha256", "")),
                    _csv_safe(e.get("source_check", "")),
                    _csv_safe(e.get("provider", "")),
                    _csv_safe(m["framework_id"]),
                    _csv_safe(m["control_id"]),
                    _csv_safe(e.get("uploaded_at", "")),
                    _csv_safe(e.get("review_status", "pending")),
                ])
        zf.writestr("evidence_index.csv", csv_buf.getvalue())

        files_dir = _files_dir()
        files_included = 0
        for e in items:
            ext = Path(e["filename"]).suffix
            src = files_dir / f"{e['id']}{ext}"
            if src.exists():
                arcname = f"evidence/{e['id']}{ext}"
                zf.write(str(src), arcname)
                files_included += 1

        # ── Auditor-ready extras ─────────────────────────────────────────
        # evidence.json: control-mapping-centric machine-readable view.
        by_fw: dict = {}
        for e in items:
            for m in (e.get("mappings") or []):
                fw = m["framework_id"]
                ctrl = m["control_id"]
                by_fw.setdefault(fw, {}).setdefault(ctrl, []).append(
                    {"evidence_id": e["id"], "name": e["name"], "filename": e["filename"], "sha256": e["sha256"]}
                )
        evidence_json = {
            "generated_at": now,
            "framework_filter": framework_id or "all",
            "control_filter": control_id or "all",
            "mappings": [
                {
                    "framework_id": fw,
                    "control_id": ctrl,
                    "evidence": entries,
                }
                for fw, controls in by_fw.items()
                for ctrl, entries in controls.items()
            ],
        }
        zf.writestr("evidence.json", json.dumps(evidence_json, indent=2))

        # console-urls.txt: direct links to the relevant cloud console per
        # source check, so auditors/engineers can verify settings manually.
        try:
            try:
                from collectors.remediation import console_url_for
            except ImportError:
                # Evidence package lives at packages/evidence (sibling of this
                # package) — make it importable when not already on sys.path.
                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evidence"))
                from collectors.remediation import console_url_for

            console_lines: list[str] = [
                "KHESTRA EVIDENCE PACKAGE — CONSOLE LINKS",
                "Direct links to the cloud console for each collected check.",
                "Replace <ORG>/<ACCOUNT> placeholders with your own.",
                "",
            ]
            seen: set = set()
            for e in items:
                src = (e.get("source_check") or "").strip()
                if not src or src in seen:
                    continue
                url = console_url_for(src)
                if url:
                    seen.add(src)
                    console_lines.append(f"{src}  →  {url}")
            if console_lines[4:]:
                zf.writestr("console-urls.txt", "\n".join(console_lines) + "\n")
        except Exception:
            pass

        # grc-findings.json: export collected checks in the GRC Engineering Club
        # finding.schema.json v1.0.0 contract so the package is consumable by
        # external GRC tooling (gap assessments, crosswalks, OSCAL pipelines).
        try:
            try:
                from collectors.importers.grc_finding import checks_to_grc_document
            except ImportError:
                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evidence"))
                from collectors.importers.grc_finding import checks_to_grc_document

            grc_evals: list = []
            for e in items:
                src = (e.get("source_check") or "").strip()
                if not src:
                    continue
                for m in (e.get("mappings") or []):
                    grc_evals.append({
                        "control_framework": m["framework_id"],
                        "control_id": m["control_id"],
                        "status": "pass" if e.get("auto_status") == "pass" else "fail",
                        "message": e.get("name") or src,
                        "remediation": {"summary": e.get("description") or "", "automation": "manual"},
                    })
            if grc_evals:
                doc = {
                    "schema_version": "1.0.0",
                    "source": "khestra",
                    "source_version": "0.1.0",
                    "run_id": now,
                    "collected_at": now,
                    "resource": {"type": "evidence_batch", "id": "khestra-evidence-hub"},
                    "evaluations": grc_evals,
                }
                zf.writestr("grc-findings.json", json.dumps(doc, indent=2))
        except Exception:
            pass

        # Executive summary PDF (best-effort; never fails the export).
        try:
            from pdf_export.engine import generate_pdf

            fw_counts: dict = {}
            ctrl_counts: dict = {}
            for e in items:
                for m in (e.get("mappings") or []):
                    fw_counts[m["framework_id"]] = fw_counts.get(m["framework_id"], 0) + 1
                    ctrl_counts[m["control_id"]] = ctrl_counts.get(m["control_id"], 0) + 1
            pdf_sections = [
                {"type": "heading", "content": "Evidence Package — Executive Summary", "level": 0},
                {"type": "kv", "key": "Generated", "value": now},
                {"type": "kv", "key": "Framework filter", "value": framework_id or "all"},
                {"type": "kv", "key": "Control filter", "value": control_id or "all"},
                {"type": "kv", "key": "Evidence items", "value": str(len(items))},
                {"type": "kv", "key": "Files included", "value": str(files_included)},
                {"type": "kv", "key": "Manifest hash", "value": total_hash},
                {"type": "page_break"},
                {"type": "heading", "content": "Evidence by Framework", "level": 1},
            ]
            for fw, cnt in sorted(fw_counts.items()):
                pdf_sections.append({"type": "kv", "key": fw, "value": f"{cnt} evidence item(s)"})
            pdf_sections.append({"type": "page_break"})
            pdf_sections.append({"type": "heading", "content": "Covered Controls", "level": 1})
            for ctrl, cnt in sorted(ctrl_counts.items()):
                pdf_sections.append({"type": "kv", "key": ctrl, "value": f"{cnt} evidence item(s)"})
            zf.writestr("00-EXECUTIVE-SUMMARY.pdf", generate_pdf("Evidence Package Summary", pdf_sections))
        except Exception:
            pass

        # Open findings + remediation scripts (best-effort).
        try:
            from findings.store import list_findings

            open_findings = [
                f for f in list_findings(status="open") if f.get("status") == "open"
            ]
            zf.writestr(
                "findings.json",
                json.dumps(
                    {
                        "generated_at": now,
                        "open_findings": [
                            {
                                "id": f["id"],
                                "title": f["title"],
                                "description": f.get("description", ""),
                                "remediation": f.get("remediation", ""),
                                "severity": f.get("severity", "medium"),
                                "framework": f.get("framework", ""),
                                "control_ids": f.get("control_ids", []),
                            }
                            for f in open_findings
                        ],
                    },
                    indent=2,
                ),
            )
            for f in open_findings:
                if not f.get("remediation"):
                    continue
                slug = re.sub(r"[^a-z0-9]+", "-", f["title"].lower()).strip("-")[:50] or f["id"]
                script = (
                    "#!/usr/bin/env bash\n"
                    "# Khestra remediation script\n"
                    f"# Finding: {f['title']}\n"
                    f"# Severity: {f.get('severity', 'medium')}\n"
                    f"# Controls: {', '.join(f.get('control_ids') or [])}\n"
                    "#\n"
                    "# Steps to remediate:\n"
                )
                for line in f["remediation"].splitlines() or [f["remediation"]]:
                    script += f"#   {line}\n"
                zf.writestr(f"remediation_scripts/{slug}.sh", script)
        except Exception:
            pass

        zf.writestr(
            "readme.txt",
            "KHESTRA EVIDENCE PACKAGE — FOR THE AUDITOR\n"
            "==========================================\n"
            "\n"
            "This ZIP contains the evidence your organization collected in Khestra for\n"
            "the compliance framework(s) listed below.\n"
            "\n"
            "CONTENTS\n"
            "--------\n"
            "  readme.txt                 These instructions\n"
            "  00-EXECUTIVE-SUMMARY.pdf   High-level summary (counts, coverage)\n"
            "  manifest.json              Machine-readable manifest with per-item hashes\n"
            "  evidence.json              Control-to-evidence mapping (machine-readable)\n"
            "  evidence_index.csv         Flat index of every evidence item\n"
            "  findings.json              Open findings (machine-readable)\n"
            "  remediation_scripts/       One script per open finding with fix steps\n"
            "  console-urls.txt           Direct links to cloud consoles per check\n"
            "  grc-findings.json          Checks in the GRC finding.schema.json contract\n"
            "  evidence/                  The evidence files themselves\n"
            "\n"
            "HOW TO VERIFY\n"
            "-------------\n"
            "1. Open 00-EXECUTIVE-SUMMARY.pdf for the headline numbers.\n"
            "2. Use manifest.json to verify integrity: each item lists its sha256.\n"
            "   Recompute:  shasum -a 256 evidence/<filename>\n"
            "3. Cross-reference evidence.json against the controls in scope:\n"
            "   every control listed there has at least one evidence item.\n"
            "4. remediation_scripts/ describes how open findings will be closed.\n"
            "\n"
            f"Generated: {now}\n"
            f"Framework filter: {framework_id or 'all'}\n"
            f"Control filter: {control_id or 'all'}\n"
            f"Total evidence: {len(items)}\n"
            f"Files included: {files_included}\n"
            f"Manifest hash: {total_hash}\n",
        )
    return buf.getvalue()


def list_requests(framework_id: str | None = None, control_id: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if framework_id:
            conditions.append("framework_id = ?")
            params.append(canonical_framework_id(framework_id))
        if control_id:
            conditions.append("control_id = ?")
            params.append(control_id)
        sql = "SELECT * FROM evidence_requests"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC"
        return [dict(r) for r in db.execute(sql, params).fetchall()]
    finally:
        db.close()


def create_request(framework_id: str = "", control_id: str = "", title: str = "", description: str = "", assigned_to: str = "", due_date: str = "") -> dict:
    eid = uuid4().hex
    now = _now()
    db = _get_db()
    try:
        db.execute(
            "INSERT INTO evidence_requests (id, framework_id, control_id, title, description, assigned_to, due_date, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)",
            (eid, canonical_framework_id(framework_id), control_id, title, description, assigned_to, due_date, now, now),
        )
        db.commit()
    finally:
        db.close()
    return get_request(eid) or {}


def get_request(request_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM evidence_requests WHERE id = ?", (request_id,)).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def patch_request(request_id: str, status: str | None = None, assigned_to: str | None = None, due_date: str | None = None) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT id FROM evidence_requests WHERE id = ?", (request_id,)).fetchone()
        if not row:
            return None
        updates: list[str] = []
        params: list[str] = []
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if assigned_to is not None:
            updates.append("assigned_to = ?")
            params.append(assigned_to)
        if due_date is not None:
            updates.append("due_date = ?")
            params.append(due_date)
        if updates:
            updates.append("updated_at = ?")
            params.append(_now())
            params.append(request_id)
            db.execute(f"UPDATE evidence_requests SET {', '.join(updates)} WHERE id = ?", params)
            db.commit()
    finally:
        db.close()
    return get_request(request_id)


def delete_request(request_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM evidence_requests WHERE id = ?", (request_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


def unmap_evidence(eid: str, framework_id: str, control_id: str) -> bool:
    framework_id = canonical_framework_id(framework_id)
    db = _get_db()
    try:
        cur = db.execute(
            "DELETE FROM evidence_mappings WHERE evidence_id = ? AND framework_id = ? AND control_id = ?",
            (eid, framework_id, control_id),
        )
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


# ─── Chain of Custody ──────────────────────────────


def log_access(eid: str, action: str, performed_by: str = "",
               metadata: dict | None = None, ip_address: str = "") -> dict:
    db = _get_db()
    try:
        rec_id = uuid4().hex[:12]
        db.execute(
            "INSERT INTO evidence_access_log (id, evidence_id, action, performed_by, performed_at, ip_address, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (rec_id, eid, action, performed_by, _now(), ip_address, json.dumps(metadata or {})),
        )
        db.commit()
        return {"id": rec_id, "action": action, "performed_by": performed_by, "performed_at": _now()}
    finally:
        db.close()


def get_evidence_history(eid: str) -> list[dict]:
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT * FROM evidence_access_log WHERE evidence_id = ? ORDER BY performed_at ASC",
            (eid,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


# ─── Multi-Party Review ────────────────────────────


def assign_reviewer(eid: str, reviewer: str, due_date: str = "") -> dict | None:
    db = _get_db()
    try:
        db.execute(
            "UPDATE evidence SET reviewer = ?, review_due_date = ?, review_began_at = ? WHERE id = ? AND review_status = 'pending'",
            (reviewer, due_date, _now(), eid),
        )
        db.commit()
        return get_evidence(eid)
    finally:
        db.close()


def request_remediation(eid: str, instructions: str) -> dict | None:
    db = _get_db()
    try:
        db.execute(
            "UPDATE evidence SET review_status = 'remediated', remediation_instructions = ?, updated_at = ? WHERE id = ?",
            (instructions, _now(), eid),
        )
        db.commit()
        return get_evidence(eid)
    finally:
        db.close()


# ─── Evidence Sufficiency ──────────────────────────


def get_sufficiency_score(framework_id: str, control_id: str) -> dict:
    framework_id = canonical_framework_id(framework_id)
    db = _get_db()
    try:
        rows = db.execute(
            "SELECT e.* FROM evidence e "
            "JOIN evidence_mappings m ON e.id = m.evidence_id "
            "WHERE m.framework_id = ? AND m.control_id = ?",
            (framework_id, control_id),
        ).fetchall()
        items = [_row_to_dict(r) for r in rows]
        count = len(items)
        if count == 0:
            return {"score": 0, "level": "insufficient", "count": 0, "breakdown": {}}

        auto_count = sum(1 for it in items if str(it.get("uploaded_by", "")).startswith("collector:"))
        manual_count = count - auto_count
        fresh_count = sum(1 for it in items if _freshness_score(it.get("uploaded_at", ""), it.get("valid_until", "")) == "fresh")
        stale_count = sum(1 for it in items if _freshness_score(it.get("uploaded_at", ""), it.get("valid_until", "")) == "stale")
        approved_count = sum(1 for it in items if it.get("review_status") == "approved")
        pending_count = sum(1 for it in items if it.get("review_status") == "pending")

        count_score = min(count * 10, 40)
        source_score = 30 if auto_count > manual_count else (15 if auto_count > 0 else 5)
        fresh_score = min(fresh_count * 10, 20)
        review_score = min(approved_count * 5, 10)

        score = min(count_score + source_score + fresh_score + review_score, 100)
        level = "comprehensive" if score >= 80 else ("adequate" if score >= 50 else ("minimal" if score >= 25 else "insufficient"))

        return {
            "score": score,
            "level": level,
            "count": count,
            "breakdown": {
                "count": count_score,
                "source": source_score,
                "freshness": fresh_score,
                "review": review_score,
                "auto_count": auto_count,
                "manual_count": manual_count,
                "fresh_count": fresh_count,
                "stale_count": stale_count,
                "approved_count": approved_count,
                "pending_count": pending_count,
            },
        }
    finally:
        db.close()


def get_sufficiency_matrix(framework_id: str) -> dict:
    framework_id = canonical_framework_id(framework_id)
    db = _get_db()
    try:
        rows = db.execute("SELECT DISTINCT control_id FROM evidence_mappings WHERE framework_id = ?", (framework_id,)).fetchall()
        controls = {}
        for row in rows:
            cid = row["control_id"]
            controls[cid] = get_sufficiency_score(framework_id, cid)
        return {"framework_id": framework_id, "controls": controls}
    finally:
        db.close()


# ─── Cross-Framework Reuse ─────────────────────────


def get_cross_framework_suggestions(eid: str) -> list[dict]:
    """Find other framework criteria this evidence could cover."""
    ev = get_evidence(eid)
    if not ev:
        return []
    try:
        from collectors.framework_mapping import CHECK_TO_FRAMEWORKS
    except ImportError:
        return []
    db = _get_db()
    try:
        existing = db.execute(
            "SELECT framework_id, control_id FROM evidence_mappings WHERE evidence_id = ?",
            (eid,),
        ).fetchall()
        existing_set = {(r["framework_id"], r["control_id"]) for r in existing}

        suggestions = []
        for check_id, fw_map in CHECK_TO_FRAMEWORKS.items():
            for fw, controls in fw_map.items():
                fw_ev = canonical_framework_id(fw)
                for ctrl in controls:
                    if (fw_ev, ctrl) in existing_set:
                        continue
                    for (efw, _ectrl) in existing_set:
                        if efw != fw_ev and ctrl in fw_map.get(CROSSWALK_KEY_FOR_EVIDENCE_ID.get(efw, ""), []):
                            suggestions.append({
                                "evidence_id": eid,
                                "framework_id": fw_ev,
                                "control_id": ctrl,
                                "confidence": "auto",
                                "via_check": check_id,
                            })
                            break
        return suggestions
    finally:
        db.close()


def get_unmapped_coverage(framework_id: str) -> list[dict]:
    """Find criteria with no evidence but with collector coverage."""
    try:
        from collectors.framework_mapping import CHECK_TO_FRAMEWORKS, canonical_framework
    except ImportError:
        return []
    framework_id = canonical_framework_id(framework_id)
    fw_key = canonical_framework(framework_id)
    db = _get_db()
    try:
        mapped = {r["control_id"] for r in db.execute(
            "SELECT DISTINCT control_id FROM evidence_mappings WHERE framework_id = ?", (framework_id,)
        ).fetchall()}
        results = []
        for check_id, fw_map in CHECK_TO_FRAMEWORKS.items():
            if fw_key in fw_map:
                for ctrl in fw_map[fw_key]:
                    if ctrl not in mapped:
                        results.append({"control_id": ctrl, "via_check": check_id})
        return results
    finally:
        db.close()
