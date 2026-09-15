"""Record of Changes appendix from session audit_log."""

from change_history import describe_change

from ssp.utils import create_table


def add_record_of_changes(doc, audit_log: list | None, *, max_rows: int = 75) -> None:
    entries = audit_log or []
    if not entries:
        return

    doc.add_page_break()
    doc.add_heading("Record of Changes", level=1)
    doc.add_paragraph(
        "Changes captured automatically when control data is updated in the assessment workspace."
    )

    rows = []
    for entry in reversed(entries[-max_rows:]):
        rows.append(
            [
                entry.get("timestamp", ""),
                entry.get("user_role", ""),
                entry.get("control_id", ""),
                describe_change(entry),
            ]
        )
    create_table(doc, ["Date / time", "Role", "Control", "Change"], rows)
