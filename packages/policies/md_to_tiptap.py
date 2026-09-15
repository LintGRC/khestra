"""Convert markdown template content to TipTap JSON."""

from __future__ import annotations

import re
from typing import Any


def _inline_to_nodes(text: str) -> list[dict[str, Any]]:
    """Parse inline formatting (bold, italic, variables) into TipTap marks."""
    nodes: list[dict[str, Any]] = []
    pattern = re.compile(r"(\*\*(.+?)\*\*)|(\*(.+?)\*)|(\{\{(\w+)\}\})")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            nodes.append({"type": "text", "text": text[pos : m.start()]})
        if m.group(1):
            nodes.append({"type": "text", "text": m.group(2), "marks": [{"type": "bold"}]})
        elif m.group(3):
            nodes.append({"type": "text", "text": m.group(4), "marks": [{"type": "italic"}]})
        elif m.group(5):
            nodes.append({"type": "variable", "attrs": {"name": m.group(6)}})
        pos = m.end()
    if pos < len(text):
        nodes.append({"type": "text", "text": text[pos:]})
    return nodes


def _line_to_node(line: str, list_type: str | None = None) -> dict[str, Any] | None:
    stripped = line.strip()

    if not stripped:
        return None

    # Heading
    h_match = re.match(r"^(#{1,3})\s+(.+)$", stripped)
    if h_match:
        return {
            "type": f"heading",
            "attrs": {"level": len(h_match.group(1))},
            "content": _inline_to_nodes(h_match.group(2)),
        }

    # Bullet list
    if stripped.startswith("- ") or stripped.startswith("* "):
        content = _inline_to_nodes(stripped[2:])
        return {"type": "listItem", "content": [{"type": "paragraph", "content": content}]}

    # Ordered list
    ol_match = re.match(r"^\d+\.\s+(.+)$", stripped)
    if ol_match:
        content = _inline_to_nodes(ol_match.group(1))
        return {"type": "listItem", "content": [{"type": "paragraph", "content": content}]}

    # Paragraph
    return {"type": "paragraph", "content": _inline_to_nodes(stripped)}


def markdown_to_tiptap(md: str) -> dict[str, Any]:
    """Convert markdown string to TipTap JSON document."""
    lines = md.split("\n")
    content: list[dict[str, Any]] = []

    i = 0
    while i < len(lines):
        node = _line_to_node(lines[i])
        if node is None:
            i += 1
            continue

        # Group consecutive list items into a list node
        if node["type"] == "listItem":
            list_items = [node]
            i += 1
            while i < len(lines):
                nxt = _line_to_node(lines[i])
                if nxt and nxt["type"] == "listItem":
                    list_items.append(nxt)
                    i += 1
                else:
                    break
            # Determine if bullet or ordered
            is_ordered = bool(re.match(r"^\d+\.\s+", lines[i - len(list_items)].strip()))
            content.append({
                "type": "orderedList" if is_ordered else "bulletList",
                "content": list_items,
            })
        else:
            content.append(node)
            i += 1

    return {"type": "doc", "content": content} if content else {"type": "doc", "content": [{"type": "paragraph"}]}
