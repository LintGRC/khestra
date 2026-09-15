"""DOCX generation for SOC 2 policy documents.

Converts markdown policy content to formatted Word documents with headings,
bullet lists, and control reference footers.
"""

from __future__ import annotations

import io
import re
from datetime import date
from typing import Dict, List

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


def _add_heading_styled(doc: Document, text: str, level: int) -> None:
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)


def _add_body(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text)
    p.style.font.size = Pt(11)
    for run in p.runs:
        run.font.size = Pt(11)


def _add_bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text, style="List Bullet")
    for run in p.runs:
        run.font.size = Pt(10.5)


def _md_to_docx(doc: Document, markdown: str) -> None:
    """Convert subset of markdown to python-docx paragraphs."""
    lines = markdown.split("\n")
    i = 0
    in_bold_section = False

    while i < len(lines):
        line = lines[i].rstrip()

        # H1: # Title
        if line.startswith("# ") and not line.startswith("## "):
            _add_heading_styled(doc, line[2:], level=1)
            i += 1
            continue
        # H2: ## Title
        if line.startswith("## "):
            _add_heading_styled(doc, line[3:], level=2)
            i += 1
            continue
        # H3: ### Title
        if line.startswith("### "):
            _add_heading_styled(doc, line[4:], level=3)
            i += 1
            continue

        # Bold-section header: **Title text**
        bold_match = re.match(r"^\*\*(.+?)\*\*$", line)
        if bold_match and not line.startswith("- "):
            p = doc.add_paragraph()
            run = p.add_run(bold_match.group(1))
            run.bold = True
            run.font.size = Pt(11)
            i += 1
            in_bold_section = True
            continue

        # Bullet: - text or * text
        if line.startswith("- ") or line.startswith("* "):
            text = line[2:]
            # Handle inline bold in bullet: - **key:** value
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            _add_bullet(doc, text)
            i += 1
            continue

        # Nested bullet (indented with spaces)
        if re.match(r"^ {2,4}[-*] ", line):
            text = re.sub(r"^ {2,4}[-*] ", "", line)
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            _add_bullet(doc, "    " + text)
            i += 1
            continue

        # Numbered: 1. text or 1) text
        if re.match(r"^\d+[.)]\s", line):
            text = re.sub(r"^\d+[.)]\s*", "", line)
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            p = doc.add_paragraph(text, style="List Number")
            for run in p.runs:
                run.font.size = Pt(11)
            i += 1
            continue

        # Horizontal rule or empty
        if line in ("", "---"):
            i += 1
            continue

        # Default: body paragraph, handle inline bold
        if "**" in line:
            p = doc.add_paragraph()
            parts = re.split(r"(\*\*.+?\*\*)", line)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                    run.font.size = Pt(11)
                else:
                    run = p.add_run(part)
                    run.font.size = Pt(11)
        else:
            _add_body(doc, line)

        i += 1


def generate_policy_docx(
    name: str,
    content: str,
    org_name: str = "Your Organization",
    version: str = "1.0",
    effective_date: str = "",
) -> bytes:
    """Generate a DOCX file from a policy name and markdown content."""

    effective_date = effective_date or date.today().strftime("%B %d, %Y")

    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.1)
        section.right_margin = Inches(1.1)

    # Default font
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(6)

    # Replace placeholders
    body = content.replace("{{ORG_NAME}}", org_name).replace("{{DATE}}", effective_date)

    _md_to_docx(doc, body)

    # Footer with control reference
    footer_section = doc.sections[0]
    footer = footer_section.footer
    footer.paragraphs[0].clear()
    run = footer.paragraphs[0].add_run(f"{org_name} — {name} v{version}")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def fill_template(
    template_key: str,
    org_name: str = "Your Organization",
) -> Dict[str, str]:
    """Return a policy dict with filled template content."""
    from policy_content import TEMPLATES

    t = TEMPLATES.get(template_key)
    if not t:
        raise ValueError(f"Unknown template key: {template_key}")

    content = t["content"].replace("{{ORG_NAME}}", org_name).replace("{{DATE}}", date.today().strftime("%B %d, %Y"))

    return {
        "name": t["name"],
        "version": "1.0",
        "description": t["description"],
        "content": content,
        "mapped_controls": t["mapped_controls"],
    }


def list_templates() -> List[Dict]:
    from policy_content import TEMPLATE_LIST

    return TEMPLATE_LIST
