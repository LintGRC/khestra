"""TSC category scoping — let users select which Trust Services Criteria categories are in scope.

Security (Common Criteria, CC1–CC9) is always mandatory.
Availability (A1), Confidentiality (C1), Processing Integrity (PI1), and Privacy (P1)
are optional. Hidden criteria data is preserved — nothing is deleted on scope-down.
"""

from __future__ import annotations

from typing import Any, Dict, List

from soc2_catalog import SOC2_CONTROLS

TSC_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "Security": {
        "label": "Security (Common Criteria)",
        "description": "Information and systems are protected against unauthorized access, disclosure, and damage.",
        "mandatory": True,
        "guidance_question": "",
        "example_commitment": "Customer data is protected with access controls, encryption, and monitoring.",
        "criteria_count": 33,
    },
    "Availability": {
        "label": "Availability",
        "description": "Information and systems are available for operation and use to meet commitments.",
        "mandatory": False,
        "guidance_question": "Do your customers require uptime guarantees or SLAs in their contracts?",
        "example_commitment": "Our platform guarantees 99.9% uptime.",
        "criteria_count": 3,
    },
    "Confidentiality": {
        "label": "Confidentiality",
        "description": "Information designated as confidential is protected as committed or agreed.",
        "mandatory": False,
        "guidance_question": "Do you store trade secrets, IP, or sensitive business data for customers?",
        "example_commitment": "Customer confidential data is classified and access-restricted.",
        "criteria_count": 2,
    },
    "Processing Integrity": {
        "label": "Processing Integrity",
        "description": "System processing is complete, valid, accurate, timely, and authorized.",
        "mandatory": False,
        "guidance_question": "Does your system process transactions where accuracy and completeness are critical?",
        "example_commitment": "All data processing is validated and reconciled for accuracy.",
        "criteria_count": 5,
    },
    "Privacy": {
        "label": "Privacy",
        "description": "Personal information is collected, used, retained, disclosed, and disposed of in conformity with commitments.",
        "mandatory": False,
        "guidance_question": "Do you collect personal data (names, emails, SSNs, health info) from end-users?",
        "example_commitment": "Personal data is collected with consent, used only for stated purposes, and securely deleted.",
        "criteria_count": 8,
    },
}

DEFAULT_SCOPE: Dict[str, bool] = {cat: True for cat in TSC_CATEGORIES}


def _get_criteria_prefix(cid: str) -> str:
    """Extract the category prefix from a control ID."""
    if cid.startswith("PI"):
        return "PI"
    if cid.startswith("CC"):
        return "CC"
    if cid.startswith("A"):
        return "A"
    if cid.startswith("C"):
        return "C"
    if cid.startswith("P"):
        return "P"
    return ""


_PREFIX_TO_CATEGORY: Dict[str, str] = {
    "CC": "Security",
    "A": "Availability",
    "C": "Confidentiality",
    "PI": "Processing Integrity",
    "P": "Privacy",
}


def get_category_for_criterion(cid: str) -> str:
    prefix = _get_criteria_prefix(cid)
    return _PREFIX_TO_CATEGORY.get(prefix, "Security")


def is_in_scope(cid: str, scope: Dict[str, bool]) -> bool:
    if cid not in SOC2_CONTROLS:
        return False
    cat = get_category_for_criterion(cid)
    return scope.get(cat, False)  # default False: missing key = not in scope


def get_in_scope_controls(scope: Dict[str, bool]) -> Dict[str, Any]:
    normalized = normalize_scope(scope)
    return {cid: meta for cid, meta in SOC2_CONTROLS.items() if is_in_scope(cid, normalized)}


def get_in_scope_criteria_ids(scope: Dict[str, bool]) -> List[str]:
    normalized = normalize_scope(scope)
    return [cid for cid in SOC2_CONTROLS if is_in_scope(cid, normalized)]


def scope_summary(scope: Dict[str, bool]) -> Dict[str, Any]:
    normalized = normalize_scope(scope)
    selected = sum(1 for v in normalized.values() if v)
    total = len(TSC_CATEGORIES)
    in_scope_ids = get_in_scope_criteria_ids(normalized)
    return {
        "selected_categories": selected,
        "total_categories": total,
        "in_scope_criteria": len(in_scope_ids),
        "total_criteria": len(SOC2_CONTROLS),
        "by_category": {
            cat: {
                "selected": normalized[cat],
                "mandatory": meta["mandatory"],
                "criteria_count": meta["criteria_count"],
            }
            for cat, meta in TSC_CATEGORIES.items()
        },
    }


def normalize_scope(scope: Dict[str, bool]) -> Dict[str, bool]:
    """Ensure all 5 category keys are present, coerce to booleans."""
    normalized: Dict[str, bool] = {}
    for cat in TSC_CATEGORIES:
        raw = scope.get(cat)
        if isinstance(raw, bool):
            normalized[cat] = raw
        elif isinstance(raw, str):
            normalized[cat] = raw.lower() in ("true", "yes", "1", "on")
        else:
            normalized[cat] = bool(raw)
    return normalized


def validate_scope(scope: Dict[str, bool]) -> Dict[str, Any]:
    errors: List[str] = []
    missing = [cat for cat in TSC_CATEGORIES if cat not in scope]
    if missing:
        errors.append(f"Missing categories: {', '.join(missing)}")
    if "Security" in scope and not scope.get("Security"):
        errors.append("Security (Common Criteria) is always required and cannot be disabled.")
    unknown = [k for k in scope if k not in TSC_CATEGORIES]
    if unknown:
        errors.append(f"Unknown categories: {', '.join(unknown)}")
    return {"valid": len(errors) == 0, "errors": errors}
