"""Gap analysis report — per-gap recommendations as DOCX."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List

from docx import Document
from docx.shared import Pt

from evidence_hints import get_pof_hints


def _build_recommendations(gap: Dict[str, Any], pof_hints: List[str]) -> List[str]:
    recs: List[str] = []
    status = gap.get("status", "")
    has_evidence = gap.get("has_evidence", False)
    has_narrative = gap.get("has_narrative", False)
    owner = gap.get("owner", "") or ""
    cid = gap.get("control_id", "")

    if not owner:
        recs.append(f"Assign a control owner for {cid}.")
    if status == "NOT STARTED":
        if not has_narrative:
            recs.append(f"Write an implementation narrative describing how {cid} is addressed.")
        if not has_evidence:
            recs.append(f"Upload evidence artifacts for {cid}.")
        recs.append(f"Set the control status from NOT STARTED to an appropriate assessment status.")
    elif status == "NOT MET":
        if not has_evidence:
            recs.append(f"Upload evidence demonstrating compliance for {cid}.")
        if not has_narrative:
            recs.append(f"Document the implementation approach for {cid} in the narrative field.")
    else:
        if not has_evidence:
            recs.append(f"Upload supporting evidence for {cid}.")
        if not has_narrative:
            recs.append(f"Add an implementation narrative for {cid}.")

    if pof_hints:
        recs.append(f"Consider collecting these artifacts for {cid}:")
        recs.extend(f"  • {h}" for h in pof_hints[:3])

    return recs


def generate_gap_analysis(ws: Dict[str, Any]) -> bytes:
    from readiness_assessment import run_readiness_assessment
    from soc2_catalog import SOC2_CONTROLS

    assessment = run_readiness_assessment(ws)
    gaps: List[Dict[str, Any]] = assessment.get("open_gaps", [])
    missing_ev: List[Dict[str, Any]] = assessment.get("missing_evidence", [])
    missing_narr: List[Dict[str, Any]] = assessment.get("missing_narrative", [])
    missing_ev_ids = {m["control_id"] for m in missing_ev}
    missing_narr_ids = {m["control_id"] for m in missing_narr}

    org = ws.get("org_name") or "Organization"
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)

    h = doc.add_heading
    h(f"Gap Analysis — {org}", level=0)
    doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}").style = doc.styles["Normal"]

    doc.add_heading("Summary", level=1)

    stats = [
        f"Total in-scope controls: {assessment.get('controls_total', 0)}",
        f"Readiness: {assessment.get('readiness_pct', 0):.0f}%",
        f"Composite score: {assessment.get('composite_score', 0):.0f}%",
        f"Open gaps: {assessment.get('gap_count', 0)}",
        f"Controls met (complete) but missing evidence: {len(missing_ev)}",
        f"Controls met (complete) but missing narrative: {len(missing_narr)}",
    ]
    for s in stats:
        doc.add_paragraph(s, style="List Bullet")

    if not gaps and not missing_ev and not missing_narr:
        doc.add_paragraph("No gaps identified. All controls are complete.", style="List Bullet")
        out = BytesIO()
        doc.save(out)
        return out.getvalue()

    doc.add_heading("Action Plan by Priority", level=1)

    cid_order = set()
    for g in gaps:
        cid_order.add(g["control_id"])
    for m in missing_ev:
        cid_order.add(m["control_id"])
    for m in missing_narr:
        cid_order.add(m["control_id"])

    for cid in sorted(cid_order):
        gap = next((g for g in gaps if g["control_id"] == cid), None)
        is_missing_ev = cid in missing_ev_ids
        is_missing_narr = cid in missing_narr_ids

        control_meta = SOC2_CONTROLS.get(cid, {})
        gap_name = ""
        if gap:
            gap_name = gap.get("name", "")
        if not gap_name:
            for src in (missing_ev, missing_narr):
                for item in src:
                    if item["control_id"] == cid:
                        gap_name = item.get("name", "")
                        break
                if gap_name:
                    break
        name = gap_name or control_meta.get("title", "")
        doc.add_heading(f"{cid} — {name}", level=2)

        if gap:
            doc.add_paragraph(f"Status: {gap['status']}", style="List Bullet")
            pof_hints: List[str] = []
            for pof in control_meta.get("points_of_focus", []):
                pof_hints.extend(get_pof_hints(pof))
            recs = _build_recommendations(gap, pof_hints)
            for r in recs:
                doc.add_paragraph(r, style="List Bullet")
        else:
            if is_missing_ev:
                doc.add_paragraph("Status is complete but missing evidence — upload artifacts.", style="List Bullet")
            if is_missing_narr:
                doc.add_paragraph("Status is complete but missing narrative — document implementation.", style="List Bullet")

    out = BytesIO()
    doc.save(out)
    return out.getvalue()
