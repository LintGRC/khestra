"""Utilities for the official DoW CUI SSP Word template."""

from datetime import datetime


def clear_document_body(doc) -> None:
    """Remove template placeholder paragraphs/tables; keep styles and document defaults."""
    body = doc.element.body
    for child in list(body):
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag in ("p", "tbl", "sdt"):
            body.remove(child)


def is_official_cui_template(path: str | None) -> bool:
    if not path:
        return False
    name = path.lower()
    return "cui-ssp" in name or "cui_ssp" in name


def patch_template_headers(doc, org_name: str, updated_date: str | None = None) -> None:
    """Legacy single-line patch — prefer template_filler.fix_page_headers."""
    from ssp.template_filler import fix_page_headers

    fix_page_headers(doc, org_name, updated_date)
