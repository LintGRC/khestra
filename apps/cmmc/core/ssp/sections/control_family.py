"""One control family section — build separately, assembled into section 4."""

from typing import Any, Dict, List, Optional

from controls import CMMC_FRAMEWORK
def ssp_rules_for_control(control_id: str) -> dict:
    """Minimum-proof SSP rules are part of the collectors edition."""
    return {}
from ssp.module_loader import load_for_control
from ssp.sections.module_evidence import add_module_evidence_block, add_policy_reference_block
from ssp.utils import add_placeholder, create_table, risk_severity


def add_control_narratives_intro(doc, *, section_number: int = 5, cui_outline: bool = False) -> None:
    if cui_outline:
        title = f"{section_number}. Security Requirements (NIST SP 800-171 Rev 2)"
        blurb = (
            "Control implementation status for each NIST SP 800-171 Rev 2 requirement in scope. "
            "The official CUI SSP template lists each requirement with Implemented / Planned / "
            "Not Applicable columns; this export uses narrative form with assessment status."
        )
    else:
        title = f"{section_number}. Control Implementation Narratives"
        blurb = (
            "Detailed descriptions of how each applicable NIST SP 800-171 control is implemented. "
            "Content is organized by the fourteen control families."
        )
    doc.add_heading(title, level=1)
    doc.add_paragraph(blurb)


def add_control_family_section(
    doc,
    family_index: int,
    family_name: str,
    controls: list,
    *,
    section_number: int = 5,
    page_break_after: bool = True,
    risks_by_control: dict[str, list[dict]] | None = None,
    org_profile: dict[str, Any] | None = None,
    org_inventory: dict[str, Any] | None = None,
    poam_ids: dict[str, str] | None = None,
) -> None:
    """
    Append one family block (section 4.N) to the document.

    Args:
        controls: List of (control_id, sanitized_answer) tuples.
        risks_by_control: Mapping of control_id -> list of risk dicts to include as evidence.
        org_profile: Organization profile dict for team/personnel lookups.
        org_inventory: Asset inventory dict for asset filtering.
    """
    doc.add_heading(f"{section_number}.{family_index} {family_name}", level=2)

    for cid, ans in controls:
        control_info = CMMC_FRAMEWORK[cid]
        doc.add_heading(f"{cid} - {control_info['name']}", level=3)

        status = ans.get("status", "NOT STARTED")
        weight = control_info.get("weight", 0)
        create_table(
            doc,
            ["Attribute", "Value"],
            [
                ["Status", status],
                ["Impact Level", risk_severity(weight)],
                ["Weight", str(weight)],
            ],
        )

        impl_desc = (
            ans.get("implementation_narrative", "").strip()
            or ans.get("implementation_desc", "").strip()
        )
        poam_id = (poam_ids or {}).get(cid)
        if impl_desc:
            doc.add_paragraph(f"Description: {impl_desc}")
            if status != "MET" and poam_id:
                doc.add_paragraph(f"Remediation tracked in POA&M Item {poam_id}.")
        elif status == "MET":
            add_placeholder(
                doc,
                "Control implementation narrative not provided. Describe how this control is implemented.",
            )
        else:
            if poam_id:
                doc.add_paragraph(
                    f"Description: Control not yet implemented — remediation tracked in POA&M Item {poam_id}."
                )
            else:
                doc.add_paragraph("Description: Control not yet implemented.")

        examine = ans.get("examine", "").strip()
        interview = ans.get("interview", "").strip()
        test = ans.get("test", "").strip()
        evidence_refs = []
        if examine:
            evidence_refs.append(f"Examine: {examine}")
        if interview:
            evidence_refs.append(f"Interview: {interview}")
        if test:
            evidence_refs.append(f"Test: {test}")
        if evidence_refs:
            doc.add_paragraph("Assessment methods: " + "; ".join(evidence_refs))

        evidence_list = ans.get("evidence", [])
        if evidence_list:
            doc.add_paragraph("Attached evidence files:")
            for ev in evidence_list:
                doc.add_paragraph(
                    f"  • {ev.get('filename', 'unknown')} (Uploaded: {ev.get('upload_date', 'n/a')})",
                    style="List Bullet",
                )

        # Linked risks
        linked_risks = (risks_by_control or {}).get(cid, [])
        if linked_risks:
            doc.add_paragraph("Linked risks affecting this control:")
            for r in linked_risks:
                title = r.get("title", "Untitled")
                status = r.get("status", "unknown")
                score = r.get("residual_score", "?")
                doc.add_paragraph(f"    \u2022 {title} \u2014 Residual: {score}, Status: {status}")

        # Linked policies
        linked_policies = ans.get("linked_policies", [])
        if linked_policies:
            doc.add_paragraph("Linked Policies:")
            for p in linked_policies:
                if isinstance(p, str):
                    doc.add_paragraph(f"    \u2022 {p}")
                else:
                    doc.add_paragraph(f"    \u2022 {p.get('title', 'Untitled')} \u2014 Version {p.get('version', '?')}")

        # Linked assets
        linked_assets = ans.get("linked_assets", [])
        if linked_assets:
            doc.add_paragraph("Linked Assets:")
            for a in linked_assets:
                if isinstance(a, str):
                    doc.add_paragraph(f"    \u2022 {a}")
                else:
                    parts = [f"{a.get('name', a.get('asset_name', 'Untitled'))}"]
                    if a.get("type") or a.get("asset_type"):
                        parts.append(f"Type: {a.get('type') or a.get('asset_type')}")
                    if a.get("cui") == "yes":
                        parts.append("CUI: Yes")
                    joined = " \u2014 ".join(parts)
                    doc.add_paragraph(f"    \u2022 {joined}")

        # Linked team members
        linked_team = ans.get("linked_team", [])
        if linked_team:
            doc.add_paragraph("Linked Team Members:")
            for t in linked_team:
                name = t if isinstance(t, str) else t.get("name", str(t))
                doc.add_paragraph(f"    \u2022 {name}")

        # SSP formatting rules (shared module references)
        rules = ssp_rules_for_control(cid)
        for module_name, rule in rules.items():
            render_type = rule.get("render_type", "")
            rows = load_for_control(rule, org_profile or {}, org_inventory)
            if render_type == "FILTERED_GRID":
                add_module_evidence_block(
                    doc, module_name, rows, rule.get("columns", []), rule.get("label", module_name)
                )
            elif render_type == "METADATA_REF":
                add_policy_reference_block(
                    doc, module_name, rows, rule.get("label", module_name)
                )

        # Supporting evidence
        evidence_list = ans.get("evidence") or []
        if evidence_list:
            doc.add_paragraph("Supporting Evidence:")
            for ev in evidence_list:
                title = ev.get("display_title", ev.get("filename", ""))
                if title:
                    doc.add_paragraph(f"    \u2022 {title}")

        doc.add_paragraph()

    if page_break_after:
        doc.add_page_break()
