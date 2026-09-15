"""Import asset inventory from CSV into org_inventory.assets."""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Tuple

from org_inventory import INVENTORY_COLUMNS

COLUMN_ALIASES = {
    "asset name": "asset_name",
    "asset_name": "asset_name",
    "name": "asset_name",
    "hostname": "asset_name",
    "type": "asset_type",
    "asset type": "asset_type",
    "asset_type": "asset_type",
    "in scope": "in_scope",
    "in_scope": "in_scope",
    "scope": "in_scope",
    "cui": "cui",
    "processes cui": "cui",
    "owner": "owner",
    "location": "location",
    "site": "location",
    "notes": "notes",
    "description": "notes",
}


def _normalize_header(header: str) -> str:
    return (header or "").strip().lower()


def _map_row(raw: Dict[str, str]) -> Dict[str, str]:
    mapped: Dict[str, str] = {}
    for key, val in raw.items():
        field = COLUMN_ALIASES.get(_normalize_header(key))
        if field and (val or "").strip():
            mapped[field] = val.strip()
    return mapped


def import_inventory_csv(file_bytes: bytes) -> Tuple[List[Dict[str, str]], List[str]]:
    """Return (asset rows, warnings)."""
    text = file_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return [], ["CSV has no header row."]

    assets: List[Dict[str, str]] = []
    warnings: List[str] = []

    for i, raw in enumerate(reader, start=2):
        row = _map_row(raw)
        if not row.get("asset_name"):
            warnings.append(f"Row {i}: missing asset name — skipped.")
            continue
        asset = {col: row.get(col, "") for col in INVENTORY_COLUMNS}
        assets.append(asset)

    if not assets:
        warnings.append("No asset rows found. Expected columns: asset_name, asset_type, in_scope, cui, owner, location, notes.")

    return assets, warnings
