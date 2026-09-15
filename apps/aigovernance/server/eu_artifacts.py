"""EU AI Act artifact generators — EU Declaration of Conformity (Art. 47) and
Technical Documentation (Art. 11 / Annex IV) as downloadable docx documents.
"""

from __future__ import annotations

import csv
import io
import json
import os
import zipfile
from datetime import date
from typing import Any, Dict

STATUS_LABELS = {
    "compliant": "Compliant",
    "partial": "Partially compliant",
    "non_compliant": "Non-compliant",
    "na": "Not applicable",
    "missing": "Not assessed",
}


def _conformity_record(sid: str, framework: str = "eu_ai_act") -> Dict[str, Any]:
    import json
    import os

    p = os.path.join(os.path.dirname(__file__), "..", "data", "conformity.json")
    if not os.path.exists(p):
        return {}
    try:
        db = json.load(open(p))
    except (json.JSONDecodeError, OSError):
        return {}
    return db.get(f"{sid}:{framework}") or {}


def _frameworks() -> Dict[str, Any]:
    try:
        from conformity_routes import FRAMEWORKS
    except ImportError:
        from server.conformity_routes import FRAMEWORKS
    return FRAMEWORKS


def _article_statuses(system: Dict[str, Any], framework: str = "eu_ai_act") -> list[Dict[str, Any]]:
    try:
        from conformity_routes import applicable_articles
    except ImportError:
        from server.conformity_routes import applicable_articles

    applicable = applicable_articles(system, framework)
    record = _conformity_record(system.get("id") or system.get("system_id") or "", framework)
    articles = record.get("articles", {})
    out = []
    for art in applicable:
        a = articles.get(art["id"], {})
        out.append({
            "ref": art.get("ref", ""),
            "title": art.get("title", ""),
            "status": a.get("status", "missing"),
            "notes": a.get("notes", ""),
        })
    return out


def export_eu_declaration_of_conformity(system: Dict[str, Any]) -> bytes:
    """EU Declaration of Conformity (Art. 47) — docx."""
    from docx import Document
    from docx.shared import Pt

    statuses = _article_statuses(system)
    compliant = all(s["status"] == "compliant" for s in statuses if s["status"] != "na")

    doc = Document()
    doc.add_heading("EU Declaration of Conformity", 0)
    doc.add_paragraph("(Artificial Intelligence Act — Regulation (EU) 2024/1689, Article 47)")

    doc.add_heading("1. AI system identification", level=1)
    rows = [
        ("System name", system.get("name") or "—"),
        ("Version", system.get("version") or "—"),
        ("Provider", system.get("vendor") or system.get("owner") or "—"),
        ("Risk classification", system.get("risk_classification") or "unclassified"),
        ("Intended purpose", system.get("purpose") or system.get("description") or "—"),
    ]
    t = doc.add_table(rows=0, cols=2)
    t.style = "Light Grid Accent 1"
    for label, value in rows:
        cells = t.add_row().cells
        cells[0].text = label
        cells[1].text = str(value)

    doc.add_heading("2. Conformity statement", level=1)
    if compliant:
        doc.add_paragraph(
            "The provider declares, under its sole responsibility, that the AI system identified "
            "above meets all applicable requirements of Chapter 2 of Regulation (EU) 2024/1689 "
            "(Articles 8-15), the conformity assessment procedure of Article 43, and, where "
            "applicable, the transparency obligations of Article 50."
        )
    else:
        doc.add_paragraph(
            "The provider declares that the AI system identified above is NOT yet fully compliant "
            "with all applicable requirements of Regulation (EU) 2024/1689. This draft declaration "
            "is for internal use; do not issue until all applicable obligations are satisfied."
        )

    doc.add_heading("3. Applicable obligations status", level=1)
    st = doc.add_table(rows=1, cols=4)
    st.style = "Table Grid"
    for i, h in enumerate(["Article", "Obligation", "Status", "Notes"]):
        cell = st.rows[0].cells[i]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(9)
    for s in statuses:
        cells = st.add_row().cells
        cells[0].text = s["ref"]
        cells[1].text = s["title"]
        cells[2].text = STATUS_LABELS.get(s["status"], s["status"])
        cells[3].text = s["notes"][:80]
        for cell in cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(8)

    doc.add_heading("4. Signatures", level=1)
    doc.add_paragraph(f"Place and date of issue: ______, {date.today().isoformat()}")
    doc.add_paragraph("Signed for and on behalf of the provider: ____________________________")
    doc.add_paragraph("Name, function: ___________________________________________")
    doc.add_paragraph(
        "Reference to the technical documentation (Article 11 / Annex IV) and any notified-body "
        "certificate (Article 44), where applicable: ____________________________"
    )

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def export_technical_documentation(system: Dict[str, Any]) -> bytes:
    """Technical documentation (Art. 11 / Annex IV) — docx."""
    from docx import Document
    from docx.shared import Pt

    statuses = _article_statuses(system)
    record = _conformity_record(system.get("id") or system.get("system_id") or "")
    overall = record.get("status", "draft")

    doc = Document()
    doc.add_heading("Technical Documentation — AI System", 0)
    doc.add_paragraph("(Artificial Intelligence Act — Regulation (EU) 2024/1689, Article 11 / Annex IV)")

    doc.add_heading("1. General description of the AI system", level=1)
    rows = [
        ("Name", system.get("name") or "—"),
        ("Version", system.get("version") or "—"),
        ("Vendor / provider", system.get("vendor") or "—"),
        ("Foundation model", system.get("foundation_model") or "—"),
        ("Fine-tuned", "Yes" if system.get("is_fine_tuned") else "No"),
        ("Intended purpose", system.get("purpose") or "—"),
        ("Description", system.get("description") or "—"),
        ("Risk classification", system.get("risk_classification") or "unclassified"),
        ("Deployment status", system.get("deployment_status") or "—"),
        ("Owner", system.get("owner") or "—"),
    ]
    t = doc.add_table(rows=0, cols=2)
    t.style = "Light Grid Accent 1"
    for label, value in rows:
        cells = t.add_row().cells
        cells[0].text = label
        cells[1].text = str(value)

    doc.add_heading("2. Input data and outputs", level=1)
    data = system.get("input_data_sources") or []
    if isinstance(data, list):
        doc.add_paragraph("Input data sources: " + (", ".join(str(x) for x in data) or "—"))
    else:
        doc.add_paragraph(f"Input data sources: {data or '—'}")
    out = system.get("output_destinations") or []
    if isinstance(out, list):
        doc.add_paragraph("Output destinations: " + (", ".join(str(x) for x in out) or "—"))
    else:
        doc.add_paragraph(f"Output destinations: {out or '—'}")
    if system.get("processing_location"):
        doc.add_paragraph(f"Processing location: {system['processing_location']}")

    doc.add_heading("3. Risk management (Article 9)", level=1)
    risk = system.get("risk_assessment") or {}
    if isinstance(risk, dict) and risk:
        rt = doc.add_table(rows=1, cols=2)
        rt.style = "Light Grid Accent 1"
        rt.rows[0].cells[0].text = "Risk"
        rt.rows[0].cells[1].text = "Assessment"
        for k, v in risk.items():
            cells = rt.add_row().cells
            cells[0].text = str(k)
            cells[1].text = str(v)
    else:
        doc.add_paragraph("Risk assessment: not recorded — complete the system risk assessment.")

    doc.add_heading("4. Monitoring, accuracy, robustness and cybersecurity (Article 15)", level=1)
    doc.add_paragraph(
        "Performance and monitoring information for this system is recorded in the Evaluations "
        "module (accuracy, robustness, bias, cybersecurity, and related evaluations) and in the "
        "conformity assessment record below."
    )

    doc.add_heading("5. Conformity assessment status (Article 43 / Annex VI-VII)", level=1)
    doc.add_paragraph(f"Overall conformity record status: {overall}")
    st = doc.add_table(rows=1, cols=4)
    st.style = "Table Grid"
    for i, h in enumerate(["Article", "Obligation", "Status", "Notes"]):
        cell = st.rows[0].cells[i]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(9)
    for s in statuses:
        cells = st.add_row().cells
        cells[0].text = s["ref"]
        cells[1].text = s["title"]
        cells[2].text = STATUS_LABELS.get(s["status"], s["status"])
        cells[3].text = s["notes"][:80]
        for cell in cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(8)

    doc.add_paragraph("")
    doc.add_paragraph("Generated by Khestra — AI Governance workspace.")

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def export_ai_soa(system: Dict[str, Any], framework: str = "iso_42001") -> bytes:
    """AI Management System Statement of Applicability (ISO 42001 clauses + Annex A) — docx."""
    from docx import Document
    from docx.shared import Pt

    FRAMEWORKS = _frameworks()

    fw = FRAMEWORKS.get(framework)
    if not fw:
        raise ValueError(f"Unknown framework: {framework}")

    statuses = _article_statuses(system, framework)
    record = _conformity_record(system.get("id") or system.get("system_id") or "", framework)
    overall = record.get("status", "draft")

    doc = Document()
    doc.add_heading("Statement of Applicability — AI Management System", 0)
    doc.add_paragraph(
        f"(ISO/IEC 42001:2023 — {fw.get('label', framework)}. "
        "Clauses 4-10 and Annex A reference controls.)"
    )
    doc.add_paragraph(f"AI system: {system.get('name') or '—'} (version {system.get('version') or '—'})")
    doc.add_paragraph(f"Overall conformity record status: {overall}")

    doc.add_heading("1. Management system clauses (4-10)", level=1)
    clause_rows = [s for s in statuses if s["ref"].startswith("Clause")]
    _render_soa_table(doc, clause_rows)

    doc.add_heading("2. Annex A reference controls", level=1)
    annex_rows = [s for s in statuses if s["ref"].startswith("A.")]
    _render_soa_table(doc, annex_rows)

    doc.add_paragraph("")
    doc.add_paragraph(
        "Justification notes are recorded per control in the conformity assessment. "
        "Generated by Khestra — AI Governance workspace."
    )

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _render_soa_table(doc, rows) -> None:
    from docx.shared import Pt

    if not rows:
        doc.add_paragraph("None recorded.")
        return
    table = doc.add_table(rows=1, cols=5)
    table.style = "Table Grid"
    for i, h in enumerate(["Ref", "Control", "Status", "Applicable", "Notes"]):
        cell = table.rows[0].cells[i]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(9)
    for s in rows:
        cells = table.add_row().cells
        cells[0].text = s["ref"]
        cells[1].text = s["title"]
        cells[2].text = STATUS_LABELS.get(s["status"], s["status"])
        cells[3].text = "No" if s["status"] == "na" else "Yes"
        cells[4].text = (s.get("notes") or "")[:80]
        for cell in cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(8)


def _model_card_markdown(system: Dict[str, Any]) -> str:
    ra = system.get("risk_assessment") or {}
    lines = [
        f"# AI System Card — {system.get('name') or 'System'}",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## 1. System identification",
        f"- **Name:** {system.get('name') or '—'}",
        f"- **Description:** {system.get('description') or '—'}",
        f"- **Purpose:** {system.get('purpose') or '—'}",
        f"- **Foundation model:** {system.get('foundation_model') or '—'}",
        f"- **Vendor:** {system.get('vendor') or '—'}",
        "",
        "## 2. Ownership & accountability",
        f"- **Owner:** {system.get('owner') or '—'}",
        f"- **Business owner:** {system.get('business_owner') or '—'}",
        f"- **Technical owner:** {system.get('technical_owner') or '—'}",
        f"- **Risk owner:** {system.get('risk_owner') or '—'}",
        "",
        "## 3. Risk classification",
        f"- **Risk tier:** {system.get('risk_classification') or 'unclassified'}",
        f"- **Risk score:** {ra.get('score', '—')}",
        "",
        "## 4. Deployment",
        f"- **Status:** {system.get('deployment_status') or '—'}",
        f"- **Environment:** {system.get('environment') or '—'}",
        f"- **Approval:** {system.get('approval_status') or 'draft'}",
        "",
        "## 5. Transparency & data",
        f"- **Public-facing:** {'Yes' if system.get('is_public_facing') else 'No'}",
        f"- **Input data:** {system.get('input_data_sources') or '—'}",
        f"- **Processing:** {system.get('processing_location') or '—'}",
        f"- **Output dest:** {system.get('output_destinations') or '—'}",
        "",
        "## 6. Model card details",
        f"- **Performance metrics:** {system.get('performance_metrics') or '—'}",
        f"- **Known limitations:** {system.get('known_limitations') or '—'}",
        f"- **Out-of-scope uses:** {system.get('out_of_scope_uses') or '—'}",
        f"- **Human oversight:** {system.get('human_oversight') or '—'}",
        f"- **Bias & fairness:** {system.get('bias_fairness_notes') or '—'}",
        f"- **Training data:** {system.get('training_data') or '—'}",
        "",
    ]
    return "\n".join(lines)


def _fria_csv_for_system(system: Dict[str, Any]) -> bytes | None:
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    path = os.path.join(data_dir, "frias.json")
    if not os.path.exists(path):
        return None
    try:
        db = json.load(open(path))
    except (json.JSONDecodeError, OSError):
        return None
    sid = system.get("id") or system.get("system_id") or ""
    name = (system.get("name") or "").strip().lower()
    rows = []
    for fr in (db.values() if isinstance(db, dict) else []):
        if not isinstance(fr, dict):
            continue
        match_id = fr.get("model_id") == sid or fr.get("system_id") == sid
        match_name = (fr.get("system_name") or "").strip().lower() == name if name else False
        if match_id or match_name:
            rows.append(fr)
    if not rows:
        return None
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "system_name", "status", "risk_classification", "system_purpose"])
    for fr in rows:
        writer.writerow([
            fr.get("id") or "",
            fr.get("system_name") or "",
            fr.get("status") or "",
            fr.get("risk_classification") or "",
            fr.get("system_purpose") or "",
        ])
    return buf.getvalue().encode("utf-8")


def export_dossier_pack(system: Dict[str, Any]) -> bytes:
    """One-click regulatory dossier: EU DoC, tech doc, AI SoA, model card, FRIA."""
    sid = system.get("id") or system.get("system_id") or "system"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", (
            f"Khestra AI Governance — regulatory dossier\n"
            f"System: {system.get('name') or sid}\n"
            f"Risk classification: {system.get('risk_classification') or 'unclassified'}\n"
            f"Generated: {date.today().isoformat()}\n\n"
            "Contents:\n"
            "  01-eu-declaration-of-conformity.docx  (EU AI Act Art. 47)\n"
            "  02-technical-documentation.docx       (Art. 11 / Annex IV)\n"
            "  03-ai-statement-of-applicability.docx (ISO/IEC 42001 SoA)\n"
            "  04-model-card.md\n"
            "  05-fria.csv                           (if a FRIA exists for this system)\n"
        ))
        zf.writestr("01-eu-declaration-of-conformity.docx", export_eu_declaration_of_conformity(system))
        zf.writestr("02-technical-documentation.docx", export_technical_documentation(system))
        zf.writestr("03-ai-statement-of-applicability.docx", export_ai_soa(system, "iso_42001"))
        zf.writestr("04-model-card.md", _model_card_markdown(system))
        fria = _fria_csv_for_system(system)
        if fria:
            zf.writestr("05-fria.csv", fria)
    return buf.getvalue()
