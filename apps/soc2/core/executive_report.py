"""Executive summary PDF — one-page board/management readiness report."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pdf_export.engine import generate_pdf


def generate_executive_summary(ws: Dict[str, Any]) -> bytes:
    from readiness import compute_dashboard

    dash = compute_dashboard(ws)
    org = ws.get("org_name") or "Organization"
    sections = [
        {"type": "heading", "content": "Executive Summary", "level": 0},
        {"type": "kv", "key": "Organization", "value": org},
        {"type": "kv", "key": "Date", "value": datetime.now().strftime("%Y-%m-%d")},
        {"type": "kv", "key": "Overall Readiness", "value": f"{dash.get('readiness_pct', 0)}%"},
        {"type": "kv", "key": "Composite Score", "value": f"{dash.get('readiness_pct', 0)}%"},
        {"type": "kv", "key": "Evidence Coverage", "value": f"{dash.get('evidence_coverage_pct', 0)}%"},
        {"type": "kv", "key": "Open Gaps", "value": str(dash.get('open_gaps', 0))},
        {"type": "kv", "key": "Controls Met", "value": f"{dash.get('controls_met', 0)} / {dash.get('controls_total', 0)}"},
        {"type": "page_break"},
        {"type": "heading", "content": "Category Breakdown", "level": 1},
    ]
    for cat in dash.get("category_readiness", []):
        sections.append({"type": "kv", "key": cat["category"], "value": f"{cat['readiness_pct']}% ({cat['met']}/{cat['total']} met)"})

    sections.append({"type": "page_break"})
    sections.append({"type": "heading", "content": "Risk & Exception Summary", "level": 1})
    sections.append({"type": "kv", "key": "Open Exceptions", "value": str(dash.get("open_exceptions", 0))})
    sections.append({"type": "kv", "key": "Expired Exceptions", "value": str(dash.get("expired_exceptions", 0))})
    sections.append({"type": "kv", "key": "Active Risks", "value": str(dash.get("active_risks", 0))})
    sections.append({"type": "kv", "key": "Open Findings", "value": str(dash.get("open_findings", 0))})

    sections.append({"type": "page_break"})
    sections.append({"type": "heading", "content": "Operational Status", "level": 1})
    sections.append({"type": "kv", "key": "Overdue Tests", "value": str(dash.get("overdue_tests", 0))})
    sections.append({"type": "kv", "key": "PoF Coverage", "value": f"{dash.get('pof_coverage_pct', 0)}%"})
    sections.append({"type": "kv", "key": "Policy Coverage", "value": f"{dash.get('policy_coverage', {}).get('mapped_pct', 0)}%"})

    return generate_pdf(f"Executive Summary — {org}", sections)
