"""Bridgeport Systems demo — partial evidence coverage for readiness testing."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Tuple

from controls import CMMC_FRAMEWORK
from demo_data import _demo_topology_bytes
from org_assets import set_topology_bytes
from org_profile import default_control_answer

DEMO_B_ORG_NAME = "Bridgeport Systems LLC"

# Open gaps — more than Apex; realistic mid-assessment state
DEMO_B_GAPS = {
    "IA.L2-3.5.3": {
        "status": "NOT MET",
        "note": (
            "Duo MFA is deployed for VPN only. AWS console and legacy file share still allow password-only "
            "for two service accounts. Conditional MFA rollout scheduled Q3 2026."
        ),
        "remediation_plan": "Enforce MFA on AWS IAM and retire shared svc-fileshare account.",
        "estimated_cost": "3200",
    },
    "SC.L2-3.13.11": {
        "status": "PARTIALLY MET",
        "note": (
            "BitLocker on laptops; AWS EBS volumes use default encryption. FIPS validation package for "
            "OpenSSL on build server still being compiled for assessor."
        ),
        "remediation_plan": "Document FIPS mode for in-scope OpenSSL; upload AWS crypto attestation.",
        "estimated_cost": "1800",
    },
    "AC.L2-3.1.8": {
        "status": "IN PROGRESS",
        "note": (
            "AD lockout policy set to 5 attempts on domain controllers. Shop-floor kiosk AD-join "
            "account lacks lockout — compensating physical access control documented."
        ),
        "remediation_plan": "Dedicated kiosk GPO with lockout; remove shared local admin.",
        "estimated_cost": "4500",
    },
    "AU.L2-3.3.4": {
        "status": "NOT MET",
        "note": (
            "CloudWatch alarms exist for AWS root login but on-prem file server audit failure is not alerted. "
            "SIEM integration deferred pending budget."
        ),
        "remediation_plan": "Winlogbeat to CloudWatch Logs; PagerDuty route for audit service stop.",
        "estimated_cost": "6200",
    },
    "IR.L2-3.6.1": {
        "status": "PLANNED",
        "note": (
            "IR plan outline in shared drive; tabletop not conducted. MSP template adopted 2026-02."
        ),
        "remediation_plan": "Finalize IRP; tabletop with exec sign-off.",
        "estimated_cost": "2800",
    },
    "SI.L2-3.14.6": {
        "status": "IN PROGRESS",
        "note": (
            "Defender on endpoints; AWS GuardDuty enabled in us-east-1 only. eu-west-1 CUI bucket "
            "monitoring pending."
        ),
        "remediation_plan": "Enable GuardDuty all regions with CUI; weekly malware scan report.",
        "estimated_cost": "900",
    },
    "CM.L2-3.4.2": {
        "status": "NOT MET",
        "note": (
            "Security configuration settings documented in wiki but not all dev AMIs rebuilt after "
            "CIS benchmark update 2026-01."
        ),
        "remediation_plan": "Rebuild golden AMI; enforce launch template version pin.",
        "estimated_cost": "5500",
    },
}

# Wireless out of scope for this enclave
DEMO_B_NA = ("AC.L2-3.1.16", "AC.L2-3.1.17", "AC.L2-3.1.18")

# MET controls that receive attached evidence files (others MET rely on examine text only)
DEMO_B_EVIDENCE_CONTROLS = (
    "AC.L2-3.1.1",
    "AC.L2-3.1.2",
    "AC.L2-3.1.12",
    "AC.L2-3.1.13",
    "AC.L2-3.1.22",
    "AT.L2-3.2.1",
    "AT.L2-3.2.2",
    "AU.L2-3.3.1",
    "AU.L2-3.3.2",
    "CM.L2-3.4.1",
    "IA.L2-3.5.1",
    "IA.L2-3.5.2",
    "IA.L2-3.5.7",
    "IR.L2-3.6.2",
    "MP.L2-3.8.3",
    "PE.L2-3.10.1",
    "PE.L2-3.10.2",
    "PS.L2-3.9.1",
    "RA.L2-3.11.1",
    "SC.L2-3.13.1",
    "SC.L2-3.13.8",
    "SC.L2-3.13.15",
    "SI.L2-3.14.1",
    "SI.L2-3.14.2",
    "SI.L2-3.14.3",
    "SI.L2-3.14.4",
    "SI.L2-3.14.5",
)


def get_demo_b_org_profile() -> Dict[str, str]:
    return {
        "org_name": DEMO_B_ORG_NAME,
        "system_name": "Bridgeport CUI Platform (AWS + Google Workspace)",
        "system_unique_id": "BRG-CUI-002",
        "system_description": (
            "Bridgeport Systems LLC fabricates precision components for federal supply chains. "
            "Approximately 28 staff access CUI via Google Workspace (GCC) and an AWS workload "
            "account hosting document review apps. A legacy on-prem file server (FS-BRG-01) "
            "is being decommissioned; CUI migration to S3 completed 2025-11."
        ),
        "architecture_summary": (
            "Identity: Google Workspace with 2SV for admins; AWS IAM Identity Center for cloud. "
            "CUI stored in S3 bucket brg-cui-prod (SSE-KMS) and Google Drive shared drives. "
            "Remote staff use Cisco AnyConnect VPN to reach internal tools — no corporate Wi-Fi "
            "in the machine shop (wired only). Endpoints: Windows 11 laptops with Defender."
        ),
        "boundary_description": (
            "In scope: AWS account 112233445566 (CUI workloads), Google Workspace tenant, "
            "VPN concentrator, FS-BRG-01 during transition, admin laptops. "
            "Out of scope: shop-floor CNC network, guest network, HR payroll (Gusto)."
        ),
        "org_address": "88 Harbor Road, Bridgeport, CT 06604",
        "org_phone": "(203) 555-0198",
        "system_owner": "Maria Chen, Operations Director",
        "iso_name": "Devon Walsh, Security Coordinator",
        "sysadmin_name": "Pat Okafor, IT Manager",
        "network_admin_name": "Pat Okafor, IT Manager",
        "auditor_name": "Internal assessment (Bridgeport ISO)",
        "hardware_inventory": (
            "28 × Lenovo ThinkPad T14 (Win11); 2 × Dell PowerEdge (AD + FS-BRG-01); "
            "Cisco ASA VPN; AWS: EC2 (2), S3, KMS, GuardDuty (partial regions)."
        ),
        "software_inventory": (
            "Google Workspace Business Plus; AWS (EC2, S3, IAM Identity Center, CloudWatch); "
            "Duo MFA (VPN); Microsoft Defender for Endpoint; Cisco AnyConnect."
        ),
        "hw_sw_org_owned": "Yes — laptops and servers owned by Bridgeport; AWS/Google are contractor-operated services.",
        "header_short_name": "Bridgeport Systems",
    }


def get_demo_b_asset_scope() -> Dict[str, int]:
    return {
        "CUI Assets": 100,
        "Security Protection Assets": 70,
        "Contractor Risk Managed Assets": 20,
        "Out-of-Scope Assets": 30,
    }


def get_demo_b_env_scope() -> Dict[str, str]:
    return {
        "processes_cui": "yes",
        "uses_wireless": "no",
        "remote_workforce": "yes",
        "uses_m365": "no",
        "uses_google": "yes",
        "cloud_hosting": "aws",
    }


def _bridgeport_narrative(cid: str, info: dict) -> str:
    return (
        f"Bridgeport implements {info['name'][:80]}… via documented policies in the CUI program "
        f"folder and technical controls on AWS/Google. Owner: Devon Walsh. "
        f"Last reviewed 2026-Q1. Evidence varies by control — see attachments where present."
    )


def _evidence_blob(cid: str, info: dict) -> str:
    return (
        f"BRIDGEPORT SYSTEMS LLC — EVIDENCE ARTIFACT (DEMO)\n"
        f"Control: {cid}\n"
        f"Family: {info['family']}\n"
        f"Requirement: {info['name'][:200]}\n\n"
        "This synthetic file simulates a policy excerpt, config export, or screenshot "
        "description for local evidence-coverage testing. Replace with real artifacts "
        "for audit.\n"
    )


def _build_evidence_attachments() -> Tuple[Dict[str, List[dict]], Dict[str, bytes]]:
    """Metadata for answers + binary map for restored_evidence."""
    meta_by_cid: Dict[str, List[dict]] = {}
    restored: Dict[str, bytes] = {}

    for cid in DEMO_B_EVIDENCE_CONTROLS:
        if cid not in CMMC_FRAMEWORK:
            continue
        info = CMMC_FRAMEWORK[cid]
        fname = f"BRG_{cid.replace('.', '_')}_evidence.txt"
        content = _evidence_blob(cid, info)
        data = content.encode("utf-8")
        fhash = hashlib.sha256(data).hexdigest()
        entry = {
            "filename": fname,
            "sha256": fhash,
            "upload_date": "2026-03-15 09:30:00",
            "uploaded_by": "Assessor",
            "control_id": cid,
        }
        meta_by_cid.setdefault(cid, []).append(entry)
        restored[f"{cid}_{fname}"] = data

    return meta_by_cid, restored


def get_demo_b_answers() -> Dict[str, Any]:
    evidence_meta, _ = _build_evidence_attachments()
    answers: Dict[str, Any] = {}

    for cid, info in CMMC_FRAMEWORK.items():
        ans = default_control_answer()
        if cid in DEMO_B_NA:
            ans["status"] = "NOT APPLICABLE"
            ans["implementation_narrative"] = (
                "No wireless access to CUI systems — machine shop and office CUI enclave are wired Ethernet only."
            )
        else:
            ans["status"] = "MET"
            ans["maturity"] = "Implemented"
            ans["implementation_narrative"] = _bridgeport_narrative(cid, info)
        if cid in evidence_meta:
            ans["examine"] = f"POL-BRG-{cid[-7:]}.pdf; AWS/Google admin export"
        elif cid not in DEMO_B_GAPS:
            ans["examine"] = ""
        ans["interview"] = "Devon Walsh (ISO), Pat Okafor (IT)"
        ans["test"] = f"Sample review Q1-2026 — {cid}"
        ans["owner"] = "Devon Walsh"
        if cid in evidence_meta:
            ans["evidence"] = list(evidence_meta[cid])
        answers[cid] = ans

    for cid, gap in DEMO_B_GAPS.items():
        answers[cid]["status"] = gap["status"]
        answers[cid]["implementation_narrative"] = gap["note"]
        answers[cid]["assessor_notes"] = gap["note"]
        answers[cid]["remediation_plan"] = gap.get("remediation_plan", "")
        answers[cid]["owner"] = "Devon Walsh"
        answers[cid]["target_date"] = "2026-10-31"
        answers[cid]["estimated_cost"] = gap.get("estimated_cost", "4000")
        answers[cid]["evidence"] = []
        if gap["status"] in ("NOT MET", "PARTIALLY MET", "IN PROGRESS", "PLANNED"):
            answers[cid]["likelihood"] = "Medium"
            answers[cid]["impact"] = "High" if CMMC_FRAMEWORK[cid]["weight"] >= 5 else "Medium"

    return answers


def get_demo_b_restored_evidence() -> Dict[str, bytes]:
    _, restored = _build_evidence_attachments()
    return restored


def get_demo_b_org_assets() -> Dict[str, Any]:
    return {
        "topology_filename": "bridgeport_topology.png",
        "appendix_files": [
            {"filename": "Bridgeport_IRP_Outline.txt", "label": "Incident Response outline (draft)"},
            {"filename": "Bridgeport_CUI_Policy.txt", "label": "CUI handling policy excerpt"},
        ],
    }


def get_demo_b_org_asset_bytes() -> Dict[str, bytes]:
    blobs: Dict[str, bytes] = {}
    set_topology_bytes(blobs, "bridgeport_topology.png", _demo_topology_bytes())
    blobs["appendix:Bridgeport_IRP_Outline.txt"] = (
        "BRIDGEPORT SYSTEMS — IR PLAN OUTLINE (DEMO)\n"
        "Contacts: Devon Walsh (ISO), Maria Chen (exec)\n"
        "Report within 30 min to helpdesk; CUI spillage procedure in section 4.\n"
    ).encode("utf-8")
    blobs["appendix:Bridgeport_CUI_Policy.txt"] = (
        "BRIDGEPORT CUI POLICY (EXCERPT / DEMO)\n"
        "CUI only in approved Google shared drives and S3 bucket brg-cui-prod.\n"
        "USB storage prohibited. VPN required off-site.\n"
    ).encode("utf-8")
    return blobs


def get_demo_b_session_payload() -> Dict[str, Any]:
    return {
        "org_name": DEMO_B_ORG_NAME,
        "org_profile": get_demo_b_org_profile(),
        "asset_scope": get_demo_b_asset_scope(),
        "answers": get_demo_b_answers(),
        "scoped_controls": list(CMMC_FRAMEWORK.keys()),
        "org_assets": get_demo_b_org_assets(),
        "org_asset_bytes": get_demo_b_org_asset_bytes(),
        "env_scope": get_demo_b_env_scope(),
        "restored_evidence": get_demo_b_restored_evidence(),
    }
