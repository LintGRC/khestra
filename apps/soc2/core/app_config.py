"""SOC 2 app constants."""

APP_TITLE = "Khestra SOC 2"
APP_VERSION = "0.1.0"

STATUS_OPTIONS = [
    "NOT STARTED",
    "IN PROGRESS",
    "PLANNED",
    "PARTIALLY MET",
    "NOT MET",
    "MET",
    "NOT APPLICABLE",
    "INHERITED",
]

ROLE_PERMISSIONS = {
    "Organization Admin": {"edit_controls": True, "edit_org": True, "export_data": True, "manage_users": True, "view_dashboard": True},
    "Compliance Manager": {"edit_controls": True, "edit_org": True, "export_data": True, "view_dashboard": True},
    "Assessor": {"edit_controls": True, "edit_org": False, "export_data": True, "view_dashboard": True},
    "Engineer": {"edit_controls": True, "edit_org": False, "export_data": False, "view_dashboard": True, "validate_evidence": True},
    "Executive": {"edit_controls": False, "edit_org": False, "export_data": True, "view_dashboard": True},
    "Auditor": {"edit_controls": False, "edit_org": False, "export_data": True, "view_dashboard": True},
}

USER_ROLES = list(ROLE_PERMISSIONS.keys())

OPERATING_STATUS_OPTIONS = [
    "NOT TESTED",
    "PASS",
    "FAIL",
    "NEEDS REVIEW",
]

FREQUENCY_OPTIONS = [
    "",
    "Continuous",
    "Daily",
    "Weekly",
    "Monthly",
    "Quarterly",
    "Annually",
    "Ad-hoc",
]
