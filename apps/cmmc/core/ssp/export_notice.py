"""Optional footer on Word export — one line, not a lecture."""

from datetime import datetime

from docx.shared import Pt


def workspace_snapshot_notice_text() -> str:
    return (
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} from local assessment data. "
        "For the current version, export again from the CMMC assessment tool after any control or profile changes."
    )


def add_cover_snapshot_notice(doc) -> None:
    """Modular SSP cover — omit; journey + Report Center handle freshness."""
    return


def append_workspace_snapshot_notice(doc) -> None:
    """End of SSP — subtle generated-on line."""
    doc.add_paragraph()
    para = doc.add_paragraph(workspace_snapshot_notice_text())
    if para.runs:
        para.runs[0].font.size = Pt(8)
