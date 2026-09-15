"""ISO 27001 Risk Assessment Report — ISO 31000-aligned ISMS deliverable.

Reads ISO-scoped risks from the shared risk register (framework="ISO 27001")
and renders the required risk assessment report document (clauses 4.1/4.2
context, 6.1.2 risk criteria, 6.1.3 assessment method, register, and
treatment summary).
"""

from __future__ import annotations

import io
from datetime import date
from typing import Any, Dict, List

# Consequence / likelihood scale labels (ISO 31000-informed, 6.1.2 criteria).
SCALES = {
    0: "Negligible / Rare",
    1: "Low / Unlikely",
    2: "Moderate / Possible",
    3: "High / Likely",
    4: "Very high / Almost certain",
    5: "Extreme / Certain",
}

TREATMENT_LABELS = {
    "accept": "Risk acceptance",
    "mitigate": "Risk treatment",
    "transfer": "Risk transfer",
    "avoid": "Risk avoidance",
}


def _score_level(score: int) -> str:
    if score >= 12:
        return "Critical"
    if score >= 9:
        return "High"
    if score >= 6:
        return "Medium"
    if score >= 4:
        return "Low"
    return "Accepted"


def risk_rows() -> List[Dict[str, Any]]:
    """ISO-scoped risks from the shared register (empty-safe)."""
    try:
        from risks.store import list_risks
        rows = list_risks(framework="ISO 27001") or []
    except Exception:
        rows = []
    out = []
    for r in rows:
        likelihood = int(r.get("likelihood") or 0)
        impact = int(r.get("impact") or 0)
        inherent = int(r.get("inherent_score") or (likelihood * impact))
        residual = int(r.get("residual_score") or 0)
        out.append({
            "id": r.get("id") or "",
            "title": r.get("title") or "Untitled risk",
            "description": r.get("description") or "",
            "likelihood": likelihood,
            "impact": impact,
            "likelihood_label": SCALES.get(likelihood, str(likelihood)),
            "impact_label": SCALES.get(impact, str(impact)),
            "inherent_score": inherent,
            "inherent_level": _score_level(inherent),
            "residual_score": residual,
            "residual_level": _score_level(residual),
            "status": r.get("status") or "open",
            "treatment": r.get("treatment") or "",
            "treatment_label": TREATMENT_LABELS.get(r.get("treatment") or "", r.get("treatment") or "Not defined"),
            "treatment_plan": r.get("treatment_plan") or "",
            "owner": r.get("owner") or "",
            "review_date": r.get("review_date") or "",
            "control_ids": r.get("control_ids") or [],
        })
    return out


def _summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    by_level: Dict[str, int] = {}
    open_count = 0
    for r in rows:
        by_level[r["inherent_level"]] = by_level.get(r["inherent_level"], 0) + 1
        if r["status"] not in ("closed", "accepted"):
            open_count += 1
    return {
        "total": total,
        "open": open_count,
        "by_level": by_level,
        "generated_at": date.today().isoformat(),
    }


def export_risk_report_docx() -> bytes:
    """ISO/IEC 27001 Risk Assessment Report (docx)."""
    from docx import Document
    from docx.shared import Pt

    rows = risk_rows()
    summary = _summary(rows)

    doc = Document()
    doc.add_heading("ISO/IEC 27001:2022 — Risk Assessment Report", 0)
    doc.add_paragraph(
        "This report documents the ISMS risk assessment performed in accordance with "
        "clause 6.1.3 and the ISO 31000 risk management framework."
    )

    doc.add_heading("1. Context (clauses 4.1 / 4.2)", level=1)
    doc.add_paragraph(
        "The organization has determined internal and external issues relevant to the "
        "ISMS and the interested parties and their requirements. Climate change has "
        "been considered as a relevant issue (Amd 1:2024)."
    )

    doc.add_heading("2. Risk criteria (clause 6.1.2)", level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 1"
    for i, h in enumerate(["Score", "Likelihood", "Consequence"]):
        table.rows[0].cells[i].text = h
    for score, label in SCALES.items():
        lik, cons = label.split(" / ")
        cells = table.add_row().cells
        cells[0].text = str(score)
        cells[1].text = lik
        cells[2].text = cons

    doc.add_heading("3. Risk assessment method (clause 6.1.3)", level=1)
    doc.add_paragraph(
        "Risks are assessed qualitatively using a 0-5 likelihood and consequence "
        "matrix; inherent score = likelihood x consequence. Residual risk is recorded "
        "after treatment. Risk levels: 12+ Critical, 9+ High, 6+ Medium, 4+ Low."
    )

    doc.add_heading("4. Risk register", level=1)
    summary_table = doc.add_table(rows=1, cols=4)
    summary_table.style = "Light Grid Accent 1"
    for i, h in enumerate(["Metric", "Value", "", ""]):
        summary_table.rows[0].cells[i].text = h
    for label, value in [
        ("Total risks", summary["total"]),
        ("Open risks", summary["open"]),
        ("Assessment date", summary["generated_at"]),
    ]:
        cells = summary_table.add_row().cells
        cells[0].text = label
        cells[1].text = str(value)

    if rows:
        reg = doc.add_table(rows=1, cols=8)
        reg.style = "Table Grid"
        headers = ["ID", "Risk", "Likelihood", "Consequence", "Inherent", "Residual", "Treatment", "Owner"]
        for i, h in enumerate(headers):
            cell = reg.rows[0].cells[i]
            cell.text = h
            for run in cell.paragraphs[0].runs:
                run.bold = True
                run.font.size = Pt(8)
        for r in rows:
            cells = reg.add_row().cells
            values = [
                r["id"][:12],
                r["title"],
                f"{r['likelihood']} ({r['likelihood_label'].split(' / ')[0]})",
                f"{r['impact']} ({r['impact_label'].split(' / ')[0]})",
                f"{r['inherent_score']} ({r['inherent_level']})",
                f"{r['residual_score']} ({r['residual_level']})" if r["residual_score"] else "—",
                r["treatment_label"],
                r["owner"],
            ]
            for i, v in enumerate(values):
                cell = cells[i]
                cell.text = str(v)
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(7)

    doc.add_paragraph("")
    doc.add_paragraph(
        "Generated by Khestra. Manual review and approval by management is required "
        "before use as evidence of the ISMS risk assessment."
    )

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def export_risk_report_xlsx() -> bytes:
    """ISO 27001 risk register workbook (xlsx)."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    rows = risk_rows()
    summary = _summary(rows)

    wb = Workbook()
    ws = wb.active
    ws.title = "Risk Register"

    headers = ["ID", "Risk", "Description", "Likelihood", "Consequence", "Inherent Score",
               "Inherent Level", "Residual Score", "Residual Level", "Status", "Treatment",
               "Treatment Plan", "Owner", "Review Date", "Linked Controls"]
    ws.append(headers)
    fill = PatternFill("solid", fgColor="1F4E79")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = fill

    for r in rows:
        ws.append([
            r["id"], r["title"], r["description"],
            f"{r['likelihood']} ({r['likelihood_label']})",
            f"{r['impact']} ({r['impact_label']})",
            r["inherent_score"], r["inherent_level"],
            r["residual_score"] or "", r["residual_level"] if r["residual_score"] else "",
            r["status"], r["treatment_label"], r["treatment_plan"],
            r["owner"], r["review_date"],
            ", ".join(r["control_ids"]) if r["control_ids"] else "",
        ])

    for i, w in enumerate([14, 34, 40, 18, 18, 12, 12, 12, 12, 12, 18, 34, 18, 14, 28], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    sheet2 = wb.create_sheet("Summary")
    sheet2["A1"] = "ISO/IEC 27001 Risk Assessment — Summary"
    sheet2["A1"].font = Font(bold=True, size=12)
    sheet2["A3"] = "Total risks"
    sheet2["B3"] = summary["total"]
    sheet2["A4"] = "Open risks"
    sheet2["B4"] = summary["open"]
    sheet2["A5"] = "Assessment date"
    sheet2["B5"] = summary["generated_at"]
    row = 7
    sheet2.cell(row=row, column=1, value="Level").font = Font(bold=True)
    sheet2.cell(row=row, column=2, value="Count").font = Font(bold=True)
    for level, count in sorted(summary["by_level"].items()):
        row += 1
        sheet2.cell(row=row, column=1, value=level)
        sheet2.cell(row=row, column=2, value=count)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
