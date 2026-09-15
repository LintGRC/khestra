"""AI Governance app constants and role permissions."""

APP_TITLE = "Khestra AI Governance"
APP_VERSION = "0.1.0"

ROLE_PERMISSIONS = {
    "Organization Admin": {"edit_controls": True, "edit_org": True, "export_data": True, "manage_users": True, "view_dashboard": True},
    "Compliance Manager": {"edit_controls": True, "edit_org": True, "export_data": True, "view_dashboard": True},
    "Assessor": {"edit_controls": True, "edit_org": False, "export_data": True, "view_dashboard": True},
    "Engineer": {"edit_controls": True, "edit_org": False, "export_data": False, "view_dashboard": True},
    "Executive": {"edit_controls": False, "edit_org": False, "export_data": True, "view_dashboard": True},
    "Auditor": {"edit_controls": False, "edit_org": False, "export_data": True, "view_dashboard": True},
}

USER_ROLES = list(ROLE_PERMISSIONS.keys())
