"""Structured hardware/software asset inventory for SSP appendix export."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List

INVENTORY_COLUMNS = [
    "asset_name",
    "asset_type",
    "in_scope",
    "cui",
    "owner",
    "location",
    "notes",
]

COLUMN_LABELS = {
    "asset_name": "Asset name",
    "asset_type": "Type",
    "in_scope": "In scope",
    "cui": "CUI",
    "owner": "Owner",
    "location": "Location",
    "notes": "Notes",
}


def default_org_inventory() -> Dict[str, Any]:
    return {"assets": [], "updated_at": ""}


def merge_org_inventory(stored: Dict[str, Any] | None) -> Dict[str, Any]:
    inv = default_org_inventory()
    if not stored:
        return inv
    rows = stored.get("assets") or []
    cleaned: List[Dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        cleaned.append({col: str(row.get(col, "")).strip() for col in INVENTORY_COLUMNS})
    inv["assets"] = [r for r in cleaned if any(r.values())]
    inv["updated_at"] = stored.get("updated_at") or ""
    return inv


def inventory_summary(org_inventory: Dict[str, Any] | None) -> str:
    assets = (org_inventory or {}).get("assets") or []
    if not assets:
        return ""
    updated = (org_inventory or {}).get("updated_at") or "not dated"
    return (
        f"Structured asset inventory: {len(assets)} item(s) "
        f"(last updated {updated}). See Appendix — Asset Inventory."
    )


def set_inventory_assets(assets: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "assets": assets,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def inventory_to_rows(org_inventory: Dict[str, Any] | None) -> List[List[str]]:
    assets = (org_inventory or {}).get("assets") or []
    return [[row.get(col, "") for col in INVENTORY_COLUMNS] for row in assets]
