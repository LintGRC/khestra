"""Sanitize and repair SSP narrative text before merge or AI telemetry."""

from __future__ import annotations

import re
from typing import Any, Dict, List

IMPLEMENTATION_SUMMARY = "Implementation summary:"
EVIDENCE_REFS = "Evidence / references:"
ASSESSMENT_APPROACH = "Assessment approach (800-171A):"
PLACEHOLDER_LINE = "[Add policy name, config export, or ticket ID]"

_INSTRUCTIONAL_MARKERS = (
    "document named policies",
    "compensating controls",
    "describe your implementation",
    "[add policy",
    "document implementation for",
)


def is_starter_template_narrative(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if IMPLEMENTATION_SUMMARY in t and ASSESSMENT_APPROACH in t:
        return True
    return t.startswith("Control ") and "Organization context:" in t


def is_instructional_summary(body: str) -> bool:
    """Org-profile tailored placeholder text — not verified implementation."""
    stripped = (body or "").strip()
    if not stripped:
        return True
    lowered = stripped.lower()
    return any(marker in lowered for marker in _INSTRUCTIONAL_MARKERS)


def existing_narrative_facts_for_ai(bundle: Dict[str, Any]) -> str:
    """Prior implementation prose the model must treat as verified facts (not gaps)."""
    narrative = (bundle.get("current_narrative") or "").strip()
    if not narrative or is_starter_template_narrative(narrative) or is_instructional_summary(narrative):
        return ""
    return narrative[:4000]


_NARRATIVE_SUBJECT_RE = re.compile(
    r"^([A-Z][A-Za-z0-9&.,\-']+(?:\s+[A-Z][A-Za-z0-9&.,\-']+){0,5})\s+"
    r"(implements|utilizes|uses|enforces|maintains|limits|provides|employs|operates)\b"
)

_PLACEHOLDER_ORG_NAMES = frozenset({
    "test corp",
    "test corporation",
    "acme",
    "acme corp",
    "example corp",
    "example organization",
    "your organization",
    "the organization",
    "contoso",
})


def subject_org_from_narrative(text: str) -> str:
    """Pull leading org name from existing SSP prose (e.g. 'Trident implements…')."""
    first = (text or "").strip().split("\n", 1)[0].strip()
    m = _NARRATIVE_SUBJECT_RE.match(first)
    if not m:
        return ""
    return m.group(1).strip()


def resolve_narrative_org_name(
    profile_org: str,
    existing_facts: str,
    *,
    allow_narrative_subject: bool = True,
) -> str:
    """Resolve org subject for SSP drafts.

    When allow_narrative_subject is False (evidence-only draft), ignore names in
    the current narrative and skip placeholder profile names like Test Corp.
    """
    profile = (profile_org or "").strip() or "The organization"
    if not allow_narrative_subject:
        if profile.lower() in _PLACEHOLDER_ORG_NAMES:
            return "The organization"
        return profile
    from_narrative = subject_org_from_narrative(existing_facts)
    if not from_narrative:
        if profile.lower() in _PLACEHOLDER_ORG_NAMES:
            return "The organization"
        return profile
    if profile.lower() in _PLACEHOLDER_ORG_NAMES:
        return from_narrative
    if from_narrative.lower() != profile.lower() and from_narrative.lower() not in profile.lower():
        return from_narrative
    return profile


def gap_excerpt_for_ai(bundle: Dict[str, Any]) -> str:
    """Assessor notes + remediation only — never mix in existing SSP prose."""
    parts: List[str] = []
    notes = (bundle.get("assessor_notes") or "").strip()
    if notes:
        parts.append(notes)
    remediation = (bundle.get("remediation_plan") or "").strip()
    if remediation:
        parts.append(f"Remediation plan: {remediation}")
    return "\n\n".join(parts)


def clean_corrupted_starter(text: str) -> str:
    """
    Repair starter worksheets corrupted by old semicolon appends:
    - strip inline prose glued to evidence placeholder lines
    - remove orphan paragraphs after Evidence / references bullets
    """
    if not is_starter_template_narrative(text):
        return text

    text = re.sub(
        r"(\[Add policy name, config export, or ticket ID\]);.*",
        r"\1",
        text,
        flags=re.IGNORECASE,
    )

    lines = text.splitlines()
    try:
        ev_idx = next(i for i, line in enumerate(lines) if line.strip() == EVIDENCE_REFS)
    except StopIteration:
        return text

    result = lines[: ev_idx + 1]
    i = ev_idx + 1
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            result.append(line)
            i += 1
            continue
        if stripped.startswith("- "):
            if ";" in stripped and len(stripped) > 100:
                stripped = stripped.split(";", 1)[0].strip()
            result.append(stripped)
            i += 1
            continue
        break

    return "\n".join(result).rstrip() + "\n"
