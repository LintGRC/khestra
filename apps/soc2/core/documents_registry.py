"""Required SOC2 documents registry — the master list of every document needed for a SOC2 Type II audit."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

FAMILY_POLICIES = [
    {"key": "code_of_conduct", "name": "Code of Conduct / Ethics Policy", "category": "Policy", "controls": ["CC1.1", "CC1.2"], "evidence_type": "policy"},
    {"key": "acceptable_use", "name": "Acceptable Use Policy", "category": "Policy", "controls": ["CC6.1", "CC6.2", "CC6.7", "CC6.8"], "evidence_type": "policy"},
    {"key": "information_security", "name": "Information Security Policy", "category": "Policy", "controls": ["CC1.1", "CC1.2"], "evidence_type": "policy"},
    {"key": "access_control", "name": "Access Control Policy", "category": "Policy", "controls": ["CC6.1", "CC6.3", "CC6.6"], "evidence_type": "policy"},
    {"key": "password_authentication", "name": "Password / Authentication Policy", "category": "Policy", "controls": ["CC6.1", "CC6.5", "CC6.6"], "evidence_type": "policy"},
    {"key": "change_management", "name": "Change Management Policy", "category": "Policy", "controls": ["CC8.1"], "evidence_type": "policy"},
    {"key": "incident_response", "name": "Incident Response Policy", "category": "Policy", "controls": ["CC7.2", "CC7.3", "CC7.4", "CC7.5"], "evidence_type": "policy"},
    {"key": "vendor_management", "name": "Vendor Management Policy", "category": "Policy", "controls": ["CC5.1", "CC5.2", "CC9.2"], "evidence_type": "policy"},
    {"key": "risk_assessment", "name": "Risk Assessment Policy", "category": "Policy", "controls": ["CC3.1", "CC3.2"], "evidence_type": "policy"},
    {"key": "data_classification", "name": "Data Classification Policy", "category": "Policy", "controls": ["CC6.1", "CC6.7", "C1.1", "C1.2"], "evidence_type": "policy"},
    {"key": "business_continuity", "name": "Business Continuity / DR Policy", "category": "Policy", "controls": ["A1.2", "CC7.5"], "evidence_type": "policy"},
    {"key": "logging_monitoring", "name": "Logging & Monitoring Policy", "category": "Policy", "controls": ["CC7.1", "CC4.1", "CC6.1", "CC7.2"], "evidence_type": "policy"},
    {"key": "backup", "name": "Backup Policy", "category": "Policy", "controls": ["A1.2", "CC6.4", "CC7.5"], "evidence_type": "policy"},
    {"key": "network_security", "name": "Network Security Policy", "category": "Policy", "controls": ["CC6.1", "CC6.6"], "evidence_type": "policy"},
    {"key": "physical_security", "name": "Physical Security Policy", "category": "Policy", "controls": ["CC6.6"], "evidence_type": "policy"},
    {"key": "media_protection", "name": "Media Protection Policy", "category": "Policy", "controls": ["CC6.6", "C1.2"], "evidence_type": "policy"},
    {"key": "personnel_security", "name": "Personnel Security Policy", "category": "Policy", "controls": ["CC1.1", "CC1.4", "CC6.1"], "evidence_type": "policy"},
    {"key": "asset_management", "name": "Asset Management Policy", "category": "Policy", "controls": ["CC6.1"], "evidence_type": "policy"},
    {"key": "mobile_device", "name": "Mobile Device / BYOD Policy", "category": "Policy", "controls": ["CC6.1", "CC6.6"], "evidence_type": "policy"},
    {"key": "secure_development", "name": "Secure Software Development Policy", "category": "Policy", "controls": ["CC8.1"], "evidence_type": "policy"},
    {"key": "privacy", "name": "Privacy Policy", "category": "Policy", "controls": [f"P{i}.1" for i in range(1, 9)], "evidence_type": "policy"},
    {"key": "availability", "name": "Availability Policy", "category": "Policy", "controls": ["A1.1", "A1.2"], "evidence_type": "policy"},
    {"key": "processing_integrity", "name": "Processing Integrity Policy", "category": "Policy", "controls": [f"PI1.{i}" for i in range(1, 6)], "evidence_type": "policy"},
]

OPERATIONAL_PLANS = [
    {"key": "system_description", "name": "System Description", "category": "Plan", "controls": ["CC1.1", "CC1.2", "CC1.3", "CC1.4", "CC2.1", "CC2.2", "CC2.3"], "evidence_type": "other"},
    {"key": "business_continuity_plan", "name": "Business Continuity Plan", "category": "Plan", "controls": ["A1.2", "CC7.5"], "evidence_type": "other"},
    {"key": "disaster_recovery_plan", "name": "Disaster Recovery Plan", "category": "Plan", "controls": ["A1.2", "CC7.5"], "evidence_type": "other"},
    {"key": "incident_response_plan", "name": "Incident Response Plan", "category": "Plan", "controls": ["CC7.2", "CC7.3", "CC7.4"], "evidence_type": "other"},
    {"key": "risk_management_plan", "name": "Risk Management Plan", "category": "Plan", "controls": ["CC3.1", "CC3.2"], "evidence_type": "other"},
    {"key": "data_retention_schedule", "name": "Data Retention / Disposal Schedule", "category": "Plan", "controls": ["C1.2", "P4.1"], "evidence_type": "other"},
]

EVIDENCE_ARTIFACTS = [
    {"key": "org_chart", "name": "Organizational Chart", "category": "Artifact", "controls": ["CC1.1"], "evidence_type": "diagram"},
    {"key": "network_diagram", "name": "Network Topology / System Boundary Diagram", "category": "Artifact", "controls": ["CC1.2"], "evidence_type": "diagram"},
    {"key": "data_flow_diagram", "name": "Data Flow Diagram", "category": "Artifact", "controls": ["CC1.2", "CC2.1"], "evidence_type": "diagram"},
    {"key": "system_architecture", "name": "System Architecture / Technical Design Documents", "category": "Artifact", "controls": ["CC1.2", "CC8.1"], "evidence_type": "diagram"},
    {"key": "risk_assessment_report", "name": "Risk Assessment Report", "category": "Artifact", "controls": ["CC3.1", "CC3.2"], "evidence_type": "audit_report"},
    {"key": "board_minutes", "name": "Board / Management Review Minutes", "category": "Artifact", "controls": ["CC1.2"], "evidence_type": "board_minutes"},
    {"key": "training_records", "name": "Security Awareness Training Records", "category": "Artifact", "controls": ["CC1.1", "CC1.4"], "evidence_type": "training_record"},
    {"key": "penetration_test_report", "name": "Penetration Test Report", "category": "Artifact", "controls": ["CC7.1"], "evidence_type": "audit_report"},
    {"key": "vulnerability_scans", "name": "Vulnerability Scan Reports", "category": "Artifact", "controls": ["CC7.1"], "evidence_type": "scan_report"},
    {"key": "sdlc_evidence", "name": "SDLC Evidence (Code Reviews, Deployments, Testing)", "category": "Artifact", "controls": ["CC8.1"], "evidence_type": "audit_report"},
    {"key": "patch_records", "name": "Patch Management Records", "category": "Artifact", "controls": ["CC7.1", "CC8.1"], "evidence_type": "audit_report"},
    {"key": "antivirus_edr", "name": "Antivirus / EDR Configuration & Coverage", "category": "Artifact", "controls": ["CC7.1"], "evidence_type": "config_export"},
]

CONTRACTUAL_DOCS = [
    {"key": "customer_agreements", "name": "Customer Agreements / Service Contracts", "category": "Contract", "controls": ["CC2.3"], "evidence_type": "other"},
    {"key": "vendor_agreements", "name": "Vendor / Subprocessor Agreements", "category": "Contract", "controls": ["CC5.1", "CC9.2"], "evidence_type": "other"},
    {"key": "dpa", "name": "Data Processing Agreements (DPAs)", "category": "Contract", "controls": ["P4.1", "C1.2"], "evidence_type": "other"},
    {"key": "nda", "name": "Non-Disclosure Agreements (NDAs)", "category": "Contract", "controls": ["CC6.1", "C1.1"], "evidence_type": "other"},
    {"key": "sla_reports", "name": "SLA Commitments & Reports", "category": "Contract", "controls": ["A1.1", "A1.2", "PI1.1"], "evidence_type": "other"},
    {"key": "subservice_soc_reports", "name": "Subservice Organization SOC2 Reports", "category": "Contract", "controls": ["CC9.2", "CC5.1"], "evidence_type": "certificate"},
]

ALL_DOCUMENTS = FAMILY_POLICIES + OPERATIONAL_PLANS + EVIDENCE_ARTIFACTS + CONTRACTUAL_DOCS


def compute_document_status(doc: Dict[str, Any], answers: Dict[str, Any]) -> Dict[str, Any]:
    """Check if any of the document's mapped TSC controls have evidence uploaded."""
    latest: Optional[str] = None
    upload_count = 0
    for cid in doc["controls"]:
        ans = answers.get(cid, {})
        for ev in ans.get("evidence") or []:
            upload_count += 1
            up = ev.get("upload_date") or ""
            if up and (latest is None or up > latest):
                latest = up

    # Also check Evidence Hub
    try:
        from evidence_hub.store import list_evidence
        for cid in doc["controls"]:
            for ev in list_evidence(framework_id="SOC2", control_id=cid):
                upload_count += 1
                up = ev.get("uploaded_at") or ""
                if up and (latest is None or up > latest):
                    latest = up
    except Exception:
        pass

    status = "needs_document" if upload_count == 0 else "ok"

    return {
        **doc,
        "status": status,
        "evidence_count": upload_count,
        "last_uploaded": latest,
    }


def build_documents_list(answers: Dict[str, Any], scoped_criteria: List[str]) -> List[Dict[str, Any]]:
    """Build the full documents list with status for a SOC2 workspace."""
    docs = []
    for doc in ALL_DOCUMENTS:
        if not any(c in scoped_criteria for c in doc["controls"]):
            continue
        docs.append(compute_document_status(doc, answers))

    policy_keys = {d["key"] for d in FAMILY_POLICIES}
    for d in docs:
        if d["key"] in policy_keys:
            d["category"] = "Policy"

    return docs
