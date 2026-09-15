"""Organization and system profile for SOC 2 assessment."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


CONTROL_STATUS_VALUES = (
    "NOT STARTED",
    "IN PROGRESS",
    "PLANNED",
    "PARTIALLY MET",
    "NOT MET",
    "MET",
    "NOT APPLICABLE",
    "INHERITED",
)


def default_org_profile(org_name: str = "") -> Dict[str, str]:
    return {
        "org_name": org_name,
        "system_name": "",
        "system_description": "",
        "architecture_summary": "",
        "boundary_description": "",
        "system_owner": "",
        "compliance_officer": "",
        "it_admin": "",
        "auditor_name": "",
        "system_unique_id": "",
        "org_address": "",
        "org_phone": "",
        "header_short_name": "",
        "hardware_inventory": "",
        "software_inventory": "",
        "team_roster": "",
        "subservice_organizations": "",
        "reporting_method": "",
        "user_entity_controls": "",
    }


def merge_org_profile(stored: Dict[str, Any] | None, org_name: str = "") -> Dict[str, str]:
    profile = default_org_profile(org_name)
    if stored:
        profile.update({k: v for k, v in stored.items() if k in profile and v is not None})
    if org_name and not profile.get("org_name"):
        profile["org_name"] = org_name
    return profile


FIELD_LABELS = {
    "org_name": "Organization name",
    "system_name": "System name",
    "system_description": "System description",
    "architecture_summary": "Architecture summary",
    "boundary_description": "System boundary",
    "system_owner": "System owner",
    "compliance_officer": "Compliance officer",
    "it_admin": "IT administrator",
    "auditor_name": "Auditor",
    "system_unique_id": "System ID",
    "org_address": "Address",
    "org_phone": "Phone",
    "header_short_name": "Short name",
    "hardware_inventory": "Hardware inventory",
    "software_inventory": "Software inventory",
    "team_roster": "Team roster",
    "subservice_organizations": "Subservice Organizations (CUEC/CSOC)",
    "reporting_method": "Reporting Method (carve-out / inclusive)",
    "user_entity_controls": "User Entity Controls (CUEC)",
}

FIELD_PLACEHOLDERS = {
    "org_name": "Acme Corp",
    "system_name": "Production SaaS Platform",
    "system_description": "Cloud-hosted SaaS platform serving enterprise customers...",
    "architecture_summary": "AWS us-east-1, EKS cluster, RDS PostgreSQL, CloudFront CDN...",
    "boundary_description": "All production infrastructure in AWS us-east-1...",
    "system_owner": "Jane Smith, CTO",
    "compliance_officer": "John Doe",
    "it_admin": "Alice Johnson",
    "auditor_name": "External Audit Firm",
    "system_unique_id": "SYS-001",
    "org_address": "123 Main St, City, State 12345",
    "org_phone": "+1-555-0100",
    "header_short_name": "ACME",
    "hardware_inventory": "AWS EC2, RDS, ELB...",
    "software_inventory": "Kubernetes, PostgreSQL, Redis...",
    "team_roster": "Jane Smith (CTO), John Doe (Compliance), Alice Johnson (IT)...",
    "subservice_organizations": "AWS (IaaS), Auth0 (IAM), Datadog (Monitoring)",
    "reporting_method": "carve-out",
    "user_entity_controls": "Users must maintain access reviews, complete security training, and report incidents within 24 hours.",
}

WIZARD_STEPS = [
    {"key": "identity", "label": "Organization Identity", "fields": ["org_name", "system_name"]},
    {"key": "description", "label": "System Description", "fields": ["system_description"]},
    {"key": "architecture", "label": "Architecture", "fields": ["architecture_summary"]},
    {"key": "boundary", "label": "System Boundary", "fields": ["boundary_description"]},
    {"key": "environment", "label": "Environment", "fields": []},
    {"key": "roles", "label": "Team & Roles", "fields": ["system_owner", "compliance_officer", "it_admin", "auditor_name"]},
    {"key": "subservice", "label": "Subservice Organizations", "fields": ["subservice_organizations", "reporting_method"]},
    {"key": "cuec", "label": "User Entity Controls (CUEC)", "fields": ["user_entity_controls"]},
]


def profile_needs_wizard(org_profile: Dict[str, str]) -> bool:
    if not org_profile.get("org_name") or org_profile["org_name"] in ("", "Your Organization"):
        return True
    filled = sum(1 for k in ("system_description", "architecture_summary", "boundary_description") if (org_profile.get(k) or "").strip())
    return filled < 2
