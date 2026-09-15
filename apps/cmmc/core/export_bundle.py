"""Export compliance package: SSP + POA&M + evidence + SPRS summary + readiness report."""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
import zipfile
from datetime import datetime
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from controls import CMMC_FRAMEWORK
from org_inventory import INVENTORY_COLUMNS
from poam_export import export_poam_xlsx
from readiness import evaluate_pre_c3pao_readiness
from security_utils import safe_evidence_filename
from sprs_entry import build_sprs_entry_summary
from sprs_validation import format_validation_report

_logger = logging.getLogger(__name__)

# Ensure packages/ is on sys.path for cross-package imports
_PACKAGES_DIR = Path(__file__).resolve().parents[2] / "packages"
if _PACKAGES_DIR.is_dir() and str(_PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGES_DIR))


def _evidence_bytes_for_entry(
    cid: str,
    ev: Dict[str, Any],
    restored_evidence: Dict[str, bytes],
) -> Optional[bytes]:
    if ev.get("data_bytes"):
        return ev["data_bytes"]
    key = f"{cid}_{ev.get('filename', '')}"
    return restored_evidence.get(key)


def _collect_evidence_paths(
    answers: Dict[str, Any],
    restored_evidence: Optional[Dict[str, bytes]] = None,
) -> List[tuple[str, str, bytes]]:
    """Return (zip_path, control_id, bytes) for each attached evidence file."""
    restored = restored_evidence or {}
    out: List[tuple[str, str, bytes]] = []
    for cid, ans in answers.items():
        for ev in ans.get("evidence") or []:
            data = _evidence_bytes_for_entry(cid, ev, restored)
            if not data:
                continue
            fname = safe_evidence_filename(ev.get("filename") or "evidence.bin")
            zip_path = f"evidence/{cid}/{fname}"
            out.append((zip_path, cid, data))
    return out


def _collect_hub_evidence_paths(scoped_controls: List[str]) -> List[tuple[str, str, bytes]]:
    """Return approved Evidence Hub files mapped to scoped controls."""
    try:
        from evidence_hub.store import list_evidence, get_evidence_file_path
    except ImportError:
        return []

    out: List[tuple[str, str, bytes]] = []
    for cid in scoped_controls:
        try:
            items = list_evidence(framework_id="CMMC", control_id=cid)
        except Exception:
            continue
        for item in items:
            if item.get("review_status") != "approved":
                continue
            try:
                path = get_evidence_file_path(item["id"])
                if not path:
                    continue
                data = path.read_bytes()
                fname = safe_evidence_filename(item.get("filename") or "hub_evidence.bin")
                zip_path = f"evidence/{cid}/{fname}"
                out.append((zip_path, cid, data))
            except Exception:
                continue
    return out


def _collect_findings_for_export(scoped_controls: List[str]) -> List[dict]:
    """Return findings linked to any of the scoped controls."""
    try:
        from findings.store import list_findings
    except ImportError:
        return []
    seen: set[str] = set()
    out: list[dict] = []
    for cid in scoped_controls:
        try:
            items = list_findings(control_id=cid)
        except Exception:
            continue
        for item in items:
            if item["id"] not in seen:
                seen.add(item["id"])
                out.append(item)
    return out


def _collect_exceptions_for_export(scoped_controls: List[str]) -> List[dict]:
    """Return open exception/POA&M items linked to any of the scoped controls."""
    try:
        from exceptions.store import list_exceptions
    except ImportError:
        return []
    seen: set[str] = set()
    out: list[dict] = []
    for cid in scoped_controls:
        try:
            items = list_exceptions(control_id=cid)
        except Exception:
            continue
        for item in items:
            if item["id"] not in seen:
                seen.add(item["id"])
                out.append(item)
    return out


def _package_readme(org_name: str, evidence_count: int, appendix_count: int) -> str:
    return "\n".join(
        [
            f"CMMC Readiness Package — {org_name}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "CONTENTS",
            "  CMMC_SSP_*.docx          System Security Plan (official DoW CUI template)",
            "  CMMC_POAM_*.xlsx         Plan of Action & Milestones",
            "  SPRS_Entry_Summary_*.txt PIEE / self-assessment handoff",
            "  Pre_C3PAO_Readiness_*.txt Checklist and remediation priority",
            "  SPRS_Validation_Report_*.txt Scoring engine self-test",
            f"  evidence/                {evidence_count} file(s) by control ID (workspace + Evidence Hub)",
            f"  org_assets/              {appendix_count} topology/appendix file(s)",
            "",
            "NOTES",
            "  - Re-export SSP after assessment changes so files match current data.",
            "  - Review the SSP before sharing with a C3PAO.",
            "  - Record of Changes and some identification tables are left for you to complete.",
            "  - This package supports audit prep; it is not a certification.",
        ]
    )


def build_export_package(
    answers: Dict[str, Any],
    org_profile: Dict[str, str],
    asset_scope: Dict[str, Any],
    scoped_controls: List[str],
    export_poam_fn: Callable,
    audit_log=None,
    org_assets: Optional[Dict[str, Any]] = None,
    org_asset_bytes: Optional[Dict[str, bytes]] = None,
    org_inventory: Optional[Dict[str, Any]] = None,
    restored_evidence: Optional[Dict[str, bytes]] = None,
    ssp_bytes: Optional[bytes] = None,
    env_scope: Optional[Dict[str, str]] = None,
) -> bytes:
    """Zip: SSP, POA&M xlsx, SPRS summary, readiness, validation, evidence + org assets."""
    from ssp import assemble_ssp
    from config import resolve_ssp_template

    from readiness_review import format_readiness_review_report, run_readiness_review
    from evidence_coverage import compute_readiness_scores, format_evidence_coverage_report

    from change_history import audit_log_to_csv

    readiness = evaluate_pre_c3pao_readiness(answers, org_profile, asset_scope, scoped_controls)
    review = run_readiness_review(
        answers, org_profile, scoped_controls, env_scope, asset_scope
    )
    from env_scope import format_env_scope_summary, merge_env_scope

    readiness_scores = compute_readiness_scores(answers, org_profile, scoped_controls)
    env_txt = format_env_scope_summary(merge_env_scope(env_scope))
    sprs = readiness["sprs_detail"]
    org_name = org_profile.get("org_name") or "Organization"
    sprs_txt = build_sprs_entry_summary(org_profile, sprs, scoped_controls, asset_scope)
    review_txt = format_readiness_review_report(review, org_name)
    evidence_detail = readiness_scores.get("evidence_detail", {})
    evidence_txt = format_evidence_coverage_report(evidence_detail, readiness_scores, org_name)
    # Pre-C3PAO readiness summary
    readiness_txt = f"Pre-C3PAO Readiness\n\nOrganization: {org_name}\nSPRS Score: {readiness.get('sprs_score', 'N/A')}/110\nControls Assessed: {readiness.get('controls_assessed', 0)}/{readiness.get('controls_total', 110)}\n"
    stamp = datetime.now().strftime("%Y%m%d")
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in org_name)[:40]

    if ssp_bytes is None:
        ssp_bytes = assemble_ssp(
            answers,
            asset_scope,
            org_name=org_name,
            scoped_controls=scoped_controls,
            org_profile=org_profile,
            org_assets=org_assets,
            org_asset_bytes=org_asset_bytes,
            template_path=resolve_ssp_template(),
            audit_log=audit_log,
            org_inventory=org_inventory,
        )
    evidence_files = _collect_evidence_paths(answers, restored_evidence)
    hub_files = _collect_hub_evidence_paths(scoped_controls)
    evidence_files.extend(hub_files)
    evidence_count = len(evidence_files)
    findings_list = _collect_findings_for_export(scoped_controls)
    exceptions_list = _collect_exceptions_for_export(scoped_controls)
    org_bytes = org_asset_bytes or {}
    poam_bytes = export_poam_xlsx(answers, scoped_controls, exceptions_list)

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"CMMC_SSP_{safe}_{stamp}.docx", ssp_bytes)
        zf.writestr(f"CMMC_POAM_{safe}_{stamp}.xlsx", poam_bytes)
        zf.writestr(f"SPRS_Entry_Summary_{stamp}.txt", sprs_txt)
        zf.writestr(f"Pre_C3PAO_Readiness_{stamp}.txt", readiness_txt)
        zf.writestr(f"Readiness_Review_{stamp}.txt", review_txt)
        zf.writestr(f"Evidence_Coverage_{stamp}.txt", evidence_txt)
        zf.writestr(f"Environment_Scope_{stamp}.txt", env_txt)
        zf.writestr(f"SPRS_Validation_Report_{stamp}.txt", format_validation_report())
        if audit_log:
            zf.writestr(f"Change_History_{stamp}.csv", audit_log_to_csv(audit_log))
        if findings_list:
            zf.writestr(f"Findings_{stamp}.json", json.dumps(findings_list, indent=2, default=str))

        # Policies — policy DOCX files
        try:
            from policies.store import list_documents
            from policies.export import generate_docx
            docs = list_documents()
            for doc in docs:
                if doc.get("content"):
                    try:
                        safe_title = doc.get("title", "Policy").replace(" ", "_").replace("/", "_").replace(":", "")[:60]
                        content = doc["content"]
                        # If content starts with {, it might be TipTap JSON — pass as-is
                        v = str(doc.get("version", 1))
                        docx_bytes = generate_docx(name=doc.get("title", "Policy"), content=content, version=v)
                        zf.writestr(f"policies/{safe_title}_v{v}.docx", docx_bytes)
                    except Exception as exc:
                        _logger.warning("Policy export failed for %s: %s", doc.get("title"), exc)
        except Exception as exc:
            _logger.warning("Policy listing failed: %s", exc)

        # Risk register CSV
        try:
            from risks.store import list_risks as _list_risks
            items = _list_risks()
            if items:
                out = StringIO()
                w = csv.writer(out)
                w.writerow([
                    "ID", "Title", "Description", "Category", "Framework", "System ID",
                    "Owner", "Status", "Likelihood", "Impact", "Inherent Score",
                    "Residual Score", "Treatment", "Treatment Plan", "Created At"
                ])
                for r in items:
                    w.writerow([
                        r.get("id"), r.get("title"), r.get("description"), r.get("category"),
                        r.get("framework"), r.get("system_id", ""), r.get("owner"), r.get("status"),
                        r.get("likelihood"), r.get("impact"), r.get("inherent_score"),
                        r.get("residual_score"), r.get("treatment"), r.get("treatment_plan"),
                        r.get("created_at"),
                    ])
                zf.writestr(f"Risk_Register_{stamp}.csv", out.getvalue())
        except Exception as exc:
            _logger.warning("Risk register export failed: %s", exc)

        # Asset inventory CSV
        if org_inventory:
            assets = org_inventory.get("assets") or []
            if assets:
                out = StringIO()
                w = csv.writer(out)
                w.writerow(INVENTORY_COLUMNS)
                for row in assets:
                    w.writerow([row.get(col, "") for col in INVENTORY_COLUMNS])
                zf.writestr(f"Asset_Inventory_{stamp}.csv", out.getvalue())

        # Personnel roster CSV
        try:
            from personnel.store import list_personnel as _list_personnel
            people = _list_personnel()
            if people:
                p_fields = ["name", "email", "role", "department", "status",
                            "mfa_status", "is_privileged", "phone", "location",
                            "manager", "frameworks", "org_id"]
                out = StringIO()
                w = csv.DictWriter(out, fieldnames=p_fields, extrasaction="ignore")
                w.writeheader()
                for p in people:
                    row = {**p}
                    if isinstance(row.get("frameworks"), list):
                        row["frameworks"] = ", ".join(row["frameworks"])
                    w.writerow(row)
                zf.writestr(f"Personnel_Roster_{stamp}.csv", out.getvalue())
        except Exception as exc:
            _logger.warning("Personnel roster export failed: %s", exc)

        zf.writestr(
            "README_Package.txt",
            _package_readme(org_name, len(evidence_files), len(org_bytes)),
        )
        for zip_path, _cid, data in evidence_files:
            zf.writestr(zip_path, data)
        for key, data in org_bytes.items():
            zf.writestr(f"org_assets/{key.replace(':', '__')}", data)

    buf.seek(0)
    return buf.getvalue()


def _format_readiness_report(readiness: Dict[str, Any], org_name: str) -> str:
    lines = [
        f"Pre-C3PAO Readiness Report — {org_name}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"Overall self-ready (heuristic): {'YES' if readiness['self_ready'] else 'NO'}",
        f"SPRS score: {readiness['sprs_score']}/110",
        f"Report export readiness: {readiness['score']}%",
        f"Evidence coverage (MET controls): {readiness['evidence_coverage_pct']}%",
        "",
        "CHECKLIST",
    ]
    for item in readiness["checklist"]:
        mark = "x" if item["done"] else " "
        lines.append(f"  [{mark}] {item['item']} — {item['detail']}")
    lines.extend(["", "REMEDIATION PRIORITY (fix 5-point controls first)"])
    for cid in readiness["remediation_priority"][:12]:
        w = CMMC_FRAMEWORK[cid]["weight"]
        lines.append(f"  - {cid} (-{w}): {CMMC_FRAMEWORK[cid]['name'][:60]}…")
    if readiness.get("blockers"):
        lines.extend(["", "BLOCKERS"])
        for b in readiness["blockers"]:
            lines.append(f"  ! {b}")
    return "\n".join(lines)
