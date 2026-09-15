"""Per-framework control→capability classification (Phase 1 contract A1).

Maps control IDs to one of the 27 open capability categories. This is
public-standards material — derivable from NIST SP 800-171, ISO 27001,
and the SOC 2 Trust Services Criteria.

Leak-test invariant: this module contains NO collector check ids and
NO check→control pairs. It holds control→capability mappings only.
"""

from __future__ import annotations

from typing import Dict

# CMMC / NIST SP 800-171 Rev 2 control→capability mapping.
# Derived from control families and specific control content.
CMMC_CONTROL_CAPABILITIES: Dict[str, str] = {
    # Access Control
    "AC.L2-3.1.1": "Access Control",
    "AC.L2-3.1.2": "Access Control",
    "AC.L2-3.1.3": "Data Protection",
    "AC.L2-3.1.4": "Access Control",
    "AC.L2-3.1.5": "Access Control",
    "AC.L2-3.1.6": "Access Control",
    "AC.L2-3.1.7": "Access Control",
    "AC.L2-3.1.8": "Password Policy",
    "AC.L2-3.1.9": "Access Control",
    "AC.L2-3.1.10": "Access Control",
    "AC.L2-3.1.11": "Access Control",
    "AC.L2-3.1.12": "Network Security",
    "AC.L2-3.1.13": "Encryption in Transit",
    "AC.L2-3.1.14": "Network Security",
    "AC.L2-3.1.15": "Access Control",
    "AC.L2-3.1.16": "Network Security",
    "AC.L2-3.1.17": "Network Security",
    "AC.L2-3.1.18": "Device Management",
    "AC.L2-3.1.19": "Encryption at Rest",
    "AC.L2-3.1.20": "Access Control",
    "AC.L2-3.1.21": "Data Protection",
    "AC.L2-3.1.22": "Data Protection",

    # Awareness and Training
    "AT.L2-3.2.1": "Personnel & HR",
    "AT.L2-3.2.2": "Personnel & HR",
    "AT.L2-3.2.3": "Security Operations",

    # Audit and Accountability
    "AU.L2-3.3.1": "Logging & Monitoring",
    "AU.L2-3.3.2": "Logging & Monitoring",
    "AU.L2-3.3.3": "Logging & Monitoring",
    "AU.L2-3.3.4": "Detection & SIEM",
    "AU.L2-3.3.5": "Detection & SIEM",
    "AU.L2-3.3.6": "Logging & Monitoring",
    "AU.L2-3.3.7": "Logging & Monitoring",
    "AU.L2-3.3.8": "Logging & Monitoring",
    "AU.L2-3.3.9": "Logging & Monitoring",

    # Configuration Management
    "CM.L2-3.4.1": "IT Asset Inventory",
    "CM.L2-3.4.2": "Security Operations",
    "CM.L2-3.4.3": "Security Operations",
    "CM.L2-3.4.4": "Security Operations",
    "CM.L2-3.4.5": "Security Operations",
    "CM.L2-3.4.6": "Security Operations",
    "CM.L2-3.4.7": "Endpoint Protection",
    "CM.L2-3.4.8": "Endpoint Protection",
    "CM.L2-3.4.9": "Endpoint Protection",

    # Identification and Authentication
    "IA.L2-3.5.1": "Password Policy",
    "IA.L2-3.5.2": "MFA",
    "IA.L2-3.5.3": "MFA",
    "IA.L2-3.5.4": "Identity & Access",
    "IA.L2-3.5.5": "Identity & Access",
    "IA.L2-3.5.6": "Identity & Access",
    "IA.L2-3.5.7": "Password Policy",
    "IA.L2-3.5.8": "Identity & Access",
    "IA.L2-3.5.9": "Identity & Access",
    "IA.L2-3.5.10": "Identity & Access",
    "IA.L2-3.5.11": "Identity & Access",

    # Incident Response
    "IR.L2-3.6.1": "Incident Response",
    "IR.L2-3.6.2": "Incident Response",
    "IR.L2-3.6.3": "Incident Response",

    # Maintenance
    "MA.L2-3.7.1": "Vulnerability Management",
    "MA.L2-3.7.2": "Vulnerability Management",
    "MA.L2-3.7.3": "Vulnerability Management",
    "MA.L2-3.7.4": "Vulnerability Management",
    "MA.L2-3.7.5": "Vulnerability Management",
    "MA.L2-3.7.6": "Vulnerability Management",

    # Media Protection
    "MP.L2-3.8.1": "Data Protection",
    "MP.L2-3.8.2": "Data Protection",
    "MP.L2-3.8.3": "Data Protection",
    "MP.L2-3.8.4": "Data Protection",
    "MP.L2-3.8.5": "Data Protection",
    "MP.L2-3.8.6": "Data Protection",
    "MP.L2-3.8.7": "Data Protection",
    "MP.L2-3.8.8": "Data Protection",
    "MP.L2-3.8.9": "Data Protection",

    # Personnel Security
    "PS.L2-3.9.1": "Personnel & HR",
    "PS.L2-3.9.2": "Personnel & HR",

    # Physical Protection
    "PE.L2-3.10.1": "Network Security",
    "PE.L2-3.10.2": "Network Security",
    "PE.L2-3.10.3": "Network Security",
    "PE.L2-3.10.4": "Network Security",
    "PE.L2-3.10.5": "Network Security",
    "PE.L2-3.10.6": "Network Security",

    # Risk Assessment
    "RA.L2-3.11.1": "Vulnerability Management",
    "RA.L2-3.11.2": "Vulnerability Management",
    "RA.L2-3.11.3": "Vulnerability Management",

    # Security Assessment
    "CA.L2-3.12.1": "Security Operations",
    "CA.L2-3.12.2": "Security Operations",
    "CA.L2-3.12.3": "Security Operations",
    "CA.L2-3.12.4": "Security Operations",

    # System and Communications Protection
    "SC.L2-3.13.1": "Encryption in Transit",
    "SC.L2-3.13.2": "Encryption in Transit",
    "SC.L2-3.13.3": "Encryption in Transit",
    "SC.L2-3.13.4": "Encryption in Transit",
    "SC.L2-3.13.5": "Encryption in Transit",
    "SC.L2-3.13.6": "Encryption in Transit",
    "SC.L2-3.13.7": "Encryption in Transit",
    "SC.L2-3.13.8": "Encryption in Transit",
    "SC.L2-3.13.9": "Web Application Security",
    "SC.L2-3.13.10": "Web Application Security",
    "SC.L2-3.13.11": "Web Application Security",
    "SC.L2-3.13.12": "Encryption in Transit",
    "SC.L2-3.13.13": "Encryption at Rest",
    "SC.L2-3.13.14": "Encryption at Rest",
    "SC.L2-3.13.15": "Cloud Security Posture",
    "SC.L2-3.13.16": "Cloud Security Posture",

    # System and Information Integrity
    "SI.L2-3.14.1": "Vulnerability Management",
    "SI.L2-3.14.2": "Vulnerability Management",
    "SI.L2-3.14.3": "Endpoint Protection",
    "SI.L2-3.14.4": "Endpoint Protection",
    "SI.L2-3.14.5": "Endpoint Protection",
    "SI.L2-3.14.6": "Endpoint Protection",
    "SI.L2-3.14.7": "Endpoint Protection",
}

# SOC 2 TSC criteria→capability mapping (key criteria only).
SOC2_CONTROL_CAPABILITIES: Dict[str, str] = {
    "CC1.1": "Personnel & HR",
    "CC1.2": "Personnel & HR",
    "CC1.3": "Personnel & HR",
    "CC1.4": "Personnel & HR",
    "CC1.5": "Personnel & HR",
    "CC2.1": "Logging & Monitoring",
    "CC2.2": "Logging & Monitoring",
    "CC3.1": "Security Operations",
    "CC3.2": "Security Operations",
    "CC4.1": "Security Operations",
    "CC5.1": "Access Control",
    "CC6.1": "Access Control",
    "CC6.2": "Identity & Access",
    "CC6.3": "MFA",
    "CC6.6": "Network Security",
    "CC6.7": "Encryption in Transit",
    "CC7.1": "Detection & SIEM",
    "CC7.2": "Detection & SIEM",
    "CC7.3": "Detection & SIEM",
    "CC7.4": "Incident Response",
    "CC7.5": "Incident Response",
    "CC8.1": "Security Operations",
    "CC9.1": "Network Security",
    "CC9.2": "Encryption at Rest",
    "A1.1": "Backup & Recovery",
    "A1.2": "Backup & Recovery",
    "C1.1": "Encryption at Rest",
    "PI1.1": "Data Protection",
    "PI1.2": "Data Protection",
    "P1.1": "Data Protection",
}

# ISO 27001 Annex A→capability mapping (key controls).
ISO27001_CONTROL_CAPABILITIES: Dict[str, str] = {
    "A.5.1": "Security Operations",
    "A.5.2": "Security Operations",
    "A.6.1": "Personnel & HR",
    "A.6.2": "Personnel & HR",
    "A.6.3": "Personnel & HR",
    "A.7.1": "Network Security",
    "A.7.2": "Network Security",
    "A.8.1": "IT Asset Inventory",
    "A.8.2": "Access Control",
    "A.8.3": "Access Control",
    "A.8.4": "Access Control",
    "A.8.5": "MFA",
    "A.8.6": "Identity & Access",
    "A.8.7": "Endpoint Protection",
    "A.8.8": "Endpoint Protection",
    "A.8.9": "Logging & Monitoring",
    "A.8.10": "Encryption at Rest",
    "A.8.11": "Encryption at Rest",
    "A.8.12": "Encryption in Transit",
    "A.8.13": "Encryption in Transit",
    "A.8.14": "Logging & Monitoring",
    "A.8.15": "Logging & Monitoring",
    "A.8.16": "Detection & SIEM",
    "A.8.20": "Network Security",
    "A.8.21": "Network Security",
    "A.8.22": "Web Application Security",
    "A.8.23": "Web Application Security",
    "A.8.24": "Encryption in Transit",
    "A.8.25": "Security Operations",
    "A.8.26": "Security Operations",
    "A.8.27": "Security Operations",
    "A.8.28": "Security Operations",
    "A.8.29": "Security Operations",
    "A.8.30": "Security Operations",
    "A.8.31": "Security Operations",
    "A.8.32": "Security Operations",
    "A.8.33": "Logging & Monitoring",
    "A.8.34": "Logging & Monitoring",
}

# Framework selector
_FRAMEWORK_MAP = {
    "cmmc": CMMC_CONTROL_CAPABILITIES,
    "soc2": SOC2_CONTROL_CAPABILITIES,
    "iso27001": ISO27001_CONTROL_CAPABILITIES,
}


def capability_for_control(framework: str, control_id: str) -> str:
    """Return the capability category for a control in a given framework.

    Returns "Uncategorized" if the control is not mapped.
    """
    caps = _FRAMEWORK_MAP.get(framework.lower(), {})
    return caps.get(control_id, "Uncategorized")


def controls_for_capability(framework: str, capability: str) -> list[str]:
    """Return all control IDs mapped to a given capability in a framework."""
    caps = _FRAMEWORK_MAP.get(framework.lower(), {})
    return [cid for cid, cap in caps.items() if cap == capability]
