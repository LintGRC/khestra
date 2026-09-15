"""Required CMMC documents registry — the master list of every document needed."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

FAMILY_POLICIES = [
    {"key": "ac_policy", "name": "Access Control Policy", "category": "Policy", "family": "AC", "controls": [f"AC.L2-3.1.{i}" for i in range(1, 23)], "evidence_type": "policy"},
    {"key": "at_policy", "name": "Awareness and Training Policy", "category": "Policy", "family": "AT", "controls": [f"AT.L2-3.2.{i}" for i in range(1, 4)], "evidence_type": "policy"},
    {"key": "au_policy", "name": "Audit and Accountability Policy", "category": "Policy", "family": "AU", "controls": [f"AU.L2-3.3.{i}" for i in range(1, 10)], "evidence_type": "policy"},
    {"key": "cm_policy", "name": "Configuration Management Policy", "category": "Policy", "family": "CM", "controls": [f"CM.L2-3.4.{i}" for i in range(1, 10)], "evidence_type": "policy"},
    {"key": "ia_policy", "name": "Identification and Authentication Policy", "category": "Policy", "family": "IA", "controls": [f"IA.L2-3.5.{i}" for i in range(1, 12)], "evidence_type": "policy"},
    {"key": "ir_policy", "name": "Incident Response Policy", "category": "Policy", "family": "IR", "controls": [f"IR.L2-3.6.{i}" for i in range(1, 4)], "evidence_type": "policy"},
    {"key": "ma_policy", "name": "Maintenance Policy", "category": "Policy", "family": "MA", "controls": [f"MA.L2-3.7.{i}" for i in range(1, 7)], "evidence_type": "policy"},
    {"key": "mp_policy", "name": "Media Protection Policy", "category": "Policy", "family": "MP", "controls": [f"MP.L2-3.8.{i}" for i in range(1, 10)], "evidence_type": "policy"},
    {"key": "ps_policy", "name": "Personnel Security Policy", "category": "Policy", "family": "PS", "controls": [f"PS.L2-3.9.{i}" for i in range(1, 3)], "evidence_type": "policy"},
    {"key": "pe_policy", "name": "Physical and Environmental Protection Policy", "category": "Policy", "family": "PE", "controls": [f"PE.L2-3.10.{i}" for i in range(1, 7)], "evidence_type": "policy"},
    {"key": "ra_policy", "name": "Risk Assessment Policy", "category": "Policy", "family": "RA", "controls": [f"RA.L2-3.11.{i}" for i in range(1, 4)], "evidence_type": "policy"},
    {"key": "ca_policy", "name": "Security Assessment Policy", "category": "Policy", "family": "CA", "controls": [f"CA.L2-3.12.{i}" for i in range(1, 5)], "evidence_type": "policy"},
    {"key": "sc_policy", "name": "System and Communications Protection Policy", "category": "Policy", "family": "SC", "controls": [f"SC.L2-3.13.{i}" for i in range(1, 17)], "evidence_type": "policy"},
    {"key": "si_policy", "name": "System and Information Integrity Policy", "category": "Policy", "family": "SI", "controls": [f"SI.L2-3.14.{i}" for i in range(1, 8)], "evidence_type": "policy"},
]

OPERATIONAL_PLANS = [
    {"key": "ssp", "name": "System Security Plan (SSP)", "category": "Plan", "controls": ["CA.L2-3.12.4"], "evidence_type": "other"},
    {"key": "poam", "name": "Plan of Action & Milestones (POA&M)", "category": "Plan", "controls": ["CA.L2-3.12.2"], "evidence_type": "other"},
    {"key": "ir_plan", "name": "Incident Response Plan", "category": "Plan", "controls": ["IR.L2-3.6.1"], "evidence_type": "other"},
    {"key": "baseline_config", "name": "Baseline Configuration Standards", "category": "Plan", "controls": ["CM.L2-3.4.1"], "evidence_type": "config_export"},
    {"key": "rules_of_behavior", "name": "Rules of Behavior / Acceptable Use", "category": "Plan", "controls": ["AC.L2-3.1.16"], "evidence_type": "policy"},
    {"key": "cui_boundary", "name": "CUI Boundary Description", "category": "Plan", "controls": ["AC.L2-3.1.19"], "evidence_type": "diagram"},
]

EVIDENCE_ARTIFACTS = [
    {"key": "org_chart", "name": "Org Chart", "category": "Artifact", "controls": ["PS.L2-3.9.1"], "evidence_type": "other"},
    {"key": "raci_matrix", "name": "RACI / Role Matrix", "category": "Artifact", "controls": ["AT.L2-3.2.2"], "evidence_type": "other"},
    {"key": "network_diagram", "name": "Network Diagram", "category": "Artifact", "controls": ["SC.L2-3.13.1"], "evidence_type": "diagram"},
    {"key": "data_flow_diagram", "name": "Data Flow Diagram", "category": "Artifact", "controls": ["SC.L2-3.13.1"], "evidence_type": "diagram"},
    {"key": "training_records", "name": "Security Awareness Training Records", "category": "Artifact", "controls": ["AT.L2-3.2.1"], "evidence_type": "training_record"},
    {"key": "screening_records", "name": "Personnel Screening Records", "category": "Artifact", "controls": ["PS.L2-3.9.1"], "evidence_type": "other"},
    {"key": "access_reviews", "name": "Access Control / Account Reviews", "category": "Artifact", "controls": ["AC.L2-3.1.2"], "evidence_type": "audit_report"},
    {"key": "privileged_reviews", "name": "Privileged Access Reviews", "category": "Artifact", "controls": ["AC.L2-3.1.7"], "evidence_type": "audit_report"},
    {"key": "wireless_auth", "name": "Wireless Access Authorizations", "category": "Artifact", "controls": ["AC.L2-3.1.16"], "evidence_type": "config_export"},
    {"key": "mobile_auth", "name": "Mobile Device Authorizations", "category": "Artifact", "controls": ["AC.L2-3.1.18"], "evidence_type": "config_export"},
    {"key": "mfa_config", "name": "MFA / Authentication Config", "category": "Artifact", "controls": ["IA.L2-3.5.3"], "evidence_type": "screenshot"},
    {"key": "audit_logs", "name": "Audit Logs (system-generated)", "category": "Artifact", "controls": ["AU.L2-3.3.1"], "evidence_type": "config_export"},
    {"key": "audit_reviews", "name": "Audit Log Review Records", "category": "Artifact", "controls": ["AU.L2-3.3.2"], "evidence_type": "audit_report"},
    {"key": "time_sync", "name": "Time Synchronization Config", "category": "Artifact", "controls": ["AU.L2-3.3.6"], "evidence_type": "config_export"},
    {"key": "config_baselines", "name": "Configuration Baseline Standards", "category": "Artifact", "controls": ["CM.L2-3.4.1"], "evidence_type": "config_export"},
    {"key": "change_records", "name": "Configuration Change Records", "category": "Artifact", "controls": ["CM.L2-3.4.3"], "evidence_type": "audit_report"},
    {"key": "ir_test_reports", "name": "Incident Response Test Reports", "category": "Artifact", "controls": ["IR.L2-3.6.3"], "evidence_type": "audit_report"},
    {"key": "maintenance_records", "name": "Maintenance Records", "category": "Artifact", "controls": ["MA.L2-3.7.1"], "evidence_type": "other"},
    {"key": "media_destruction", "name": "Media Sanitization / Destruction Records", "category": "Artifact", "controls": ["MP.L2-3.8.3"], "evidence_type": "other"},
    {"key": "removable_media", "name": "Removable Media Controls", "category": "Artifact", "controls": ["MP.L2-3.8.7"], "evidence_type": "config_export"},
    {"key": "physical_access_logs", "name": "Physical Access Logs", "category": "Artifact", "controls": ["PE.L2-3.10.1"], "evidence_type": "other"},
    {"key": "visitor_records", "name": "Visitor Records", "category": "Artifact", "controls": ["PE.L2-3.10.3"], "evidence_type": "other"},
    {"key": "physical_device_inventory", "name": "Physical Access Device Inventory", "category": "Artifact", "controls": ["PE.L2-3.10.5"], "evidence_type": "other"},
    {"key": "risk_assessment", "name": "Risk Assessment Records", "category": "Artifact", "controls": ["RA.L2-3.11.1"], "evidence_type": "audit_report"},
    {"key": "vuln_scans", "name": "Vulnerability Scan Reports", "category": "Artifact", "controls": ["RA.L2-3.11.2"], "evidence_type": "scan_report"},
    {"key": "assessment_results", "name": "Security Assessment Results", "category": "Artifact", "controls": ["CA.L2-3.12.1"], "evidence_type": "audit_report"},
    {"key": "continuous_monitoring", "name": "Continuous Monitoring Reports", "category": "Artifact", "controls": ["CA.L2-3.12.3"], "evidence_type": "audit_report"},
    {"key": "fips_certs", "name": "FIPS Cryptographic Certificates", "category": "Artifact", "controls": ["SC.L2-3.13.11"], "evidence_type": "certificate"},
    {"key": "key_management", "name": "Cryptographic Key Management Records", "category": "Artifact", "controls": ["SC.L2-3.13.10"], "evidence_type": "other"},
    {"key": "flaw_remediation", "name": "Flaw Remediation Logs", "category": "Artifact", "controls": ["SI.L2-3.14.1"], "evidence_type": "audit_report"},
    {"key": "malware_logs", "name": "Malware Detection / EDR Logs", "category": "Artifact", "controls": ["SI.L2-3.14.2"], "evidence_type": "scan_report"},
    {"key": "system_monitoring", "name": "System Monitoring Evidence", "category": "Artifact", "controls": ["SI.L2-3.14.3"], "evidence_type": "audit_report"},
    {"key": "pentest_reports", "name": "Penetration Test Reports", "category": "Artifact", "controls": ["CA.L2-3.12.1"], "evidence_type": "audit_report"},
]

CONTRACTUAL_DOCS = [
    {"key": "vendor_flowdown", "name": "Vendor CMMC Flow-Down Clauses", "category": "Contract", "controls": ["CA.L2-3.12.3"], "evidence_type": "other"},
    {"key": "vendor_certs", "name": "Vendor CMMC Certificates / SPRS Scores", "category": "Contract", "controls": ["CA.L2-3.12.3"], "evidence_type": "certificate"},
    {"key": "crm", "name": "Customer Responsibility Matrix (CRM)", "category": "Contract", "controls": ["SC.L2-3.13.1"], "evidence_type": "other"},
    {"key": "isa_atc", "name": "Interconnection Security Agreements / ATC", "category": "Contract", "controls": ["SC.L2-3.13.1"], "evidence_type": "other"},
]

ALL_DOCUMENTS = FAMILY_POLICIES + OPERATIONAL_PLANS + EVIDENCE_ARTIFACTS + CONTRACTUAL_DOCS


def compute_document_status(doc: Dict[str, Any], answers: Dict[str, Any]) -> Dict[str, Any]:
    """Check if any of the document's mapped controls have evidence uploaded."""
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
            for ev in list_evidence(framework_id="CMMC", control_id=cid):
                upload_count += 1
                up = ev.get("uploaded_at") or ""
                if up and (latest is None or up > latest):
                    latest = up
    except Exception:
        pass

    if upload_count == 0:
        status = "needs_document"
    else:
        status = "ok"

    return {
        **doc,
        "status": status,
        "evidence_count": upload_count,
        "last_uploaded": latest,
    }


def build_documents_list(answers: Dict[str, Any], scoped_controls: List[str]) -> List[Dict[str, Any]]:
    """Build the full documents list with status for a workspace."""
    docs = []
    for doc in ALL_DOCUMENTS:
        if not any(c in scoped_controls for c in doc["controls"]):
            continue
        docs.append(compute_document_status(doc, answers))

    policies_templates = {"ac_policy", "at_policy", "au_policy", "cm_policy", "ia_policy",
                          "ir_policy", "ma_policy", "mp_policy", "ps_policy", "pe_policy",
                          "ra_policy", "ca_policy", "sc_policy", "si_policy"}
    for d in docs:
        if d["key"] in policies_templates:
            d["category"] = "Policy"

    return docs
