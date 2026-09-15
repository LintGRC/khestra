"""Profile wizard constants — no Streamlit."""

from typing import Dict, List

WIZARD_STEPS: List[Dict] = [
    {
        "id": "identity",
        "title": "Organization identity",
        "caption": "Names that appear on your SSP cover page.",
        "fields": ["org_name", "system_name"],
    },
    {
        "id": "description",
        "title": "What the system does",
        "caption": "Help auditors understand purpose, users, and CUI.",
        "fields": ["system_description"],
    },
    {
        "id": "architecture",
        "title": "Architecture",
        "caption": "Cloud, on-prem, identity provider, endpoints — high level is fine.",
        "fields": ["architecture_summary"],
    },
    {
        "id": "boundary",
        "title": "System boundary",
        "caption": "What's in scope vs out of scope for this assessment.",
        "fields": ["boundary_description"],
    },
    {
        "id": "environment",
        "title": "Environment & scope",
        "caption": "Wireless, remote work, M365, and cloud — helps suggest N/A and flag contradictions.",
        "fields": [],
    },
    {
        "id": "roles",
        "title": "Key roles",
        "caption": "Who owns the system and security responsibilities.",
        "fields": ["system_owner", "iso_name", "sysadmin_name", "network_admin_name", "auditor_name"],
    },
]

FIELD_LABELS = {
    "org_name": "Organization name",
    "system_name": "System name",
    "system_description": "System description",
    "architecture_summary": "Architecture summary",
    "boundary_description": "System boundary",
    "system_owner": "System owner",
    "iso_name": "Information security officer",
    "sysadmin_name": "System administrator",
    "network_admin_name": "Network administrator",
    "auditor_name": "Assessor / auditor",
}

FIELD_PLACEHOLDERS = {
    "org_name": "Acme Defense LLC",
    "system_name": "CUI Enclave (e.g. M365 + Azure)",
    "system_description": "Who uses the system, what CUI is processed, primary business purpose…",
    "architecture_summary": "Entra ID, SharePoint, Intune endpoints, VPN, etc.",
    "boundary_description": "In-scope: … Out-of-scope: payroll, public website…",
    "system_owner": "Name, title",
    "iso_name": "Name, title",
    "sysadmin_name": "Name or team",
    "network_admin_name": "Name or team",
    "auditor_name": "Internal assessor or consultant",
}


def profile_needs_wizard(org_profile: Dict[str, str]) -> bool:
    name = (org_profile.get("org_name") or "").strip().lower()
    if not name or name in ("your organization", "organization"):
        return True
    filled = sum(
        1
        for k in ("system_description", "architecture_summary", "boundary_description")
        if (org_profile.get(k) or "").strip()
    )
    return filled < 2
