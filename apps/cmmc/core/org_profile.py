"""Organization and system profile used in SSP/POA&M report generation."""

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
        "system_name": "CUI Information System",
        "system_description": "",
        "architecture_summary": "",
        "boundary_description": "",
        "system_owner": "",
        "system_owner_title": "",
        "iso_name": "",
        "iso_title": "",
        "sysadmin_name": "",
        "network_admin_name": "",
        "auditor_name": "",
        "system_unique_id": "",
        "cage_code": "",
        "uei": "",
        "org_address": "",
        "org_phone": "",
        "header_short_name": "",
        "gov_poc_name": "",
        "gov_poc_title": "",
        "gov_poc_address": "",
        "gov_poc_phone": "",
        "gov_poc_email": "",
        "poc_name": "",
        "poc_email": "",
        "poc_phone": "",
        "assessment_methodology": "Basic",
        "hardware_inventory": "",
        "software_inventory": "",
        "hw_sw_org_owned": "Yes",
        "team_roster": "",
        "board_resource_ask": "",
    }


def default_control_answer() -> Dict[str, Any]:
    return {
        "status": "NOT STARTED",
        "maturity": "Ad Hoc",
        "implementation_narrative": "",
        "human_edited": False,
        "examine": "",
        "interview": "",
        "test": "",
        "evidence": [],
        "assessor_notes": "",
        "remediation_plan": "",
        "owner": "",
        "target_date": "",
        "estimated_cost": "",
        "last_updated": "",
        "validation_passed": False,
        "likelihood": "Medium",
        "impact": "Medium",
        "comments": [],
        "linked_policies": [],
        "linked_assets": [],
        "linked_team": [],
        "objectives": [],
        "override_active": False,
        "override_justification": "",
        "fips_certificate_number": "",
        "cloud_authorization_status": "",
        "dfars_72hr_reporting_enabled": False,
    }


def merge_org_profile(stored: Dict[str, Any] | None, org_name: str = "") -> Dict[str, str]:
    profile = default_org_profile(org_name)
    if stored:
        profile.update({k: v for k, v in stored.items() if k in profile and v is not None})
    if org_name and not profile.get("org_name"):
        profile["org_name"] = org_name
    return profile


def merge_control_answer(stored: Dict[str, Any] | None) -> Dict[str, Any]:
    answer = default_control_answer()
    if stored:
        answer.update(stored)
    status = (answer.get("status") or "NOT STARTED").strip().upper()
    if status not in CONTROL_STATUS_VALUES:
        answer["status"] = "NOT STARTED"
    else:
        answer["status"] = status
    return answer
