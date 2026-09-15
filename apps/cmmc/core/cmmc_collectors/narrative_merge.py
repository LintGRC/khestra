"""Merge suggested SSP prose with existing implementation narratives."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

IMPLEMENTATION_SUMMARY = "Implementation summary:"
CATALOG_REFERENCE = "Catalog reference:"
SHARED_RESPONSIBILITY = "Shared responsibility:"
ASSESSMENT_APPROACH = "Assessment approach (800-171A):"
EVIDENCE_REFS = "Evidence / references:"
PLACEHOLDER_LINE = "[Add policy name, config export, or ticket ID]"


def is_starter_template_narrative(text: str) -> bool:
    """True when narrative matches org-profile starter layout (not export prose)."""
    t = (text or "").strip()
    if not t:
        return False
    if IMPLEMENTATION_SUMMARY in t and ASSESSMENT_APPROACH in t:
        return True
    return t.startswith("Control ") and "Organization context:" in t


def _section_body_bounds(text: str, header: str, next_headers: List[str]) -> Tuple[int, int]:
    idx = text.find(header)
    if idx < 0:
        return -1, -1
    start = idx + len(header)
    while start < len(text) and text[start] in "\n\r":
        start += 1
    end = len(text)
    for nh in next_headers:
        pos = text.find(nh, start)
        if pos >= 0:
            end = min(end, pos)
    return start, end


def _is_placeholder_summary(body: str) -> bool:
    stripped = body.strip()
    if not stripped:
        return True
    if PLACEHOLDER_LINE in stripped:
        return True
    lowered = stripped.lower()
    return len(stripped) < 220 and (
        "document " in lowered or "describe " in lowered or stripped.endswith("compensating controls.")
    )


def _add_collector_evidence_lines(text: str, sources: List[str]) -> str:
    if not sources:
        return text
    lines = text.splitlines()
    out: List[str] = []
    placeholder_replaced = False
    for line in lines:
        if PLACEHOLDER_LINE in line:
            placeholder_replaced = True
            for src in sources:
                out.append(f"- {src}")
            continue
        out.append(line)
    if not placeholder_replaced and EVIDENCE_REFS in text:
        try:
            idx = out.index(EVIDENCE_REFS)
        except ValueError:
            return text
        insert_at = idx + 1
        while insert_at < len(out) and out[insert_at].startswith("- "):
            insert_at += 1
        for offset, src in enumerate(sources):
            if not any(src in row for row in out):
                out.insert(insert_at + offset, f"- {src}")
    return "\n".join(out)


def _append_prose_paragraph(existing: str, new_text: str) -> str:
    existing = (existing or "").strip()
    new_text = (new_text or "").strip()
    if not new_text:
        return existing
    if not existing:
        return new_text
    if new_text in existing:
        return existing
    return f"{existing}\n\n{new_text}"


def append_to_starter_implementation_summary(
    existing: str,
    new_text: str,
    sources: Optional[List[str]] = None,
) -> str:
    """Insert suggested prose under Implementation summary:, preserving worksheet sections."""
    from cmmc_collectors.narrative_sanitize import clean_corrupted_starter, is_instructional_summary

    existing = clean_corrupted_starter(existing)
    new_text = (new_text or "").strip()
    if not new_text:
        return existing

    next_headers = [CATALOG_REFERENCE, SHARED_RESPONSIBILITY, ASSESSMENT_APPROACH, EVIDENCE_REFS]
    start, end = _section_body_bounds(existing, IMPLEMENTATION_SUMMARY, next_headers)
    if start < 0:
        return _append_prose_paragraph(existing, new_text)

    old_body = existing[start:end].strip()
    if (
        not old_body
        or _is_placeholder_summary(old_body)
        or is_instructional_summary(old_body)
    ):
        new_body = new_text
    elif new_text in old_body:
        new_body = old_body
    else:
        new_body = _append_prose_paragraph(old_body, new_text)

    merged = existing[:start] + new_body + "\n\n" + existing[end:].lstrip("\n")
    return _add_collector_evidence_lines(merged, sources or [])


def merge_ssp_narrative(
    existing: str,
    suggested: str,
    mode: str,
    *,
    sources: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """
    Merge suggested SSP into existing narrative.

    Returns (merged_text, merge_strategy).
    """
    existing = existing or ""
    suggested = (suggested or "").strip()
    sources = sources or []

    if mode == "replace":
        if is_starter_template_narrative(existing):
            return suggested, "replace_with_export_prose"
        if not existing.strip():
            return suggested, "replace_prose"
        return suggested, "replace_prose"

    if is_starter_template_narrative(existing):
        from cmmc_collectors.narrative_sanitize import clean_corrupted_starter

        existing = clean_corrupted_starter(existing)
        merged = append_to_starter_implementation_summary(existing, suggested, sources)
        return merged, "append_into_implementation_summary"

    return _append_prose_paragraph(existing, suggested), "append_prose"


def preview_merges(
    existing: str,
    suggested: str,
    *,
    sources: Optional[List[str]] = None,
) -> Dict[str, str]:
    from cmmc_collectors.narrative_sanitize import clean_corrupted_starter

    cleaned = clean_corrupted_starter(existing) if is_starter_template_narrative(existing) else existing
    append_text, append_strategy = merge_ssp_narrative(
        cleaned, suggested, "append", sources=sources
    )
    replace_text, replace_strategy = merge_ssp_narrative(
        cleaned, suggested, "replace", sources=sources
    )
    return {
        "append": append_text,
        "replace": replace_text,
        "append_strategy": append_strategy,
        "replace_strategy": replace_strategy,
        "narrative_format": "starter" if is_starter_template_narrative(cleaned) else "prose",
    }
