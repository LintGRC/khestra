"""Section 1 — official DoW CUI SSP system identification outline."""

from controls import CMMC_FRAMEWORK

from ssp.utils import add_placeholder


def add_system_identification(
    doc,
    org_profile: dict | None = None,
    asset_scope: dict | None = None,
    answers: dict | None = None,
    scoped_controls: list | None = None,
    sprs_result: dict | None = None,
) -> None:
    profile = org_profile or {}
    scope = asset_scope or {}
    org_name = (profile.get("org_name") or "Organization").strip()
    system_name = (profile.get("system_name") or "Information System").strip()
    system_uid = (profile.get("system_unique_id") or "").strip()

    def field(key: str, fallback: str) -> str:
        value = (profile.get(key) or "").strip()
        return value if value else fallback

    doc.add_heading("1. SYSTEM IDENTIFICATION", level=1)

    doc.add_heading("1.1. System Name/Title:", level=2)
    doc.add_paragraph(system_name)

    doc.add_heading("1.1.1. System Categorization:", level=3)
    doc.add_paragraph("Moderate Impact for Confidentiality")

    doc.add_heading("1.1.2. System Unique Identifier:", level=3)
    if system_uid:
        doc.add_paragraph(system_uid)
    else:
        add_placeholder(doc, "Insert the System Unique Identifier (e.g., internal asset ID or eMASS identifier).")

    doc.add_heading("1.2. Responsible Organization:", level=2)
    doc.add_paragraph(f"Name: {org_name}")
    doc.add_paragraph(f"CAGE Code: {field('cage_code', '[CAGE code]')}")
    doc.add_paragraph(f"UEI: {field('uei', '[Unique Entity Identifier]')}")
    doc.add_paragraph(f"Address: {field('org_address', '[Organization address]')}")
    doc.add_paragraph(f"Phone: {field('org_phone', '[Organization phone]')}")

    doc.add_heading("1.2.1. Information Owner (Government point of contact responsible for CUI):", level=3)
    doc.add_paragraph(f"Name: {field('gov_poc_name', '[Government POC name, if applicable]')}")
    doc.add_paragraph(f"Title: {field('gov_poc_title', '[Title]')}")
    doc.add_paragraph(f"Office Address: {field('gov_poc_address', '[Office address]')}")
    doc.add_paragraph(f"Work Phone: {field('gov_poc_phone', '[Work phone]')}")
    doc.add_paragraph(f"e-Mail Address: {field('gov_poc_email', '[e-mail address]')}")

    doc.add_heading("1.2.1.1. System Owner (assignment of security responsibility):", level=4)
    doc.add_paragraph(f"Name: {field('system_owner', '[System owner name]')}")
    doc.add_paragraph(f"Title: {field('system_owner_title', '[Title]')}")
    doc.add_paragraph("Office Address: [Office address]")
    doc.add_paragraph("Work Phone: [Work phone]")
    doc.add_paragraph("e-Mail Address: [e-mail address]")

    doc.add_heading("1.2.1.2. System Security Officer:", level=4)
    doc.add_paragraph(f"Name: {field('iso_name', '[System security officer name]')}")
    doc.add_paragraph(f"Title: {field('iso_title', '[Title]')}")
    doc.add_paragraph("Office Address: [Office address]")
    doc.add_paragraph("Work Phone: [Work phone]")
    doc.add_paragraph("e-Mail Address: [e-mail address]")

    doc.add_heading("1.3. General Description/Purpose of System:", level=2)
    if profile.get("system_description", "").strip():
        doc.add_paragraph(profile["system_description"].strip())
    else:
        add_placeholder(
            doc,
            "What is the function/purpose of the system? Provide a short, high-level description.",
        )

    if sprs_result and answers is not None and scoped_controls is not None:
        scoped = [cid for cid in scoped_controls if cid in answers]
        total = len(scoped)
        met = sum(1 for cid in scoped if answers[cid].get("status") == "MET")
        readiness = round((met / total) * 100, 1) if total else 0
        sprs_score = sprs_result.get("final_score", "N/A")
        doc.add_paragraph(
            f"Assessment status: SPRS score {sprs_score}/110; {readiness}% of scoped controls "
            f"marked MET ({met} of {total})."
        )
        critical = [
            cid
            for cid in scoped
            if answers[cid].get("status") not in ("MET", "NOT APPLICABLE", "INHERITED")
            and CMMC_FRAMEWORK[cid]["weight"] >= 5
        ]
        if critical:
            doc.add_paragraph(
                f"Open critical gaps (5-point controls): {len(critical)} — "
                f"examples include {', '.join(critical[:3])}."
            )

    cui_level = scope.get("CUI Assets", 0)
    if cui_level > 0:
        doc.add_paragraph(
            f"The system processes Controlled Unclassified Information (CUI); "
            f"CUI assets represent {cui_level}% of scoped assets."
        )

    doc.add_page_break()
