"""SOC 2 System Description DOCX generation."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, List

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

from soc2_catalog import SOC2_CONTROLS
from system_description import DC_SECTION_200, dc_200_coverage
from tsc_scoping import DEFAULT_SCOPE, get_in_scope_controls


def _add_heading_styled(doc: Document, text: str, level: int = 1) -> None:
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)


def _add_body(doc: Document, text: str) -> None:
    para = doc.add_paragraph(text)
    para.style.font.size = Pt(11)
    para.style.font.name = "Calibri"


def _add_bullet(doc: Document, text: str) -> None:
    para = doc.add_paragraph(text, style="List Bullet")
    para.style.font.size = Pt(10.5)
    para.style.font.name = "Calibri"


def _add_table_row(table, cells: List[str], bold: bool = False) -> None:
    row = table.add_row()
    for i, text in enumerate(cells):
        cell = row.cells[i]
        cell.text = text
        for para in cell.paragraphs:
            para.style.font.size = Pt(10)
            para.style.font.name = "Calibri"
            if bold:
                for run in para.runs:
                    run.bold = True


def _profile_text(org_profile: Dict[str, Any], key: str) -> str:
    value = (org_profile.get(key) or "").strip()
    return value if value else "[Not yet documented]"


def _add_kv_table(doc: Document, rows: List[tuple[str, str]]) -> None:
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Field"
    hdr[1].text = "Value"
    for para in hdr[0].paragraphs + hdr[1].paragraphs:
        for run in para.runs:
            run.bold = True
            run.font.size = Pt(10)
    for label, value in rows:
        _add_table_row(table, [label, value or "[Not yet documented]"])


def generate_system_description_docx(ws: Dict[str, Any]) -> bytes:
    """SOC 2 System Description DOCX shaped to AICPA DC Section 200."""

    org_profile = dict(ws.get("org_profile") or {})
    if not org_profile.get("org_name"):
        org_profile["org_name"] = ws.get("org_name") or "Organization"
    answers = ws.get("answers") or {}
    policies = ws.get("policies") or []
    exceptions = ws.get("exceptions") or []
    engagement = ws.get("soc2_engagement") or {}
    cuecs = ws.get("cuecs") or []
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    in_scope = get_in_scope_controls(scope)
    dc = dc_200_coverage(org_profile)

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

    org_name = org_profile.get("org_name") or ws.get("org_name") or "Organization"
    system_name = org_profile.get("system_name") or "System"
    now = datetime.now().strftime("%B %d, %Y")

    # ── Title Page ────────────────────────────────────────────
    doc.add_paragraph("")
    doc.add_paragraph("")
    title = doc.add_heading(f"System Description", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    subtitle = doc.add_heading(f"{org_name}", level=1)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    meta = doc.add_paragraph(f"{system_name}\nGenerated: {now}")
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.style.font.size = Pt(12)

    doc.add_page_break()

    # ── Table of Contents ─────────────────────────────────────
    _add_heading_styled(doc, "Table of Contents", level=1)
    toc_items = [
        "1. Engagement",
        "2. Types of Services Provided (DC-1.1)",
        "3. Infrastructure (DC-1.2)",
        "4. Software (DC-1.3)",
        "5. People (DC-1.4)",
        "6. Data (DC-1.5)",
        "7. Processes and Procedures (DC-1.6)",
        "8. Monitoring and Reporting (DC-1.7)",
        "9. System Boundaries (DC-2.1)",
        "10. Products and Services (DC-2.2)",
        "11. Subservice Organizations (DC-3.1)",
        "12. Complementary User Entity Controls (DC-3.2)",
        "13. Service Commitments (DC-4.1)",
        "14. System Requirements (DC-4.2)",
        "15. Control Objectives and Related Controls (DC-5.1)",
        "16. Changes to the System (DC-6.1)",
        "17. Criteria Met and Not Met (DC-7.1)",
        "18. Description Criteria (DC Section 200) Coverage",
        "19. Evidence Summary",
        "20. Appendices",
    ]
    for item in toc_items:
        _add_bullet(doc, item)
    doc.add_page_break()

    # ── 1. Engagement ─────────────────────────────────────────
    _add_heading_styled(doc, "1. Engagement", level=1)
    type_label = {"type1": "Type I", "type2": "Type II"}.get(
        engagement.get("type"), engagement.get("type") or "[Not yet documented]"
    )
    _add_kv_table(doc, [
        ("Report type", type_label if engagement.get("type") else "[Not yet documented]"),
        ("CPA firm", engagement.get("firm") or "[Not yet documented]"),
        ("CPA contact", engagement.get("cpa_contact") or "[Not yet documented]"),
        ("Engagement window",
         f"{engagement.get('engagement_start') or '—'} → {engagement.get('engagement_end') or '—'}"),
        ("Engagement status", engagement.get("status") or "[Not yet documented]"),
    ])
    _add_body(doc, f"This System Description documents the system operated by {org_name} "
              f"for {system_name} against the AICPA Trust Services Criteria, using the "
              f"Description Criteria in DC Section 200.")

    in_scope_ids = list(in_scope.keys()) or list(SOC2_CONTROLS.keys())
    total = len(in_scope_ids)
    met = sum(1 for cid in in_scope_ids if answers.get(cid, {}).get("status", "NOT STARTED") in ("MET", "NOT APPLICABLE", "INHERITED"))
    gaps = sum(1 for cid in in_scope_ids if answers.get(cid, {}).get("status", "NOT STARTED") in ("NOT MET", "NOT STARTED"))
    pct = round((met / total) * 100) if total else 0
    evidence_count = sum(len(answers.get(cid, {}).get("evidence") or []) for cid in in_scope_ids)
    _add_body(doc, f"As of {now}, {pct}% of in-scope criteria are assessed as meeting requirements, "
              f"with {gaps} open gaps. {evidence_count} evidence artifacts have been collected. "
              f"DC Section 200 coverage: {dc['dc_200_pct']}% "
              f"({dc['dc_200_covered']}/{dc['dc_200_total']} description criteria).")

    # ── DC-1.1 Types of Services ───────────────────────────────
    _add_heading_styled(doc, "2. Types of Services Provided (DC-1.1)", level=1)
    _add_body(doc, DC_SECTION_200["DC-1.1"]["description"])
    _add_kv_table(doc, [
        ("System name", _profile_text(org_profile, "system_name")),
        ("Services provided", _profile_text(org_profile, "system_description")),
    ])

    # ── DC-1.2 Infrastructure ─────────────────────────────────
    _add_heading_styled(doc, "3. Infrastructure (DC-1.2)", level=1)
    _add_body(doc, DC_SECTION_200["DC-1.2"]["description"])
    _add_kv_table(doc, [
        ("Cloud providers", _profile_text(org_profile, "cloud_providers")),
        ("Data centers", _profile_text(org_profile, "data_centers")),
        ("Architecture", _profile_text(org_profile, "architecture_summary")),
    ])

    # ── DC-1.3 Software ───────────────────────────────────────
    _add_heading_styled(doc, "4. Software (DC-1.3)", level=1)
    _add_body(doc, DC_SECTION_200["DC-1.3"]["description"])
    _add_kv_table(doc, [
        ("Technology stack", _profile_text(org_profile, "tech_stack")),
        ("Software inventory", _profile_text(org_profile, "software_inventory")),
    ])

    # ── DC-1.4 People ─────────────────────────────────────────
    _add_heading_styled(doc, "5. People (DC-1.4)", level=1)
    _add_body(doc, DC_SECTION_200["DC-1.4"]["description"])
    _add_kv_table(doc, [
        ("System owner", _profile_text(org_profile, "system_owner")),
        ("Compliance officer", _profile_text(org_profile, "compliance_officer")),
        ("IT administrator", _profile_text(org_profile, "it_admin")),
        ("Auditor", org_profile.get("auditor_name") or "[Not yet documented]"),
    ])

    # ── DC-1.5 Data ───────────────────────────────────────────
    _add_heading_styled(doc, "6. Data (DC-1.5)", level=1)
    _add_body(doc, DC_SECTION_200["DC-1.5"]["description"])
    _add_kv_table(doc, [
        ("Data classification", _profile_text(org_profile, "data_classification")),
        ("Data flows", _profile_text(org_profile, "data_flows")),
        ("Boundary", _profile_text(org_profile, "boundary_description")),
    ])

    # ── DC-1.6 Processes ──────────────────────────────────────
    _add_heading_styled(doc, "7. Processes and Procedures (DC-1.6)", level=1)
    _add_body(doc, DC_SECTION_200["DC-1.6"]["description"])
    _add_kv_table(doc, [
        ("Incident response", _profile_text(org_profile, "incident_response_procedures")),
        ("Change management", _profile_text(org_profile, "change_management_procedures")),
    ])

    # ── DC-1.7 Monitoring ─────────────────────────────────────
    _add_heading_styled(doc, "8. Monitoring and Reporting (DC-1.7)", level=1)
    _add_body(doc, DC_SECTION_200["DC-1.7"]["description"])
    _add_kv_table(doc, [
        ("Monitoring tools", _profile_text(org_profile, "monitoring_tools")),
        ("Reporting frequency", _profile_text(org_profile, "reporting_frequency")),
    ])

    # ── DC-2.1 Boundaries ─────────────────────────────────────
    _add_heading_styled(doc, "9. System Boundaries (DC-2.1)", level=1)
    _add_body(doc, DC_SECTION_200["DC-2.1"]["description"])
    _add_body(doc, _profile_text(org_profile, "boundary_description"))
    if (org_profile.get("scope_definition") or "").strip():
        _add_body(doc, org_profile["scope_definition"])

    # ── DC-2.2 Products ───────────────────────────────────────
    _add_heading_styled(doc, "10. Products and Services (DC-2.2)", level=1)
    _add_body(doc, DC_SECTION_200["DC-2.2"]["description"])
    _add_body(doc, _profile_text(org_profile, "system_description"))
    if (org_profile.get("service_catalog") or "").strip():
        _add_body(doc, org_profile["service_catalog"])

    # ── DC-3.1 Subservice / carve-out ─────────────────────────
    _add_heading_styled(doc, "11. Subservice Organizations (DC-3.1)", level=1)
    _add_body(doc, DC_SECTION_200["DC-3.1"]["description"])
    reporting = (org_profile.get("reporting_method") or "").strip()
    reporting_label = reporting or "[Not yet documented]"
    _add_kv_table(doc, [
        ("Reporting method (carve-out vs inclusive)", reporting_label),
        ("Subservice organizations", _profile_text(org_profile, "subservice_organizations")),
    ])
    if reporting.lower().replace("_", "-") in ("carve-out", "carveout"):
        _add_body(doc, "The carve-out method is used. Complementary subservice organization "
                  "controls (CSOC) at the subservice organization are excluded from this description.")
    elif reporting.lower() == "inclusive":
        _add_body(doc, "The inclusive method is used. Controls at the subservice organization "
                  "are included in this description.")

    # ── DC-3.2 CUEC ───────────────────────────────────────────
    _add_heading_styled(doc, "12. Complementary User Entity Controls (DC-3.2)", level=1)
    _add_body(doc, DC_SECTION_200["DC-3.2"]["description"])
    cuec_text = (org_profile.get("user_entity_controls") or "").strip()
    if cuec_text:
        _add_body(doc, cuec_text)
    if cuecs:
        table = doc.add_table(rows=1, cols=4)
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        for i, h in enumerate(["Control", "Description", "Assigned to", "Status"]):
            hdr[i].text = h
            for run in hdr[i].paragraphs[0].runs:
                run.bold = True
                run.font.size = Pt(10)
        for cuec in cuecs:
            _add_table_row(table, [
                cuec.get("control_id") or "",
                cuec.get("description") or "",
                cuec.get("assigned_to") or "",
                cuec.get("status") or "",
            ])
    if not cuec_text and not cuecs:
        _add_body(doc, "[Not yet documented]")

    # ── DC-4.1 Commitments ────────────────────────────────────
    _add_heading_styled(doc, "13. Service Commitments (DC-4.1)", level=1)
    _add_body(doc, DC_SECTION_200["DC-4.1"]["description"])
    _add_kv_table(doc, [
        ("Service commitments", _profile_text(org_profile, "service_commitments")),
        ("SLA documentation", _profile_text(org_profile, "sla_documentation")),
    ])

    # ── DC-4.2 Requirements ───────────────────────────────────
    _add_heading_styled(doc, "14. System Requirements (DC-4.2)", level=1)
    _add_body(doc, DC_SECTION_200["DC-4.2"]["description"])
    _add_kv_table(doc, [
        ("Availability", _profile_text(org_profile, "availability_requirements")),
        ("Security", _profile_text(org_profile, "security_requirements")),
        ("Confidentiality", _profile_text(org_profile, "confidentiality_requirements")),
    ])

    # ── DC-5.1 Control objectives ─────────────────────────────
    _add_heading_styled(doc, "15. Control Objectives and Related Controls (DC-5.1)", level=1)
    _add_body(doc, DC_SECTION_200["DC-5.1"]["description"])

    catalog_for_dump = in_scope if in_scope else SOC2_CONTROLS
    categories = sorted({m["category"] for m in catalog_for_dump.values()})
    for cat in categories:
        cat_ids = [cid for cid, m in catalog_for_dump.items() if m["category"] == cat]
        cat_met = sum(1 for cid in cat_ids if answers.get(cid, {}).get("status", "NOT STARTED") in ("MET", "NOT APPLICABLE", "INHERITED"))
        _add_heading_styled(doc, f"{cat} ({cat_met}/{len(cat_ids)} met)", level=2)

        for cid in cat_ids:
            meta = SOC2_CONTROLS[cid]
            ans = answers.get(cid, {})
            status = ans.get("status", "NOT STARTED")
            narrative = (ans.get("implementation_narrative") or "").strip()
            evidence = ans.get("evidence") or []

            _add_heading_styled(doc, f"{cid} - {meta['title']}", level=3)
            _add_body(doc, f"Status: {status}")
            _add_body(doc, meta.get("description", ""))

            if narrative:
                _add_body(doc, f"Implementation: {narrative}")

            if evidence:
                _add_body(doc, f"Evidence: {len(evidence)} artifact(s) attached")

            if ans.get("operating_status") and ans["operating_status"] != "NOT TESTED":
                _add_body(doc, f"Operating effectiveness: {ans['operating_status']}")

            if ans.get("frequency"):
                _add_body(doc, f"Frequency: {ans['frequency']}")

            lrd = ans.get("last_review_date") or ""
            nrd = ans.get("next_review_date") or ""
            if lrd or nrd:
                parts = []
                if lrd: parts.append(f"Last review: {lrd}")
                if nrd: parts.append(f"Next review: {nrd}")
                _add_body(doc, " | ".join(parts))

            linked_policies = ans.get("linked_policies") or []
            if linked_policies:
                pol_strs = []
                for p in linked_policies:
                    title = p.get("title", "?")
                    ver = p.get("version", "?")
                    pol_strs.append(f"{title} (v{ver})")
                _add_body(doc, f"Linked policies: {', '.join(pol_strs)}")

            linked_assets = ans.get("linked_assets") or []
            if linked_assets:
                asset_strs = []
                for a in linked_assets:
                    name = a.get("name") or a.get("asset_name", "?")
                    atype = a.get("type") or a.get("asset_type", "?")
                    asset_strs.append(f"{name} ({atype})")
                _add_body(doc, f"Linked assets: {', '.join(asset_strs)}")

            linked_team = ans.get("linked_team") or []
            if linked_team:
                _add_body(doc, f"Linked team: {', '.join(t if isinstance(t, str) else t.get('name', str(t)) for t in linked_team)}")

            if status in ("NOT MET", "NOT STARTED", "IN PROGRESS", "PLANNED"):
                remediation = (ans.get("remediation_plan") or "").strip()
                if remediation:
                    _add_body(doc, f"Remediation: {remediation}")

    # ── DC-6.1 Changes ────────────────────────────────────────
    _add_heading_styled(doc, "16. Changes to the System (DC-6.1)", level=1)
    _add_body(doc, DC_SECTION_200["DC-6.1"]["description"])
    _add_kv_table(doc, [
        ("Significant changes", _profile_text(org_profile, "system_changes")),
        ("Change log", _profile_text(org_profile, "change_log")),
    ])

    # ── DC-7.1 Criteria met / not met ─────────────────────────
    _add_heading_styled(doc, "17. Criteria Met and Not Met (DC-7.1)", level=1)
    _add_body(doc, DC_SECTION_200["DC-7.1"]["description"])
    met_ids = [cid for cid in in_scope_ids if answers.get(cid, {}).get("status") in ("MET", "INHERITED")]
    not_met = [cid for cid in in_scope_ids if answers.get(cid, {}).get("status") in ("NOT MET", "NOT STARTED")]
    _add_body(doc, f"Criteria met or inherited: {len(met_ids)} of {total}.")
    _add_body(doc, f"Criteria not met or not started: {len(not_met)} of {total}.")
    if not_met:
        _add_body(doc, "Open criteria: " + ", ".join(not_met[:40]) + ("…" if len(not_met) > 40 else ""))

    # ── DC Section 200 coverage table ─────────────────────────
    _add_heading_styled(doc, "18. Description Criteria (DC Section 200) Coverage", level=1)
    _add_body(doc, "The following table maps this description to AICPA DC Section 200.")
    cov_table = doc.add_table(rows=1, cols=4)
    cov_table.style = "Table Grid"
    hdr = cov_table.rows[0].cells
    for i, h in enumerate(["Criterion", "Title", "Required", "Covered"]):
        hdr[i].text = h
        for run in hdr[i].paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(10)
    for d in dc["dc_200_details"]:
        _add_table_row(cov_table, [
            d["dc_id"],
            d["title"],
            "Required" if d["required"] else "Recommended",
            "Yes" if d["covered"] else "No",
        ])

    # ── Evidence summary ──────────────────────────────────────
    _add_heading_styled(doc, "19. Evidence Summary", level=1)
    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(["Control", "Filename", "Upload Date", "Status"]):
        hdr[i].text = h
        for run in hdr[i].paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(10)
    for cid in in_scope_ids:
        ans = answers.get(cid, {})
        for ev in ans.get("evidence") or []:
            _add_table_row(table, [
                cid,
                ev.get("filename", ""),
                ev.get("upload_date", ""),
                ev.get("review_status", "pending"),
            ])

    # ── Appendices ────────────────────────────────────────────
    _add_heading_styled(doc, "20. Appendices", level=1)

    # Policies
    if policies:
        _add_heading_styled(doc, "Policies", level=2)
        table = doc.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        for i, h in enumerate(["Policy", "Version", "Mapped Controls"]):
            hdr[i].text = h
            for run in hdr[i].paragraphs[0].runs:
                run.bold = True
                run.font.size = Pt(10)
        for p in policies:
            _add_table_row(table, [
                p.get("name", ""),
                p.get("version", ""),
                ", ".join(p.get("mapped_controls") or []),
            ])

    # Exceptions
    open_exceptions = [e for e in exceptions if e.get("status") in ("pending_approval", "approved")]
    if open_exceptions:
        _add_heading_styled(doc, "Exceptions", level=2)
        table = doc.add_table(rows=1, cols=5)
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        for i, h in enumerate(["Control", "Status", "Risk Level", "Description", "Expiry"]):
            hdr[i].text = h
            for run in hdr[i].paragraphs[0].runs:
                run.bold = True
                run.font.size = Pt(10)
        for exc in open_exceptions:
            _add_table_row(table, [
                exc.get("control_id", ""),
                exc.get("status", ""),
                exc.get("risk_level", ""),
                exc.get("description", "")[:80],
                exc.get("expiry_date", ""),
            ])

    # ── Footer ────────────────────────────────────────────────
    for section in doc.sections:
        footer = section.footer
        footer.is_linked_to_previous = False
        para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        para.text = f"{org_name} — System Description — Generated {now}"
        para.style.font.size = Pt(8)
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()
