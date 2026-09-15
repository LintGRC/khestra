"""Synthetic demo organization — realistic enough for sample SSP/POA&M exports."""

from pathlib import Path
from typing import Any, Dict

from controls import CMMC_FRAMEWORK
from org_assets import set_topology_bytes
from org_profile import default_control_answer

DEMO_ORG_NAME = "Apex Defense Manufacturing LLC"
_PLATFORM_ROOT = Path(__file__).resolve().parents[1]
_ASSET_DIRS = (
    _PLATFORM_ROOT / "samples",
    Path(__file__).resolve().parent / "samples",
    Path(__file__).resolve().parent / "docs" / "samples",
)

# Open gaps for POA&M / SPRS demo — longer, audit-style notes
DEMO_GAPS = {
    "IA.L2-3.5.3": {
        "status": "NOT MET",
        "note": (
            "MFA is enforced for Entra global administrators and remote access via Conditional Access "
            "policy CA-MFA-PRIV (reviewed 2026-03-15). Two legacy engineering workstations on the shop floor "
            "still allow cached Entra sessions without step-up MFA when accessing the CUI SharePoint site. "
            "Remediation: extend CA-MFA-ALL-CUI to all CUI library sessions; disable persistent browser sessions "
            "on shared PCs. Target completion 2026-09-30. Owner: Sam Rivera."
        ),
        "remediation_plan": "Deploy CA policy CA-MFA-ALL-CUI; re-image legacy PCs with Intune compliance baseline.",
        "estimated_cost": "2400",
    },
    "SC.L2-3.13.11": {
        "status": "IN PROGRESS",
        "note": (
            "BitLocker AES-256 and TLS 1.2+ are enabled on all Intune-managed endpoints. Azure SSE for SharePoint "
            "uses Microsoft-managed keys. FIPS 140-2 validation evidence for the full crypto stack is still being "
            "collected from Microsoft compliance portal exports for assessor package. "
            "Target: upload FIPS attestation bundle by 2026-08-01."
        ),
        "remediation_plan": "Download GCC High / commercial compliance artifacts; map to SC.L2-3.13.11 statement.",
        "estimated_cost": "1200",
    },
    "IR.L2-3.6.1": {
        "status": "PLANNED",
        "note": (
            "Draft Incident Response Plan v2.1 covers CUI spillage, ransomware, and DIB notification timelines. "
            "Tabletop exercise not yet performed in 2026. ISO scheduled Q3 tabletop with MSP and legal review "
            "of DFARS 7012 72-hour reporting clause."
        ),
        "remediation_plan": "Finalize IRP v2.1; conduct tabletop; attach attendance sheet.",
        "estimated_cost": "3500",
    },
    "AU.L2-3.3.1": {
        "status": "IN PROGRESS",
        "note": (
            "Audit records from Entra ID, SharePoint, and FortiGate are forwarded to the MSP SIEM workspace with "
            "180-day retention. Monthly review checklist exists but Q2 2026 privileged-access review log is incomplete — "
            "three admin role assignments lack matching ticket references. "
            "Remediation: complete Q2 review export and attach to AU evidence folder by 2026-08-15."
        ),
        "remediation_plan": "Close Q2 privileged-access review; automate missing-ticket alerts in SIEM.",
        "estimated_cost": "2800",
    },
    "CM.L2-3.4.1": {
        "status": "IN PROGRESS",
        "note": (
            "Intune baseline Win11-CUI-v4 is assigned to 27 of 45 endpoints. Remaining 18 devices are pending "
            "hardware refresh or awaiting maintenance window. Asset inventory in CMDB documents gold image hash "
            "SHA256:9f3a… per build record BR-2026-04."
        ),
        "remediation_plan": "Complete baseline deployment; close exceptions in POA&M weekly.",
        "estimated_cost": "6000",
    },
}

_FAMILY_NARRATIVE = {
    "Access Control": (
        "Apex implements {name} within the CUI enclave using Microsoft Entra ID groups, SharePoint permission "
        "levels, and Conditional Access. Access approvals are tracked in ticket queue SEC-{cid}. "
        "The ISO reviews {family} controls quarterly; last review 2026-Q1. "
        "Evidence: Entra audit logs (90-day retention), access review export, SOP-AC series."
    ),
    "Awareness and Training": (
        "All users with CUI access complete annual cyber awareness (DoW CUI training) and role-based modules "
        "within 30 days of hire. {name} is documented in LMS course APEX-CUI-AT. "
        "Completion records are exported monthly to HR compliance folder. "
        "Evidence: LMS completion report, training roster, onboarding checklist."
    ),
    "Audit and Accountability": (
        "Audit records for {name} are generated from Entra ID, SharePoint audit log, and FortiGate syslog "
        "forwarded to the organization's SIEM workspace (retention 180 days). "
        "Alert rules notify the ISO for privileged role changes. "
        "Evidence: sample log extract LOG-{cid}, SIEM rule export, retention policy screenshot."
    ),
    "Configuration Management": (
        "Configuration baselines for endpoints are defined in Intune configuration profile Win11-CUI-v4. "
        "{name} is verified during monthly vulnerability scan cycle and change tickets CHG-{cid}. "
        "Deviations require ISO approval. Evidence: Intune compliance report, change record, baseline export."
    ),
    "Identification and Authentication": (
        "Authentication for CUI systems is centralized in Entra ID with password policy ENTRA-PW-14 "
        "(14 char, complexity, lockout). {name} applies to all in-scope identities. "
        "Service accounts use managed identities where possible. Evidence: CA policy export, password policy, sample sign-in log."
    ),
    "Incident Response": (
        "Apex maintains Incident Response Plan v2.1 (draft) covering {name}. Reporting path: user → helpdesk → "
        "ISO → executive within 1 hour for confirmed CUI incidents. "
        "Evidence: IRP section mapping, ticket template INC-CUI, contact tree."
    ),
    "Maintenance": (
        "Maintenance on CUI systems follows change control SOP-MAINT-01. Remote vendor access uses time-bound "
        "Entra guest accounts. {name} is satisfied through approved maintenance windows and logging. "
        "Evidence: maintenance log, vendor access ticket, session recording where applicable."
    ),
    "Media Protection": (
        "CUI at rest resides only in GCC SharePoint libraries; portable media is prohibited by policy POL-MP-03. "
        "{name} is enforced via DLP rule DLP-CUI-USB block and BitLocker on endpoints. "
        "Evidence: DLP policy export, BitLocker compliance report, media sanitization record."
    ),
    "Personnel Security": (
        "HR completes background screening per contract DD254 before CUI access. {name} is documented in "
        "onboarding checklist HR-CUI-01 with termination same-day access revocation via Entra workflow. "
        "Evidence: sample redacted HR file, offboarding ticket, access disable timestamp."
    ),
    "Physical Protection": (
        "CUI processing occurs at Apex HQ (Badge access) and remote telework on approved managed devices only. "
        "{name} is addressed through facility badge logs and clean-desk policy for printed CUI (rare). "
        "Evidence: visitor log sample, badge access report, physical security SOP."
    ),
    "Risk Assessment": (
        "Annual risk assessment RA-2026 documents threats to the CUI enclave including phishing, supply chain, "
        "and insider risk. {name} findings are tracked in POA&M. "
        "Evidence: risk register excerpt, assessment memo, POA&M linkage RA-{cid}."
    ),
    "Security Assessment": (
        "Internal self-assessment against NIST 800-171 Rev 2 is performed annually using this tool and "
        "independent spot checks by MSP. {name} is reviewed by ISO and system owner each quarter. "
        "Evidence: assessment results, POA&M, meeting minutes."
    ),
    "System and Communications Protection": (
        "Network boundaries are enforced at FortiGate edge and Entra application proxy for admin tasks. "
        "Encryption in transit uses TLS 1.2+; CUI SharePoint uses Microsoft platform encryption. "
        "{name} — see network diagram and crypto standard STD-SC-01. Evidence: firewall rule export, TLS scan, architecture diagram."
    ),
    "System and Information Integrity": (
        "Defender for Business provides AV/EDR on endpoints; vulnerability scans run monthly (Tenable.io agent). "
        "{name} is monitored via SIEM alerts and patch compliance in Intune. "
        "Critical patches applied within 14 days. Evidence: scan report, patch compliance, ticket PATCH-{cid}."
    ),
}


def get_demo_org_profile() -> Dict[str, str]:
    return {
        "org_name": DEMO_ORG_NAME,
        "system_name": "Apex CUI Enclave (Microsoft 365 GCC + Managed Endpoints)",
        "system_unique_id": "APEX-ENCLAVE-001",
        "system_description": (
            "Apex Defense Manufacturing LLC engineers and manufactures subassemblies for DoW programs. "
            "The Apex CUI Enclave is a cloud-first environment where controlled technical data (CUI) "
            "is stored and shared among approximately 45 engineers, program managers, and quality staff. "
            "Primary CUI repositories are SharePoint Online (GCC) libraries; identity and device management "
            "are provided by Microsoft Entra ID and Intune. There are no on-premises servers processing CUI."
        ),
        "architecture_summary": (
            "Users authenticate to Microsoft Entra ID (GCC) with Conditional Access requiring compliant "
            "Intra ID-joined or Entra hybrid-joined Windows 11 devices for CUI access. CUI documents reside "
            "in SharePoint site collection APEX-CUI-ENG with sensitivity labels. Remote engineers connect "
            "via FortiGate SSL-VPN into the corporate network before accessing cloud services; VPN sessions "
            "require MFA. Security telemetry flows to Microsoft Defender and exported sign-in logs; FortiGate "
            "syslog is retained 180 days. See topology diagram in System Environment section."
        ),
        "boundary_description": (
            "The authorization boundary includes: Entra ID tenant (GCC), Intune-managed endpoints accessing "
            "CUI, SharePoint CUI site collection, Azure AD sign-in and audit logs, FortiGate VPN concentrator "
            "when used for CUI access, and administrative workstations used to manage the enclave. "
            "Explicitly out of scope: corporate HR/payroll (SAP), manufacturing OT networks without CUI, "
            "and visitor guest Wi-Fi."
        ),
        "org_address": "1200 Industrial Park Drive, Dayton, OH 45417",
        "org_phone": "(937) 555-0142",
        "system_owner": "Jordan Lee, VP Operations",
        "iso_name": "Sam Rivera, IT Security Lead",
        "sysadmin_name": "Alex Kim, Systems Administrator",
        "network_admin_name": "Alex Kim, Systems Administrator",
        "auditor_name": "Internal assessment team (Apex ISO)",
        "hardware_inventory": (
            "In-scope hardware (see CMDB export CMDB-APEX-2026-Q1): "
            "42 × Dell Latitude 5540 laptops (Windows 11 23H2, Intune-managed); "
            "3 × Dell Precision workstations (engineering CAD, CUI-capable); "
            "2 × Fortinet FortiGate FG-60F (edge firewall/VPN, firmware 7.4.3); "
            "1 × Hyper-V host (legacy file print — out of scope for CUI); "
            "Azure GCC: Entra ID, Exchange Online, SharePoint Online (no customer-managed VMs). "
            "OT programming station OT-PLC-02 (legacy, segmented — see POA&M AC.L2-3.1.8)."
        ),
        "software_inventory": (
            "Microsoft 365 GCC: Entra ID P1, Exchange Online, SharePoint Online, Teams; "
            "Microsoft Defender for Business; Microsoft Intune; "
            "Azure AD Connect v2.0.28.0 (read-only sync from on-prem AD for corporate accounts); "
            "FortiOS 7.4.3; Tenable.io agent (vulnerability scanning); "
            "Engineering: SolidWorks 2024 (CUI drawings exported to SharePoint only). "
            "Full software inventory spreadsheet: \\\\fileserver\\ISO\\Inventory\\SW-INV-2026.xlsx"
        ),
        "hw_sw_org_owned": "Yes — all in-scope hardware is owned by Apex; cloud services are contractor-operated GCC subscriptions under Apex tenant.",
        "header_short_name": "Apex Defense Mfg",
    }


def get_demo_asset_scope() -> Dict[str, int]:
    return {
        "CUI Assets": 100,
        "Security Protection Assets": 85,
        "Contractor Risk Managed Assets": 15,
        "Out-of-Scope Assets": 25,
    }


def _met_narrative(cid: str, info: dict) -> str:
    family = info["family"]
    template = _FAMILY_NARRATIVE.get(
        family,
        (
            "Apex addresses {name} through documented policies and technical controls in the CUI enclave. "
            "Implementation details are maintained by the ISO and reviewed quarterly. "
            "Evidence: SOP-{cid}, configuration export, assessment record."
        ),
    )
    return template.format(name=info["name"], family=family, cid=cid[-7:])


def get_demo_answers() -> Dict[str, Any]:
    answers = {}
    for cid, info in CMMC_FRAMEWORK.items():
        ans = default_control_answer()
        ans["status"] = "MET"
        ans["maturity"] = "Implemented"
        ans["implementation_narrative"] = _met_narrative(cid, info)
        ans["examine"] = f"SOP-{info['family'][:2].upper()}-{cid[-7:]}.pdf; config export; Entra/Intune screenshot"
        ans["interview"] = "Sam Rivera (ISO), Alex Kim (SysAdmin)"
        ans["test"] = f"Sample ticket / log review Q1-2026 — {cid}"
        ans["owner"] = "Sam Rivera"
        answers[cid] = ans

    for cid, gap in DEMO_GAPS.items():
        answers[cid]["status"] = gap["status"]
        answers[cid]["implementation_narrative"] = gap["note"]
        answers[cid]["assessor_notes"] = gap["note"]
        answers[cid]["remediation_plan"] = gap.get("remediation_plan", "")
        answers[cid]["owner"] = "Sam Rivera"
        answers[cid]["target_date"] = "2026-09-30"
        answers[cid]["estimated_cost"] = gap.get("estimated_cost", "5000")
        if gap["status"] in ("NOT MET", "PARTIALLY MET", "IN PROGRESS", "PLANNED"):
            answers[cid]["likelihood"] = "Medium"
            answers[cid]["impact"] = "High" if CMMC_FRAMEWORK[cid]["weight"] >= 5 else "Medium"

    return answers


def _demo_topology_bytes() -> bytes:
    for base in _ASSET_DIRS:
        path = base / "demo_topology.png"
        if path.is_file():
            return path.read_bytes()

    # Dev-only fallback: generate PNG when scripts/ is present
    for gen_path in (
        _PLATFORM_ROOT / "scripts" / "generate_demo_assets.py",
        Path(__file__).resolve().parent / "scripts" / "generate_demo_assets.py",
    ):
        if gen_path.is_file():
            import importlib.util

            out_path = _ASSET_DIRS[0] / "demo_topology.png"
            spec = importlib.util.spec_from_file_location("generate_demo_assets", gen_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.generate_topology_png(out_path)
            return out_path.read_bytes()

    raise FileNotFoundError(
        "demo_topology.png not found. Expected in samples/ or docs/samples/ "
        "(submission package should include samples/demo_topology.png)."
    )


def _demo_appendix_bytes() -> Dict[str, bytes]:
    irp = (
        "APEX DEFENSE MANUFACTURING LLC — INCIDENT RESPONSE PLAN (EXCERPT / DEMO)\n"
        "Version 2.1 draft | CUI enclave\n\n"
        "1. Purpose\n"
        "Define roles and steps for CUI security incidents including spillage, unauthorized access, "
        "and ransomware affecting SharePoint CUI libraries or Entra ID.\n\n"
        "2. Reporting\n"
        "Users report to helpdesk@apexdefense.example within 15 minutes. ISO assesses within 1 hour. "
        "Executive notification for confirmed CUI incidents. DFARS 7012 consideration within 72 hours.\n\n"
        "3. Contacts\n"
        "ISO: Sam Rivera | System Owner: Jordan Lee | MSP: Northline Cyber SOC\n"
    )
    acm = (
        "APEX CUI ACCESS CONTROL MATRIX (EXCERPT / DEMO)\n"
        "SharePoint site: APEX-CUI-ENG\n\n"
        "Role: Engineer — Read/Write CUI libraries; no admin\n"
        "Role: Program Manager — Read/Write; approval workflow\n"
        "Role: Quality — Read only\n"
        "Role: ISO — Full control + audit\n"
        "Guest access prohibited without ISO approval ticket.\n"
    )
    return {
        "appendix:Apex_IR_Plan_Draft.txt": irp.encode("utf-8"),
        "appendix:Apex_Access_Control_Matrix.txt": acm.encode("utf-8"),
    }


def get_demo_org_assets() -> Dict[str, Any]:
    return {
        "topology_filename": "demo_topology.png",
        "appendix_files": [
            {"filename": "Apex_IR_Plan_Draft.txt", "label": "Incident Response Plan v2.1 (draft excerpt)"},
            {"filename": "Apex_Access_Control_Matrix.txt", "label": "Access Control Matrix — CUI SharePoint"},
        ],
    }


def get_demo_org_asset_bytes() -> Dict[str, bytes]:
    blobs: Dict[str, bytes] = {}
    set_topology_bytes(blobs, "demo_topology.png", _demo_topology_bytes())
    for key, data in _demo_appendix_bytes().items():
        blobs[key] = data
    return blobs


def get_demo_env_scope() -> Dict[str, str]:
    return {
        "processes_cui": "yes",
        "uses_wireless": "yes",
        "remote_workforce": "yes",
        "uses_m365": "yes",
        "uses_google": "no",
        "cloud_hosting": "azure",
    }


def get_demo_org_inventory() -> Dict[str, Any]:
    from org_inventory import set_inventory_assets

    return set_inventory_assets(
        [
            {
                "asset_name": "APEX-LT-042",
                "asset_type": "Laptop",
                "in_scope": "yes",
                "cui": "yes",
                "owner": "Engineering",
                "location": "HQ",
                "notes": "CUI engineering workstation",
            },
            {
                "asset_name": "APEX-LT-017",
                "asset_type": "Laptop",
                "in_scope": "yes",
                "cui": "yes",
                "owner": "Program Management",
                "location": "HQ",
                "notes": "",
            },
            {
                "asset_name": "MacBook-Pro-ISO",
                "asset_type": "Laptop",
                "in_scope": "yes",
                "cui": "no",
                "owner": "ISO",
                "location": "HQ",
                "notes": "Security team",
            },
            {
                "asset_name": "APEX-VM-DEV01",
                "asset_type": "Server",
                "in_scope": "yes",
                "cui": "yes",
                "owner": "IT",
                "location": "Azure",
                "notes": "CUI dev environment",
            },
            {
                "asset_name": "APEX-LT-099",
                "asset_type": "Laptop",
                "in_scope": "yes",
                "cui": "no",
                "owner": "Quality",
                "location": "HQ",
                "notes": "Not yet enrolled in Intune (demo gap)",
            },
        ]
    )


def get_demo_session_payload() -> Dict[str, Any]:
    return {
        "org_name": DEMO_ORG_NAME,
        "org_profile": get_demo_org_profile(),
        "asset_scope": get_demo_asset_scope(),
        "answers": get_demo_answers(),
        "scoped_controls": list(CMMC_FRAMEWORK.keys()),
        "org_assets": get_demo_org_assets(),
        "org_asset_bytes": get_demo_org_asset_bytes(),
        "org_inventory": get_demo_org_inventory(),
        "env_scope": get_demo_env_scope(),
    }
