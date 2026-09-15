"""Render filtered shared-module data as text blocks in the SSP."""

from __future__ import annotations

from typing import Any, Dict, List


def add_module_evidence_block(doc, module_name: str, rows: List[Dict[str, str]], columns: List[str], label: str) -> None:
    """Append a formatted evidence block to the document for a shared module."""
    if not rows:
        doc.add_paragraph()
        return

    doc.add_paragraph(f"Linked {label}:")
    for row in rows:
        parts = []
        for col in columns:
            val = row.get(col, "")
            if col == "role":
                parts.append(val)
            elif val:
                col_label = col.replace("_", " ").title()
                parts.append(f"{col_label}: {val}")
        if parts:
            joined = " \u2014 ".join(parts)
            doc.add_paragraph(f"    \u2022 {joined}")

    doc.add_paragraph()


def add_policy_reference_block(doc, module_name: str, rows: List[Dict[str, str]], label: str) -> None:
    """Append a policy metadata reference block."""
    if not rows:
        doc.add_paragraph(f"Referenced policy: {label} (not yet uploaded to Policy Manager)")
        doc.add_paragraph()
        return

    doc.add_paragraph(f"Referenced {label}:")
    for p in rows:
        doc.add_paragraph(
            f"    \u2022 {p.get('title', 'Untitled')} \u2014 "
            f"Version {p.get('version', 1)}, "
            f"Status: {p.get('status', 'draft')}, "
            f"Last updated: {p.get('updated_at', 'N/A')}",
        )
    doc.add_paragraph()
