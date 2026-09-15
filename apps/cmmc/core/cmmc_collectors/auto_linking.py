"""One-time auto-populate linked_assets from inventory by matching asset_type."""

from __future__ import annotations

from typing import Any, Dict, List


def auto_link_assets(
    control_id: str,
    answer: Dict[str, Any],
    linking_profile: Dict[str, Any] | None,
    org_inventory: Dict[str, Any] | None,
) -> List[Dict[str, Any]]:
    """Return auto-matched assets from inventory, or empty list if already linked / not applicable.

    Only runs once — subsequent calls return [].
    Caller should save matched assets + _auto_linked flag to the answer.
    """
    if answer.get("_auto_linked"):
        return []
    if answer.get("linked_assets"):
        return []

    if not linking_profile:
        return []
    assets_profile = linking_profile.get("assets")
    if not assets_profile:
        return []
    suggested = assets_profile.get("suggested", [])
    if not suggested:
        return []

    inventory = org_inventory.get("assets", []) if isinstance(org_inventory, dict) else []
    if not inventory:
        return []

    matched = [
        a for a in inventory
        if (a.get("asset_type") or a.get("type") or "") in suggested
    ]
    return matched
