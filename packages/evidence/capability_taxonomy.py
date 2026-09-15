"""Frozen open-core capability taxonomy (Phase 0 contract).

The 27 capability categories below are the OPEN-side taxonomy that the free
tier's capability-keyed remediation (D8') and manual posture (D9) key off.
They are a projection of the collector capability labels (`CHECK_CAPABILITIES`)
applied by the closed `khestra-collectors` package.

Leak-test invariant (docs/OPEN_CORE_SPLIT.md §5):
  This module contains NO collector check ids and NO check->control pairs.
  It holds capability categories only. The per-framework control->capability
  classification (control ids only, derivable from public standards) is added
  in Phase 1 of the open-core split.

Set is frozen as of 2026-08-16; changing it requires an explicit contract
revision (docs/OPEN_CORE_CONTRACT.md).
"""

from __future__ import annotations

CAPABILITY_CATEGORIES: frozenset[str] = frozenset(
    {
        "Access Control",
        "Admin Accounts",
        "Audit Retention",
        "Backup & Recovery",
        "Cloud Security Posture",
        "Conditional Access",
        "Data Protection",
        "Detection & SIEM",
        "Device Management",
        "Encryption at Rest",
        "Encryption in Transit",
        "Endpoint Protection",
        "IT Asset Inventory",
        "Identity & Access",
        "Incident Response",
        "Key Management",
        "Logging & Monitoring",
        "MFA",
        "Network Security",
        "Password Policy",
        "Personnel & HR",
        "Secrets Management",
        "Security Operations",
        "Software Development",
        "User Access Review",
        "Vulnerability Management",
        "Web Application Security",
    }
)

# Phase 1: per-framework control->capability classification will live here as
# a SECOND, separate mapping (control ids only — public-standards material).
# Never add check ids or check->control pairs to this module.