"""Demo session detection and clear — no Streamlit."""

from __future__ import annotations

from typing import Any, Dict, Optional

from controls import CMMC_FRAMEWORK
from demo_data import DEMO_ORG_NAME
from demo_data_b import DEMO_B_ORG_NAME
from env_scope import default_env_scope
from org_inventory import merge_org_inventory
from org_profile import default_control_answer, default_org_profile
from org_assets import merge_org_assets
from scope_ui import apply_scope_from_assets, default_asset_scope

DEMO_ORG_NAMES = frozenset({DEMO_ORG_NAME, DEMO_B_ORG_NAME})
DEMO_LABELS = {"apex": "Apex Defense", "bridgeport": "Bridgeport Systems"}


def is_demo_org(org_profile: Dict[str, str] | None) -> bool:
    name = (org_profile or {}).get("org_name", "").strip()
    return name in DEMO_ORG_NAMES


def demo_id_for_org(org_name: str) -> Optional[str]:
    if org_name == DEMO_ORG_NAME:
        return "apex"
    if org_name == DEMO_B_ORG_NAME:
        return "bridgeport"
    return None


def demo_status(org_profile: Dict[str, str]) -> Dict[str, Any]:
    if not is_demo_org(org_profile):
        return {"is_demo": False}
    name = (org_profile.get("org_name") or "").strip()
    demo_id = demo_id_for_org(name) or ""
    return {
        "is_demo": True,
        "demo_id": demo_id,
        "org_name": name,
        "label": DEMO_LABELS.get(demo_id, name),
    }


def start_fresh_workspace_state(state: Dict[str, Any], asset_types: Dict[str, str]) -> Dict[str, Any]:
    """Blank workspace — keeps client_id only."""
    asset_scope = default_asset_scope(asset_types)
    return {
        **state,
        "client_id": state.get("client_id"),
        "org_name": "",
        "org_profile": default_org_profile(),
        "asset_scope": asset_scope,
        "scoped_controls": apply_scope_from_assets(asset_scope),
        "answers": {cid: default_control_answer() for cid in CMMC_FRAMEWORK},
        "audit_log": [],
        "sprs_history": [],
        "org_assets": merge_org_assets(None),
        "org_asset_bytes": {},
        "org_inventory": merge_org_inventory(None),
        "restored_evidence": {},
        "env_scope": default_env_scope(),
        "scope_confirmed": False,
        "last_export_at": None,
        "assessment_fingerprint_at_export": None,
    }
