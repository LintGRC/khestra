"""Load/save workspace from disk — standalone platform (no Streamlit)."""

from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app_config import APP_VERSION, ASSET_TYPES
from catalog_migration import migrate_scoped_controls
from client_workspaces import (
    active_client_id,
    client_evidence_dir,
    client_org_assets_dir,
    client_session_path,
    ensure_default_client,
    list_clients,
    set_active_client_id,
)
from kevidence.types import CheckResult
from controls import CMMC_FRAMEWORK
from env_scope import default_env_scope, merge_env_scope
from evidence_store import answers_without_evidence_bytes, load_evidence_from_disk, persist_evidence_to_disk
from org_assets import load_org_assets_from_disk, merge_org_assets, persist_org_assets_to_disk
from org_inventory import merge_org_inventory
from org_profile import default_control_answer, default_org_profile, merge_org_profile
from persistence import answers_from_saved
from readiness_review import assessment_changed_since_export, assessment_fingerprint
from scope_ui import apply_scope_from_assets, default_asset_scope
from workspace_flags import resolve_scope_confirmed


def _session_path(client_id: str) -> Path:
    ensure_default_client()
    return client_session_path(client_id)


def _org_assets_path(client_id: str) -> Path:
    return client_org_assets_dir(client_id)


def _evidence_path(client_id: str) -> Path:
    return client_evidence_dir(client_id)


def _empty_workspace(client_id: str) -> Dict[str, Any]:
    asset_scope = default_asset_scope(ASSET_TYPES)
    return {
        "client_id": client_id,
        "version": APP_VERSION,
        "org_name": "Your Organization",
        "org_profile": default_org_profile(),
        "answers": {cid: default_control_answer() for cid in CMMC_FRAMEWORK},
        "audit_log": [],
        "asset_scope": asset_scope,
        "scoped_controls": apply_scope_from_assets(asset_scope),
        "current_role": "Assessor",
        "current_user_name": "",
        "msp_mode": False,
        "sprs_history": [],
        "org_assets": merge_org_assets(None),
        "org_asset_bytes": {},
        "org_inventory": merge_org_inventory(None),
        "live_asset_snapshots": {},
        "scope_confirmed": False,
        "last_export_at": None,
        "assessment_fingerprint_at_export": None,
        "cmmc_assessment": {},
        "cmmc_scope": {},
        "contracts": [],
        "answers_l1": {},
        "l1_assessment": {},
        "env_scope": default_env_scope(),
        "restored_evidence": {},
    }


def load_workspace(client_id: Optional[str] = None) -> Dict[str, Any]:
    cid = client_id or active_client_id()
    from sandbox_access import enforce_org_access_for_workspace

    enforce_org_access_for_workspace(cid)
    path = _session_path(cid)
    if not path.exists():
        return _empty_workspace(cid)

    try:
        with open(path, encoding="utf-8") as f:
            loaded = json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"WARNING: Corrupt workspace file {path}, resetting to empty workspace", file=sys.stderr)
        return _empty_workspace(cid)

    org_name = loaded.get("org_name", "")
    disk_assets, disk_bytes = load_org_assets_from_disk(folder=_org_assets_path(cid))
    asset_scope = loaded.get("asset_scope") or default_asset_scope(ASSET_TYPES)
    saved_scope = loaded.get("scoped_controls")
    if saved_scope:
        scoped = migrate_scoped_controls(saved_scope)
    else:
        scoped = apply_scope_from_assets(asset_scope)

    return {
        "client_id": cid,
        "version": loaded.get("version", APP_VERSION),
        "org_name": org_name,
        "org_profile": merge_org_profile(loaded.get("org_profile"), org_name),
        "answers": answers_from_saved(loaded.get("answers")),
        "audit_log": loaded.get("audit_log", []),
        "asset_scope": asset_scope,
        "scoped_controls": scoped,
        "current_role": loaded.get("current_role", "Assessor"),
        "current_user_name": loaded.get("current_user_name", ""),
        "sprs_history": loaded.get("sprs_history", []),
        "org_assets": merge_org_assets(loaded.get("org_assets")) if loaded.get("org_assets") else disk_assets,
        "org_asset_bytes": disk_bytes,
        "org_inventory": merge_org_inventory(loaded.get("org_inventory")),
        "live_asset_snapshots": loaded.get("live_asset_snapshots") or {},
        "scope_confirmed": resolve_scope_confirmed(loaded),
        "last_export_at": loaded.get("last_export_at"),
        "assessment_fingerprint_at_export": loaded.get("assessment_fingerprint_at_export"),
        "env_scope": merge_env_scope(loaded.get("env_scope")),
        "restored_evidence": load_evidence_from_disk(_evidence_path(cid)),
        "cmmc_assessment": loaded.get("cmmc_assessment") or {},
        "cmmc_scope": loaded.get("cmmc_scope") or {},
        "contracts": loaded.get("contracts") or [],
        "answers_l1": loaded.get("answers_l1") or {},
        "l1_assessment": loaded.get("l1_assessment") or {},
        "msp_mode": bool(loaded.get("msp_mode")),
    }


def save_workspace(state: Dict[str, Any]) -> None:
    cid = state.get("client_id") or active_client_id()
    from sandbox_access import enforce_org_access_for_workspace

    enforce_org_access_for_workspace(cid)
    all_entries = []
    for ans in state["answers"].values():
        all_entries.extend(ans.get("evidence") or [])
    persist_evidence_to_disk(
        _evidence_path(cid),
        all_entries,
        cid,
        state.get("restored_evidence"),
    )
    payload = {
        "version": APP_VERSION,
        "org_name": state.get("org_name", ""),
        "org_profile": state.get("org_profile", {}),
        "answers": answers_without_evidence_bytes(state["answers"]),
        "audit_log": state.get("audit_log", []),
        "asset_scope": state.get("asset_scope", {}),
        "current_role": state.get("current_role", "Assessor"),
        "current_user_name": state.get("current_user_name", ""),
        "sprs_history": state.get("sprs_history", []),
        "org_assets": state.get("org_assets", {}),
        "org_inventory": state.get("org_inventory", {}),
        "live_asset_snapshots": state.get("live_asset_snapshots") or {},
        "scope_confirmed": bool(state.get("scope_confirmed")),
        "last_export_at": state.get("last_export_at"),
        "assessment_fingerprint_at_export": state.get("assessment_fingerprint_at_export"),
        "env_scope": state.get("env_scope", default_env_scope()),
        "cmmc_assessment": state.get("cmmc_assessment") or {},
        "cmmc_scope": state.get("cmmc_scope") or {},
        "contracts": state.get("contracts") or [],
        "answers_l1": state.get("answers_l1") or {},
        "l1_assessment": state.get("l1_assessment") or {},
        "msp_mode": bool(state.get("msp_mode")),
    }
    scoped = state.get("scoped_controls")
    if scoped:
        payload["scoped_controls"] = scoped

    path = _session_path(cid)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)

    persist_org_assets_to_disk(
        state.get("org_assets", {}),
        state.get("org_asset_bytes", {}),
        folder=_org_assets_path(cid),
    )


def persist_live_asset_snapshot(
    connector_id: str,
    checks: List[CheckResult],
    *,
    client_id: Optional[str] = None,
    synced_at: str,
) -> None:
    """Save connector-derived live assets into the active workspace."""
    from scope_coverage import apply_live_asset_snapshot

    ws = load_workspace(client_id)
    ws = apply_live_asset_snapshot(ws, connector_id, checks, synced_at=synced_at)
    save_workspace(ws)


def export_stamp(state: Dict[str, Any]) -> Dict[str, str]:
    fp = assessment_fingerprint(state["answers"], state["scoped_controls"])
    stamped = datetime.now().isoformat(timespec="seconds")
    return {"last_export_at": stamped, "assessment_fingerprint_at_export": fp}


def export_stale(state: Dict[str, Any]) -> bool:
    return assessment_changed_since_export(
        state["answers"],
        state["scoped_controls"],
        state.get("assessment_fingerprint_at_export"),
    )


def log_change(
    audit_log: List[Dict[str, Any]],
    control_id: str,
    field: str,
    old_val: Any,
    new_val: Any,
    role: str = "Assessor",
) -> None:
    from assessment_helpers import log_audit_event

    log_audit_event(audit_log, control_id, field, old_val, new_val, role)


def patch_control(
    state: Dict[str, Any],
    control_id: str,
    *,
    status: Optional[str] = None,
    implementation_narrative: Optional[str] = None,
    assessor_notes: Optional[str] = None,
    examine: Optional[str] = None,
    interview: Optional[str] = None,
    test: Optional[str] = None,
    owner: Optional[str] = None,
    target_date: Optional[str] = None,
    remediation_plan: Optional[str] = None,
    estimated_cost: Optional[str] = None,
    likelihood: Optional[str] = None,
    impact: Optional[str] = None,
    maturity: Optional[str] = None,
    linked_policies: Optional[list] = None,
    linked_assets: Optional[list] = None,
    linked_team: Optional[list] = None,
    linked_subcontractors: Optional[list] = None,
    objectives: Optional[list] = None,
    override_active: Optional[bool] = None,
    override_justification: Optional[str] = None,
    fips_certificate_number: Optional[str] = None,
    cloud_authorization_status: Optional[str] = None,
    dfars_72hr_reporting_enabled: Optional[bool] = None,
    human_edited: Optional[bool] = None,
) -> Dict[str, Any]:
    if control_id not in CMMC_FRAMEWORK:
        raise ValueError(f"Unknown control: {control_id}")

    if status == "NOT APPLICABLE" and not (override_justification or "").strip():
        raise ValueError(
            "NOT APPLICABLE requires a written justification (override_justification) — "
            "unjustified N/A is scored as not met"
        )

    ws = deepcopy(state)
    ans = ws["answers"].setdefault(control_id, default_control_answer())
    role = ws.get("current_role", "Assessor")

    updates = {
        "status": status,
        "implementation_narrative": implementation_narrative,
        "assessor_notes": assessor_notes,
        "examine": examine,
        "interview": interview,
        "test": test,
        "owner": owner,
        "target_date": target_date,
        "remediation_plan": remediation_plan,
        "estimated_cost": estimated_cost,
        "likelihood": likelihood,
        "impact": impact,
        "maturity": maturity,
        "linked_policies": linked_policies,
        "linked_assets": linked_assets,
        "linked_team": linked_team,
        "linked_subcontractors": linked_subcontractors,
        "objectives": objectives,
        "override_active": override_active,
        "override_justification": override_justification,
        "fips_certificate_number": fips_certificate_number,
        "cloud_authorization_status": cloud_authorization_status,
        "dfars_72hr_reporting_enabled": dfars_72hr_reporting_enabled,
    }
    for field, new_val in updates.items():
        if new_val is None:
            continue
        old_val = ans.get(field)
        if new_val != old_val:
            log_change(ws["audit_log"], control_id, field, old_val, new_val, role)
            ans[field] = new_val

    if human_edited is not None:
        ans["human_edited"] = human_edited

    if status is not None:
        _maybe_sprs_snapshot(ws)

    save_workspace(ws)
    return ws


def _maybe_sprs_snapshot(ws: Dict[str, Any]) -> None:
    """Append SPRS history entry when score changes (platform trend chart)."""
    from sprs_engine import calculate_detailed_sprs

    detailed = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])
    today = datetime.now().strftime("%Y-%m-%d")
    history = list(ws.get("sprs_history") or [])
    if history:
        last = history[-1]
        if last.get("timestamp", "")[:10] == today and last.get("score") == detailed["final_score"]:
            return
    scoped = set(ws.get("scoped_controls") or [])
    answered = [
        cid for cid in scoped
        if (ws.get("answers") or {}).get(cid, {}).get("status") in ("MET", "NOT APPLICABLE", "INHERITED")
    ]
    total = len(scoped) or 1
    history.append(
        {
            "timestamp": datetime.now().isoformat(),
            "score": detailed["final_score"],
            "readiness": round(len(answered) * 100.0 / total, 1),
            "controls_met": len(answered),
            "controls_total": total,
            "critical_gaps": len(detailed.get("critical_gaps") or []),
            "total_gaps": detailed.get("breakdown", {}).get("total_gaps_count", 0),
        }
    )
    ws["sprs_history"] = history


def add_control_comment(
    state: Dict[str, Any],
    control_id: str,
    text: str,
    author: str,
) -> Dict[str, Any]:
    import uuid
    from datetime import datetime

    if control_id not in CMMC_FRAMEWORK:
        raise ValueError(f"Unknown control: {control_id}")

    body = (text or "").strip()
    if not body:
        raise ValueError("Comment cannot be empty")

    ws = deepcopy(state)
    ans = ws["answers"].setdefault(control_id, default_control_answer())
    comments = list(ans.get("comments") or [])
    comment = {
        "id": f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}",
        "author": (author or "Assessor").strip() or "Assessor",
        "text": body,
        "created_at": datetime.now().isoformat(),
    }
    comments.append(comment)
    ans["comments"] = comments
    save_workspace(ws)
    return ws


def attach_evidence(
    state: Dict[str, Any],
    control_id: str,
    *,
    filename: str,
    data: bytes,
    sha256: str,
    upload_date: str,
    provenance: Optional[Dict[str, Any]] = None,
    display_title: str = "",
    evidence_type: str = "",
    auto_status: str = "",
    review_status: str = "",
) -> Dict[str, Any]:
    if control_id not in CMMC_FRAMEWORK:
        raise ValueError(f"Unknown control: {control_id}")

    ws = deepcopy(state)
    ans = ws["answers"].setdefault(control_id, default_control_answer())
    from security_utils import safe_evidence_filename

    safe_name = safe_evidence_filename(filename)
    evs = list(ans.get("evidence") or [])
    evs = [e for e in evs if e.get("filename") != safe_name]
    entry: Dict[str, Any] = {
        "filename": safe_name,
        "upload_date": upload_date,
        "sha256": sha256,
        "data_bytes": data,
    }
    if provenance:
        entry["provenance"] = provenance
    if display_title:
        entry["display_title"] = display_title
    if evidence_type:
        entry["evidence_type"] = evidence_type
    if auto_status:
        entry["auto_status"] = auto_status
    if review_status:
        entry["review_status"] = review_status
    evs.append(entry)
    ans["evidence"] = evs
    restored = dict(ws.get("restored_evidence") or {})
    from evidence_store import evidence_file_key

    restored[evidence_file_key(control_id, safe_name)] = data
    ws["restored_evidence"] = restored
    save_workspace(ws)
    return ws


def detach_evidence(
    state: Dict[str, Any],
    control_id: str,
    *,
    filename: str,
) -> Dict[str, Any]:
    if control_id not in CMMC_FRAMEWORK:
        raise ValueError(f"Unknown control: {control_id}")

    from security_utils import safe_evidence_filename
    from evidence_store import evidence_file_key

    safe_name = safe_evidence_filename(filename)
    ws = deepcopy(state)
    ans = ws["answers"].get(control_id)
    if not ans:
        raise ValueError("Evidence file not found")

    evs = list(ans.get("evidence") or [])
    if not any(e.get("filename") == safe_name for e in evs):
        raise ValueError("Evidence file not found")

    ans["evidence"] = [e for e in evs if e.get("filename") != safe_name]
    restored = dict(ws.get("restored_evidence") or {})
    restored.pop(evidence_file_key(control_id, safe_name), None)
    ws["restored_evidence"] = restored
    save_workspace(ws)
    return ws


def list_workspace_clients() -> List[Dict[str, str]]:
    ensure_default_client()
    return list_clients()


def activate_client(client_id: str) -> None:
    set_active_client_id(client_id)
