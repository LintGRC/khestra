"""POA&M section embedded in the SSP — uses the same columns as the standalone Excel export."""

from poam_export import POAM_COLUMNS, build_poam_dataframe


def add_poam_section(doc, answers: dict, scoped_controls: list, *, section_number: int = 4) -> None:
    title = f"{section_number}. Plan of Action and Milestones (POA&M)"
    doc.add_heading(title, level=1)
    doc.add_paragraph(
        "Open security weaknesses requiring corrective action. This table matches the standalone "
        "POA&M Excel export from Report Center. The official DoW CUI SSP template does not "
        "include a separate POA&M appendix — gaps are also documented per control in section "
        f"{section_number + 1}."
    )

    df = build_poam_dataframe(answers, scoped_controls)
    if df.empty:
        doc.add_paragraph("No outstanding POA&M items for scoped controls.")
        doc.add_page_break()
        return

    headers = list(df.columns)
    rows = [list(row) for row in df.itertuples(index=False, name=None)]
    from ssp.utils import create_table

    create_table(doc, headers, rows)
    doc.add_paragraph(f"Total outstanding items: {len(rows)}")
    doc.add_page_break()
