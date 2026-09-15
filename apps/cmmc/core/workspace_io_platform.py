"""Workspace ZIP and OSCAL export — no Streamlit."""

from __future__ import annotations

import json
import uuid
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Dict, List, Tuple

from app_config import APP_VERSION
from catalog_migration import migrate_scoped_controls
from controls import CMMC_FRAMEWORK
from env_scope import default_env_scope, merge_env_scope
from evidence_store import answers_without_evidence_bytes, evidence_file_key, get_evidence_bytes
from org_assets import merge_org_assets, storage_key_from_disk_name
from org_inventory import merge_org_inventory
from org_profile import default_control_answer, merge_org_profile
from persistence import answers_from_saved
from scope_ui import apply_scope_from_assets
from security_utils import validate_workspace_zip
from workspace_flags import resolve_scope_confirmed


def export_oscal_json(
    answers: Dict[str, Any],
    asset_scope: Dict[str, Any],
    audit_log: List[Dict],
    org_name: str,
) -> str:
    oscal_data = {
        "system-security-plan": {
            "uuid": str(uuid.uuid4()),
            "metadata": {
                "title": f"CMMC Assessment - {org_name}",
                "last-modified": datetime.now(timezone.utc).isoformat(),
                "version": APP_VERSION,
                "oscal-version": "1.0.4",
            },
            "import-profile": {
                "href": "https://raw.githubusercontent.com/usnistgov/oscal-content/master/nist.gov/SP800-171/rev-2/json/NIST_SP-800-171_rev2_catalog.json"
            },
            "control-implementation": {
                "description": "CMMC Level 2 Control Implementation",
                "implemented-requirements": [],
            },
        }
    }
    for cid, answer in answers.items():
        if cid not in CMMC_FRAMEWORK:
            continue
        oscal_data["system-security-plan"]["control-implementation"]["implemented-requirements"].append(
            {
                "uuid": str(uuid.uuid4()),
                "control-id": cid,
                "description": CMMC_FRAMEWORK[cid]["name"],
                "props": [
                    {"name": "implementation-status", "value": answer.get("status", "NOT STARTED")},
                    {"name": "weight", "value": str(CMMC_FRAMEWORK[cid]["weight"])},
                    {"name": "family", "value": CMMC_FRAMEWORK[cid]["family"]},
                    {"name": "maturity", "value": answer.get("maturity", "Ad Hoc")},
                ],
                "statements": [
                    {
                        "statement-id": f"{cid}_stmt",
                        "description": answer.get("implementation_narrative")
                        or answer.get("implementation_desc", "No implementation description provided"),
                    }
                ],
            }
        )
    return json.dumps(oscal_data, indent=2)


def export_oscal_poam_json(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    org_name: str,
) -> str:
    """OSCAL 1.0.4 plan-of-action-and-milestones export for the current gap set.

    Uses the same gap definition and weakness numbering as the POA&M workbook
    (poam_gap_controls / poam_weakness_ids), so the machine-readable artifact
    links 1:1 with the exported spreadsheet and the SSP cross-references.
    """
    from poam_export import poam_gap_controls, poam_weakness_ids

    gaps = poam_gap_controls(answers, scoped_controls)
    weakness_ids = poam_weakness_ids(answers, scoped_controls)
    poam_items = []
    for cid in gaps:
        ans = answers.get(cid, {})
        weight = CMMC_FRAMEWORK.get(cid, {}).get("weight", 0)
        target_date = ans.get("target_date", "")
        item = {
            "uuid": str(uuid.uuid4()),
            "title": f"{cid} - {CMMC_FRAMEWORK.get(cid, {}).get('name', cid)}",
            "description": ans.get("assessor_notes", ""),
            "props": [
                {"name": "control-id", "value": cid},
                {"name": "weakness-id", "value": weakness_ids.get(cid, "")},
                {"name": "weight", "value": str(weight)},
                {"name": "poam-eligible", "value": "true"},
                {"name": "closeout-days", "value": "180"},
            ],
            "related-requirements": [{"requirement-id": cid}],
            "remediation": {
                "description": ans.get("remediation_plan", "") or "Draft plan",
            },
        }
        if target_date:
            item["remediation"]["target-date"] = target_date
        poam_items.append(item)

    oscal_data = {
        "plan-of-action-and-milestones": {
            "uuid": str(uuid.uuid4()),
            "metadata": {
                "title": f"CMMC POA&M - {org_name}",
                "last-modified": datetime.now(timezone.utc).isoformat(),
                "version": APP_VERSION,
                "oscal-version": "1.0.4",
            },
            "poam-items": poam_items,
        }
    }
    return json.dumps(oscal_data, indent=2)


def build_workspace_zip(state: Dict[str, Any]) -> bytes:
    out_zip = BytesIO()
    clean_answers = {}
    evidence_binaries: Dict[str, bytes] = {}
    restored = state.get("restored_evidence") or {}

    for cid, data in state["answers"].items():
        clean_answers[cid] = dict(data)
        clean_evidence_metadata = []
        for ev in data.get("evidence") or []:
            ev_meta = {k: v for k, v in ev.items() if k != "data_bytes"}
            fkey = evidence_file_key(cid, ev.get("filename", ""))
            blob = get_evidence_bytes(cid, ev, restored)
            if blob:
                evidence_binaries[fkey] = blob
            clean_evidence_metadata.append(ev_meta)
        clean_answers[cid]["evidence"] = clean_evidence_metadata

    payload = {
        "version": APP_VERSION,
        "org_name": state.get("org_name", ""),
        "org_profile": state.get("org_profile", {}),
        "answers": clean_answers,
        "audit_log": state.get("audit_log", []),
        "asset_scope": state.get("asset_scope", {}),
        "scoped_controls": state.get("scoped_controls"),
        "current_role": state.get("current_role", "Assessor"),
        "current_user_name": state.get("current_user_name", ""),
        "sprs_history": state.get("sprs_history", []),
        "org_assets": state.get("org_assets", {}),
        "org_inventory": state.get("org_inventory", {}),
        "env_scope": state.get("env_scope", {}),
        "scope_confirmed": bool(state.get("scope_confirmed")),
        "msp_mode": bool(state.get("msp_mode")),
    }

    org_bytes = dict(state.get("org_asset_bytes") or {})

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("state.json", json.dumps(payload, indent=2))
        for fkey, binary in evidence_binaries.items():
            z.writestr(f"evidence/{fkey}", binary)
        for fkey, binary in org_bytes.items():
            z.writestr(f"org_assets/{fkey.replace(':', '__')}", binary)

    return out_zip.getvalue()


def load_workspace_zip_bytes(zip_bytes: bytes) -> Tuple[Dict[str, Any], List[str]]:
    """Parse workspace zip → state dict for save_workspace. Returns (state, warnings)."""
    ok, err = validate_workspace_zip(BytesIO(zip_bytes))
    if not ok:
        raise ValueError(err or "Invalid workspace archive")

    warnings: List[str] = []
    with zipfile.ZipFile(BytesIO(zip_bytes)) as z:
        if "state.json" not in z.namelist():
            raise ValueError("Missing state.json in workspace archive.")

        state_data = json.loads(z.read("state.json").decode("utf-8"))
        restored_evidence: Dict[str, bytes] = {}
        org_bytes: Dict[str, bytes] = {}

        for fpath in z.namelist():
            if fpath.startswith("evidence/"):
                restored_evidence[fpath.replace("evidence/", "", 1)] = z.read(fpath)
            elif fpath.startswith("org_assets/"):
                fkey = storage_key_from_disk_name(fpath.replace("org_assets/", "", 1))
                org_bytes[fkey] = z.read(fpath)

        org_name = state_data.get("org_name", "")
        org_profile = merge_org_profile(state_data.get("org_profile"), org_name)
        asset_scope = state_data.get("asset_scope") or {}
        saved_scope = state_data.get("scoped_controls")
        if saved_scope:
            scoped = migrate_scoped_controls(saved_scope)
        else:
            scoped = apply_scope_from_assets(asset_scope)

        answers = answers_from_saved(state_data.get("answers"))
        for cid, blob_map in restored_evidence.items():
            if "_" not in cid:
                continue
            control_id, _ = cid.split("_", 1)
            if control_id in answers:
                for ev in answers[control_id].get("evidence") or []:
                    if evidence_file_key(control_id, ev.get("filename", "")) == cid:
                        ev["data_bytes"] = blob_map

        return {
            "client_id": state_data.get("client_id"),
            "org_name": org_name,
            "org_profile": org_profile,
            "answers": answers,
            "audit_log": state_data.get("audit_log", []),
            "asset_scope": asset_scope,
            "scoped_controls": scoped,
            "current_role": state_data.get("current_role", "Assessor"),
            "current_user_name": state_data.get("current_user_name", ""),
            "sprs_history": state_data.get("sprs_history", []),
            "org_assets": merge_org_assets(state_data.get("org_assets")),
            "org_asset_bytes": org_bytes,
            "org_inventory": merge_org_inventory(state_data.get("org_inventory")),
            "scope_confirmed": resolve_scope_confirmed(state_data),
            "env_scope": merge_env_scope(state_data.get("env_scope")),
            "restored_evidence": restored_evidence,
            "msp_mode": bool(state_data.get("msp_mode")),
        }, warnings


def reset_workspace_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Clear assessment while keeping client_id."""
    from org_profile import default_org_profile

    asset_scope = state.get("asset_scope") or {}
    return {
        **state,
        "org_name": "Your Organization",
        "org_profile": default_org_profile(),
        "answers": {cid: default_control_answer() for cid in CMMC_FRAMEWORK},
        "audit_log": [],
        "sprs_history": [],
        "org_assets": merge_org_assets(None),
        "org_asset_bytes": {},
        "org_inventory": merge_org_inventory(None),
        "scope_confirmed": False,
        "last_export_at": None,
        "assessment_fingerprint_at_export": None,
        "env_scope": default_env_scope(),
        "restored_evidence": {},
        "scoped_controls": apply_scope_from_assets(asset_scope),
    }


def reset_controls_only(state: Dict[str, Any]) -> Dict[str, Any]:
    """Keeps organization profile and scope; clears control answers only."""
    return {
        **state,
        "answers": {cid: default_control_answer() for cid in CMMC_FRAMEWORK},
        "audit_log": [],
        "sprs_history": [],
        "restored_evidence": {},
        "last_export_at": None,
        "assessment_fingerprint_at_export": None,
    }
