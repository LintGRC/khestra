"""Application constants and role configuration."""

from org_profile import CONTROL_STATUS_VALUES

APP_TITLE = "CMMC"
APP_VERSION = "0.1.0"
MAX_FILE_SIZE_MB = 10

STATUS_OPTIONS = list(CONTROL_STATUS_VALUES)


def status_option_index(status: str) -> int:
    normalized = (status or "NOT STARTED").strip().upper()
    try:
        return STATUS_OPTIONS.index(normalized)
    except ValueError:
        return 0


MATURITY_LEVELS = ["Ad Hoc", "Documented", "Implemented", "Managed", "Optimized"]
SEVERITY_LEVELS = ["Critical", "High", "Moderate", "Low"]
LIKELIHOOD_LEVELS = ["Low", "Medium", "High", "Critical"]
IMPACT_LEVELS = ["Low", "Medium", "High", "Critical"]
USER_ROLES = ["Organization Admin", "Compliance Manager", "Assessor", "Engineer", "Executive", "Auditor"]
ROLE_DISPLAY = {
    "Organization Admin": "Organization Admin",
    "Compliance Manager": "Compliance Manager",
    "Assessor": "Assessor",
    "Engineer": "Contributor",
    "Executive": "Viewer",
    "Auditor": "Auditor",
}
ROLE_BY_DISPLAY = {v: k for k, v in ROLE_DISPLAY.items()}

FAMILY_MAPPING = {
    "01. Access Control": "Access Control",
    "02. Awareness & Training": "Awareness and Training",
    "03. Audit & Accountability": "Audit and Accountability",
    "04. Configuration Management": "Configuration Management",
    "05. Identification & Authentication": "Identification and Authentication",
    "06. Incident Response": "Incident Response",
    "07. Maintenance": "Maintenance",
    "08. Media Protection": "Media Protection",
    "09. Personnel Security": "Personnel Security",
    "10. Physical Protection": "Physical Protection",
    "11. Risk Assessment": "Risk Assessment",
    "12. Security Assessment": "Security Assessment",
    "13. System & Communications": "System and Communications Protection",
    "14. System & Information Integrity": "System and Information Integrity",
}

ASSET_TYPES = {
    "CUI Assets": "Percent of environment that stores or processes CUI — 100% = full Level 2 scope",
    "Security Protection Assets": "Percent protected by security mechanisms (e.g. firewalls, EDR)",
    "Contractor Risk Managed Assets": "Percent under contractor risk-managed policies",
    "Out-of-Scope Assets": "Percent explicitly excluded from this assessment",
}

CONTROL_DEPENDENCIES = {
    "IA.L2-3.5.3": ["AC.L2-3.1.12", "AC.L2-3.1.13", "SC.L2-3.13.8"],
    "SC.L2-3.13.8": ["MP.L2-3.8.6", "SC.L2-3.13.16"],
    "AU.L2-3.3.1": ["SI.L2-3.14.4", "IR.L2-3.6.2"],
    "CM.L2-3.4.1": ["RA.L2-3.11.2", "SI.L2-3.14.6"],
}

VALIDATION_RULES = {
    "SC.L2-3.13.11": {
        "type": "config_file",
        "rules": [
            {"pattern": r"aes256-gcm|AES-256-GCM", "description": "FIPS-validated AES-256-GCM encryption"},
            {"pattern": r"fips_enabled\s*=\s*[1-9]", "description": "FIPS mode enabled"},
            {"pattern": r"tls-version\s*=\s*1\.3", "description": "TLS 1.3 enforced"},
        ],
        "file_types": [".conf", ".json", ".txt"],
    },
    "IA.L2-3.5.7": {
        "type": "password_policy",
        "rules": [
            {"pattern": r"minlength\s*=\s*1[4-9]|\d{2,}", "description": "Min length >= 14"},
            {"pattern": r"complexity\s*=\s*enabled", "description": "Complexity enabled"},
            {"pattern": r"history\s*=\s*2[4-9]|[3-9]\d", "description": "History >= 24"},
        ],
        "file_types": [".txt", ".ps1", ".json"],
    },
    "AC.L2-3.1.8": {
        "type": "threshold_check",
        "rules": [
            {"pattern": r"lockout-threshold\s*=\s*[1-5]", "description": "Lockout threshold <= 5"},
            {"pattern": r"reset-time\s*=\s*[1-9][0-9]|[1-2]\d{2}", "description": "Reset time >= 30 min"},
        ],
        "file_types": [".conf", ".xml", ".json"],
    },
}

ROLE_PERMISSIONS = {
    "Organization Admin": {"view_dashboard": True, "edit_controls": True, "approve_poam": True, "export_data": True, "manage_users": True, "manage_billing": True, "validate_evidence": True},
    "Compliance Manager": {"view_dashboard": True, "edit_controls": True, "approve_poam": True, "export_data": True, "manage_users": True, "manage_billing": False, "validate_evidence": True},
    "Assessor": {"view_dashboard": True, "edit_controls": True, "approve_poam": False, "export_data": True, "manage_users": False, "manage_billing": False, "validate_evidence": True},
    "Engineer": {
        "view_dashboard": False,
        "edit_controls": True,
        "approve_poam": False,
        "export_data": False,
        "manage_users": False,
        "manage_billing": False,
        "validate_evidence": True,
    },
    "Executive": {"view_dashboard": True, "edit_controls": False, "approve_poam": True, "export_data": True, "manage_users": False, "manage_billing": False, "validate_evidence": False},
    "Auditor": {"view_dashboard": True, "edit_controls": False, "approve_poam": True, "export_data": True, "manage_users": False, "manage_billing": False, "validate_evidence": False},
}
