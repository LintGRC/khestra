from controls import CMMC_FRAMEWORK

from ssp.utils import create_table, sanitize_answers


def add_evidence_appendix(doc, answers: dict, scoped_controls: list, *, section_number: int = 6) -> None:
    doc.add_heading(f"{section_number}. Evidence Appendix", level=1)
    doc.add_paragraph(
        "References to evidence supporting control implementations described in this SSP."
    )

    sanitized = sanitize_answers(answers)
    evidence_count = 0

    for cid in scoped_controls:
        if cid not in CMMC_FRAMEWORK or cid not in sanitized:
            continue
        evidence_list = sanitized[cid].get("evidence", [])
        if not evidence_list:
            continue

        control_info = CMMC_FRAMEWORK[cid]
        doc.add_heading(f"{cid} - {control_info['name']}", level=2)
        rows = []
        for ev in evidence_list:
            ev_type = ev.get("evidence_type", "other")
            title = ev.get("display_title", ev.get("filename", "unknown"))
            version = ev.get("evidence_version", "")
            sha = ev.get("sha256", "")
            if len(sha) > 16:
                sha = sha[:16] + "..."
            rows.append([
                ev_type,
                title,
                version,
                ev.get("upload_date", "n/a"),
                sha,
            ])
        create_table(doc, ["Type", "Description", "Version", "Upload Date", "Hash"], rows)
        evidence_count += len(evidence_list)

    if evidence_count == 0:
        doc.add_paragraph("No evidence attachments have been provided for scoped controls.")
