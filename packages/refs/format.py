"""Canonical framework-reference display formatting.

Single source for rendering control references across the fleet so every
surface shows the same format ("EU AI Act Art. 73", "ISO 42001 Annex A.2",
"NIST AI RMF GOVERN 1", ...). TS mirror: shared/frontend/refs/format.ts.
"""

from __future__ import annotations

import re

FRAMEWORK_LABELS = {
    "EU AI Act": "EU AI Act",
    "NIST AI RMF": "NIST AI RMF",
    "ISO 42001": "ISO 42001",
    "OWASP Agentic": "OWASP Agentic",
    "CMMC": "CMMC",
    "SOC 2": "SOC 2",
    "ISO 27001": "ISO 27001",
}

_ANNEX_CLAUSE = re.compile(r"A\.\d+")


def display_clause(framework: str, clause: str) -> str:
    """Render a bare clause string (e.g. "10.1, 10.2", "Art. 9", "GOVERN 1.1", "A.6")
    with the framework label. Already-labeled strings pass through unchanged."""
    label = FRAMEWORK_LABELS.get(framework, framework)
    text = (clause or "").strip()
    if not text or text.startswith(label):
        return text
    if framework == "ISO 42001":
        parts = [_annex_part(p) for p in (t.strip() for t in text.split(",")) if p]
        return f"{label} " + ", ".join(parts)
    if framework == "ISO 27001":
        parts = [_annex_part(p) for p in (t.strip() for t in text.split(",")) if p]
        return f"{label} " + ", ".join(parts)
    return f"{label} {text}"


def _annex_part(part: str) -> str:
    if _ANNEX_CLAUSE.fullmatch(part):
        return f"Annex {part}"
    return part


def _framework_from_id(control_id: str) -> str:
    if control_id.startswith("EU-"):
        return "EU AI Act"
    if control_id.startswith("NIST-"):
        return "NIST AI RMF"
    if control_id.startswith("ISO-A.") or control_id.startswith("ISO-"):
        return "ISO 42001"
    if control_id.startswith("ISO27K-"):
        return "ISO 27001"
    if control_id.startswith("OWASP-LLM-"):
        return "OWASP LLM Top 10"
    if control_id.startswith("OWASP-"):
        return "OWASP Agentic"
    if control_id.startswith("AC.L") or ".L" in control_id:
        return "CMMC"
    if control_id.startswith("SOC-") or control_id.startswith("CC") or control_id.startswith(("A1.", "C1.", "PI1.", "P")):
        return "SOC 2"
    return ""


def render_control_ref(control_id: str) -> str:
    """Render a catalog control ID to its display form."""
    cid = (control_id or "").strip()
    framework = _framework_from_id(cid)
    if framework == "EU AI Act":
        return f"EU AI Act Art. {cid[3:]}"
    if framework == "NIST AI RMF":
        return f"NIST AI RMF {cid[5:].replace('-', ' ', 1)}"
    if framework == "ISO 42001":
        clause = cid[4:]
        if clause.startswith("A."):
            return f"ISO 42001 Annex {clause}"
        return f"ISO 42001 Clause {clause}"
    if framework == "ISO 27001":
        clause = cid[len("ISO27K-"):]
        if clause.startswith("A."):
            return f"ISO 27001 Annex {clause}"
        return f"ISO 27001 {clause}"
    if framework == "OWASP Agentic":
        return f"OWASP ASI{int(cid[6:]):02d}"
    if framework == "OWASP LLM Top 10":
        return f"OWASP LLM{int(cid[10:]):02d}:2025"
    if framework == "CMMC":
        return f"CMMC {cid}"
    if framework == "SOC 2":
        return f"SOC 2 {cid}"
    return cid
