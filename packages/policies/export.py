"""DOCX export for policies — handles markdown, HTML, and TipTap JSON content."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from io import BytesIO
from typing import Any


def substitute_variables(text: str, variables: dict[str, str] | None = None) -> str:
    """Replace {{variable_name}} with values, leaving unmatched placeholders intact."""
    if not variables:
        return text
    return re.sub(r"\{\{(\w+)\}\}", lambda m: variables.get(m.group(1), m.group(0)), text)


def _is_tiptap(content: str) -> dict | None:
    """Detect TipTap JSON content and return parsed dict if valid."""
    text = (content or "").strip()
    if not text.startswith("{"):
        return None
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, ValueError, TypeError):
        return None
    if isinstance(parsed, dict) and parsed.get("type") == "doc":
        return parsed
    return None


def _tiptap_node_to_md(node: dict) -> str:
    """Convert a single TipTap JSON node to markdown string."""
    node_type = node.get("type", "")
    content_nodes = node.get("content") or []

    def _text(n: dict) -> str:
        text = n.get("text", "")
        for mark in n.get("marks") or []:
            if mark.get("type") == "bold":
                text = f"**{text}**"
            elif mark.get("type") == "italic":
                text = f"*{text}*"
            elif mark.get("type") == "code":
                text = f"`{text}`"
            elif mark.get("type") == "link":
                href = mark.get("attrs", {}).get("href", "")
                text = f"[{text}]({href})"
        return text

    if node_type == "doc":
        return "\n\n".join(_tiptap_node_to_md(c) for c in content_nodes)

    if node_type == "heading":
        level = node.get("attrs", {}).get("level", 1)
        prefix = "#" * level
        text = "".join(_text(c) for c in content_nodes)
        return f"{prefix} {text}"

    if node_type == "paragraph":
        text = "".join(_text(c) for c in content_nodes)
        return text

    if node_type in ("bulletList", "orderedList"):
        items = []
        for i, item in enumerate(content_nodes):
            item_text = _tiptap_node_to_md(item)
            if node_type == "orderedList":
                items.append(f"{i + 1}. {item_text}")
            else:
                items.append(f"- {item_text}")
        return "\n".join(items)

    if node_type == "listItem":
        return "".join(_tiptap_node_to_md(c) for c in content_nodes)

    if node_type == "text":
        return _text(node)

    if node_type == "hardBreak":
        return "\n"

    if node_type in ("horizontalRule", "horizontal_rule"):
        return "---"

    if node_type == "codeBlock":
        lang = node.get("attrs", {}).get("language", "")
        code = "".join(_text(c) for c in content_nodes)
        return f"```{lang}\n{code}\n```"

    return ""


def _tiptap_to_markdown(tiptap: dict) -> str:
    """Convert a TipTap JSON document tree to markdown."""
    return _tiptap_node_to_md(tiptap)


def _is_html(content: str) -> bool:
    return bool(re.search(r"</?(p|div|h[1-6]|ul|ol|li|strong|em|br|table|span)\b", content, re.IGNORECASE))


class _HtmlStripper(HTMLParser):
    """Strip dangerous tags, keeping only safe formatting tags."""

    SAFE_TAGS = frozenset({"p", "br", "strong", "b", "em", "i", "u", "h2", "h3", "h4", "ul", "ol", "li", "span"})

    def __init__(self) -> None:
        super().__init__()
        self.safe_html: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SAFE_TAGS:
            self.safe_html.append(f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SAFE_TAGS:
            self.safe_html.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.safe_html.append(data)

    def get_safe_html(self) -> str:
        return "".join(self.safe_html)


def sanitize_html(html: str) -> str:
    """Strip dangerous HTML tags, keeping only safe formatting tags."""
    stripper = _HtmlStripper()
    try:
        stripper.feed(html)
        return stripper.get_safe_html()
    except Exception:
        return html


def _html_to_docx(doc: Any, html: str) -> None:
    """Parse simple safe HTML into python-docx elements."""
    from docx.shared import Pt

    lines = html.replace("</p>", "\n").replace("</h2>", "\n").replace("</h3>", "\n").replace("</li>", "\n")
    lines = re.sub(r"<[^>]+>", "", lines)

    in_list = False
    for line in lines.split("\n"):
        line = line.strip()
        if not line:
            if in_list:
                in_list = False
            continue

        if line.startswith("## "):
            doc.add_heading(line[3:], level=2)
            in_list = False
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
            in_list = False
        elif line.startswith("- ") or line.startswith("* "):
            doc.add_paragraph(line[2:], style="List Bullet")
            in_list = True
        elif re.match(r"^\d+\.\s+", line):
            doc.add_paragraph(re.sub(r"^\d+\.\s+", "", line), style="List Number")
            in_list = True
        elif "**" in line:
            p = doc.add_paragraph()
            for segment in re.split(r"(\*\*.*?\*\*)", line):
                if segment.startswith("**") and segment.endswith("**"):
                    run = p.add_run(segment[2:-2])
                    run.bold = True
                elif segment:
                    p.add_run(segment)
            in_list = False
        else:
            doc.add_paragraph(line)
            in_list = False


def generate_docx(
    name: str,
    content: str,
    version: str = "1.0",
    variables: dict[str, str] | None = None,
) -> bytes:
    """Generate a DOCX from policy content (markdown or HTML) with variable substitution."""
    content = substitute_variables(content, variables)

    try:
        from docx import Document
        from docx.shared import Inches, Pt
    except ImportError:
        return _fallback_text(name, content, version)

    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    tiptap = _is_tiptap(content)
    if tiptap:
        content = _tiptap_to_markdown(tiptap)
        _markdown_to_docx(doc, content)
    elif _is_html(content):
        safe = sanitize_html(content)
        _html_to_docx(doc, safe)
    else:
        _markdown_to_docx(doc, content)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


def _markdown_to_docx(doc: Any, content: str) -> None:
    """Parse markdown content into python-docx elements."""
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif line.startswith("- ") or line.startswith("* "):
            doc.add_paragraph(line[2:], style="List Bullet")
        elif re.match(r"^\d+\.\s+", line):
            doc.add_paragraph(re.sub(r"^\d+\.\s+", "", line), style="List Number")
        elif "**" in line:
            p = doc.add_paragraph()
            for segment in re.split(r"(\*\*.*?\*\*)", line):
                if segment.startswith("**") and segment.endswith("**"):
                    run = p.add_run(segment[2:-2])
                    run.bold = True
                elif segment:
                    p.add_run(segment)
        elif line == "---":
            pass
        else:
            doc.add_paragraph(line)


def _fallback_text(name: str, content: str, version: str) -> bytes:
    from datetime import date
    text = f"# {name}\n\n{content}\n\n---\nVersion: {version} | {date.today().isoformat()}"
    return text.encode("utf-8")
