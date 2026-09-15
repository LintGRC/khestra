"""Asset inventory appendix from structured org_inventory."""

from org_inventory import COLUMN_LABELS, INVENTORY_COLUMNS, inventory_to_rows

from ssp.utils import create_table


def add_asset_inventory_appendix(doc, org_inventory: dict | None) -> None:
    assets = (org_inventory or {}).get("assets") or []
    if not assets:
        return

    doc.add_page_break()
    doc.add_heading("APPENDIX — Asset Inventory", level=1)
    updated = (org_inventory or {}).get("updated_at") or ""
    if updated:
        doc.add_paragraph(f"Last updated in assessment workspace: {updated}")
    doc.add_paragraph(
        "Hardware and software assets in scope for this system. "
        "Maintain this list in the assessment tool and re-export when assets change."
    )
    headers = [COLUMN_LABELS[col] for col in INVENTORY_COLUMNS]
    create_table(doc, headers, inventory_to_rows(org_inventory))
