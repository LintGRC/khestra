"""Deterministic post-generation checks for AI SSP drafts."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

_GAP_STATUSES = frozenset({"NOT MET", "PARTIALLY MET", "IN PROGRESS", "PLANNED"})

# Terms that often appear in catalog examples but are rarely in collector telemetry.
_HIGH_RISK_KEYWORDS = (
    "fido2",
    "yubikey",
    "vpn",
    "hardware token",
    "biometric",
    "ipsec",
    "pim",
    "microsoft authenticator",
    "just-in-time",
    "o365",
)

_COMPLIANCE_SUCCESS_PHRASES = (
    "fully complies with",
    "fully meets the requirement",
    "is completely enforced",
    "fully enforced",
    "full compliance",
    "fully compliant",
)

_ENFORCEMENT_PHRASES = (
    "is enforced",
    "are enforced",
    "mandatory",
    "requires mfa for all",
    "must use mfa",
    "is required for all",
)

_NON_SSP_MARKERS = (
    "```",
    "import ",
    "typescript",
    "promptbuilder",
    "lintsspdraft",
    "industrial-grade blueprint",
    "linguistic synthesizer",
    "<regulatory_reference",
    "export default function",
)

_ASSESSOR_ESSAY_MARKERS = (
    "not documented in the provided evidence",
    "not documented in provided evidence",
    "is also not documented",
    "remediation plan in place",
    "ongoing efforts to ensure",
    "partially met",
    "not yet fully implemented",
    "means of limiting unsuccessful logon attempts is defined but",
)


from cmmc_collectors.narrative_sanitize import existing_narrative_facts_for_ai, gap_excerpt_for_ai


def verified_telemetry_payload(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Facts the model may treat as implementation evidence (excludes catalog text)."""
    if bundle.get("include_current_narrative"):
        existing = bundle.get("existing_narrative_facts") or existing_narrative_facts_for_ai(bundle)
    else:
        existing = ""
    return {
        "control_id": bundle.get("control_id"),
        "control_name": bundle.get("control_name"),
        "assessment_status": bundle.get("status"),
        "organization": bundle.get("org_name"),
        "technology_stack": bundle.get("stack_label"),
        "existing_implementation_narrative": existing,
        "collector_findings": bundle.get("collector_findings_only")
        or [
            f
            for f in (bundle.get("findings") or [])
            if not str(f).startswith(
                (
                    "System description:",
                    "Architecture summary:",
                    "System boundary:",
                    "Hardware inventory:",
                    "Software inventory:",
                    "Environment scope:",
                )
            )
        ],
        "org_profile_context": bundle.get("org_profile_findings") or [],
        "gap_and_remediation": gap_excerpt_for_ai(bundle),
        "remediation_plan": bundle.get("remediation_plan") or "",
        "target_date": bundle.get("target_date") or "",
        "owner": bundle.get("owner") or "",
        "linked_policies": [
            {"title": p.get("title", ""), "version": p.get("version", "")}
            for p in (bundle.get("linked_policies") or [])
        ],
        "linked_assets": [
            {"name": a.get("name", ""), "type": a.get("type", ""), "cui": bool(a.get("cui", False))}
            for a in (bundle.get("linked_assets") or [])
        ],
        "linked_team": bundle.get("linked_team") or [],
        "evidence_artifacts": bundle.get("evidence_artifacts")
        or [
            {
                "title": (e.get("display_title") or e.get("filename") or "")[:200],
                "evidence_type": e.get("evidence_type") or "",
            }
            for e in (bundle.get("evidence_files") or [])[:40]
        ],
        "examine": (bundle.get("examine") or "").strip(),
        "interview": (bundle.get("interview") or "").strip(),
        "test": (bundle.get("test") or "").strip(),
        "assessment_objectives_171a": [
            {
                "letter": o.get("letter", ""),
                "status": o.get("status", "NOT_STARTED"),
                "text": o.get("text", ""),
            }
            for o in (bundle.get("objectives") or [])
        ],
    }


def verified_telemetry_json(bundle: Dict[str, Any]) -> str:
    return json.dumps(verified_telemetry_payload(bundle), indent=2)


def _verified_text(bundle: Dict[str, Any]) -> str:
    return verified_telemetry_json(bundle).lower()


def _numbers_in_text(text: str) -> List[str]:
    return re.findall(r"\b\d{1,4}\b", text)


def lint_ssp_draft(draft: str, bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scan AI draft for unsupported catalog bleed, status leaps, and metric drift.

    Returns {"passed": bool, "warnings": list[str]}.
    """
    warnings: List[str] = []
    if not (draft or "").strip():
        return {"passed": True, "warnings": []}

    draft_lower = draft.lower()
    catalog_lower = (bundle.get("catalog_description") or "").lower()
    telemetry_lower = _verified_text(bundle)
    findings_text = " ".join(bundle.get("findings") or []).lower()
    status = (bundle.get("status") or "").strip()

    for marker in _NON_SSP_MARKERS:
        if marker in draft_lower:
            warnings.append(
                "Draft does not look like SSP prose (code, markdown, or prompt text detected). "
                "Regenerate or use the template draft."
            )
            break

    for marker in _ASSESSOR_ESSAY_MARKERS:
        if marker in draft_lower:
            warnings.append(
                "Draft reads like an assessor gap essay rather than implementation prose."
            )
            break

    for keyword in _HIGH_RISK_KEYWORDS:
        in_draft = keyword in draft_lower
        in_catalog = keyword in catalog_lower
        in_telemetry = keyword in telemetry_lower
        if in_draft and in_catalog and not in_telemetry:
            warnings.append(
                f'Potential hallucination: "{keyword}" appears in the control catalog and the draft, '
                "but not in verified collector notes or telemetry."
            )

    if status.upper() in _GAP_STATUSES:
        for phrase in _COMPLIANCE_SUCCESS_PHRASES:
            if phrase in draft_lower:
                warnings.append(
                    f'Status inconsistency: assessment is "{status}" but the draft uses success phrasing '
                    f'("{phrase}").'
                )
                break

    if "registered" in findings_text and "enforc" not in findings_text:
        if any(phrase in draft_lower for phrase in _ENFORCEMENT_PHRASES):
            warnings.append(
                "Registration vs enforcement: collector findings mention registration but not enforcement; "
                "the draft may overstate mandatory MFA coverage."
            )

    for num in _numbers_in_text(draft):
        if num not in telemetry_lower:
            warnings.append(
                f'Unsupported metric: the number "{num}" appears in the draft but not in verified telemetry.'
            )

    # De-duplicate while preserving order
    seen = set()
    unique: List[str] = []
    for w in warnings:
        if w not in seen:
            seen.add(w)
            unique.append(w)

    return {"passed": len(unique) == 0, "warnings": unique}
