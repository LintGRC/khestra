"""SOC 2 workspace persistence."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app_config import APP_VERSION, STATUS_OPTIONS
from client_workspaces import (
    active_client_id,
    client_evidence_dir,
    client_session_path,
    ensure_default_client,
)
from evidence_store import answers_without_evidence_bytes, load_evidence_from_disk, persist_evidence_to_disk
from org_profile import merge_org_profile, profile_needs_wizard, WIZARD_STEPS, FIELD_LABELS, FIELD_PLACEHOLDERS
from env_scope import merge_env_scope, env_scope_complete, format_env_scope_summary, scoping_suggestions
from org_inventory import merge_org_inventory
from soc2_catalog import SOC2_CONTROLS
from tsc_scoping import DEFAULT_SCOPE, get_in_scope_controls, get_in_scope_criteria_ids, is_in_scope


def default_control_answer() -> Dict[str, Any]:
    return {
        "status": "NOT STARTED",
        "implementation_narrative": "",
        "assessor_notes": "",
        "owner": "",
        "target_date": "",
        "remediation_plan": "",
        "operating_status": "NOT TESTED",
        "frequency": "",
        "last_review_date": "",
        "next_review_date": "",
        "evidence": [],
        "comments": [],
        "reviews": [],
        "linked_policies": [],
        "linked_assets": [],
        "linked_team": [],
        "points_of_focus": {},
    }


def default_pof_entry() -> Dict[str, Any]:
    return {
        "status": "not_applicable",
        "justification": "",
    }


def _evidence_path(client_id: str) -> Path:
    return client_evidence_dir(client_id)


def _empty_workspace(client_id: str) -> Dict[str, Any]:
    return {
        "client_id": client_id,
        "version": APP_VERSION,
        "org_name": "Your Organization",
        "org_profile": {},
        "env_scope": {},
        "org_inventory": {},
        "tsc_scope": dict(DEFAULT_SCOPE),
        "scoping_completed": False,
        "answers": {cid: default_control_answer() for cid in SOC2_CONTROLS},
        "audit_log": [],
        "audit_periods": [],
        "soc2_engagement": {},
        "evidence_requests": [],
        "exceptions": [],
        "risks": [],
        "policies": [],
        "policy_attestations": [],
        "findings": [],
        "current_role": "Assessor",
        "current_user_name": "",
        "is_demo": False,
        "demo_id": None,
        "restored_evidence": {},
    }


def workspace_is_locked(ws: Dict[str, Any]) -> bool:
    """True when any audit period is frozen — workspace edits are blocked."""
    return any(p.get("frozen") for p in (ws.get("audit_periods") or []))


class WorkspaceLockedError(Exception):
    """Raised when mutating a frozen workspace."""


def require_workspace_editable(ws: Dict[str, Any]) -> None:
    if workspace_is_locked(ws):
        raise WorkspaceLockedError("Workspace is locked while an audit period is frozen")


def load_workspace(client_id: Optional[str] = None, *, load_evidence_bytes: bool = False) -> Dict[str, Any]:
    cid = client_id or active_client_id()
    path = client_session_path(cid)
    if not path.exists():
        return _empty_workspace(cid)

    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print(f"WARNING: Corrupt workspace file {path}, resetting to empty workspace", file=sys.stderr)
        return _empty_workspace(cid)

    answers = loaded.get("answers") or {}
    for cid_key in SOC2_CONTROLS:
        answers.setdefault(cid_key, default_control_answer())

    return {
        "client_id": cid,
        "version": loaded.get("version", APP_VERSION),
        "org_name": loaded.get("org_name", "Your Organization"),
        "org_profile": loaded.get("org_profile") or {},
        "env_scope": loaded.get("env_scope") or {},
        "org_inventory": loaded.get("org_inventory") or {},
        "tsc_scope": loaded.get("tsc_scope") or dict(DEFAULT_SCOPE),
        "scoping_completed": loaded.get("scoping_completed", False),
        "answers": answers,
        "audit_log": loaded.get("audit_log", []),
        "audit_periods": loaded.get("audit_periods") or [],
        "soc2_engagement": loaded.get("soc2_engagement") or {},
        "evidence_requests": loaded.get("evidence_requests") or [],
        "exceptions": loaded.get("exceptions") or [],
        "risks": loaded.get("risks") or [],
        "policies": loaded.get("policies") or [],
        "policy_attestations": loaded.get("policy_attestations") or [],
        "findings": loaded.get("findings") or [],
        "current_role": loaded.get("current_role", "Assessor"),
        "current_user_name": loaded.get("current_user_name", ""),
        "is_demo": bool(loaded.get("is_demo")),
        "demo_id": loaded.get("demo_id"),
        "restored_evidence": load_evidence_from_disk(_evidence_path(cid))
        if load_evidence_bytes
        else {},
    }


def save_workspace(state: Dict[str, Any]) -> None:
    cid = state.get("client_id") or active_client_id()
    if not state.get("restored_evidence"):
        state = {**state, "restored_evidence": load_evidence_from_disk(_evidence_path(cid))}
    all_entries = []
    for ans in state.get("answers", {}).values():
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
        "org_profile": state.get("org_profile") or {},
        "env_scope": state.get("env_scope") or {},
        "org_inventory": state.get("org_inventory") or {},
        "tsc_scope": state.get("tsc_scope") or dict(DEFAULT_SCOPE),
        "scoping_completed": state.get("scoping_completed", False),
        "answers": answers_without_evidence_bytes(state["answers"]),
        "audit_log": state.get("audit_log", []),
        "audit_periods": state.get("audit_periods") or [],
        "soc2_engagement": state.get("soc2_engagement") or {},
        "evidence_requests": state.get("evidence_requests") or [],
        "exceptions": state.get("exceptions") or [],
        "risks": state.get("risks") or [],
        "policies": state.get("policies") or [],
        "policy_attestations": state.get("policy_attestations") or [],
        "findings": state.get("findings") or [],
        "current_role": state.get("current_role", "Assessor"),
        "current_user_name": state.get("current_user_name", ""),
        "is_demo": bool(state.get("is_demo")),
        "demo_id": state.get("demo_id"),
    }
    path = client_session_path(cid)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def attach_evidence(
    state: Dict[str, Any],
    control_id: str,
    *,
    filename: str,
    data: bytes,
    sha256: str,
    upload_date: str,
    valid_from: Optional[str] = None,
    valid_to: Optional[str] = None,
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise ValueError(f"Unknown control: {control_id}")
    scope = state.get("tsc_scope") or DEFAULT_SCOPE
    if not is_in_scope(control_id, scope):
        raise ValueError(f"Control {control_id} is not in scope")
    require_workspace_editable(state)
    ws = deepcopy(state)
    ans = ws["answers"].setdefault(control_id, default_control_answer())
    evs = list(ans.get("evidence") or [])
    evs = [e for e in evs if e.get("filename") != filename]
    entry = {
        "filename": filename,
        "upload_date": upload_date,
        "sha256": sha256,
        "data_bytes": data,
        "source": "manual",
        "review_status": "pending",
    }
    if valid_from:
        entry["valid_from"] = valid_from
    if valid_to:
        entry["valid_to"] = valid_to
    evs.append(entry)
    ans["evidence"] = evs
    return ws


def patch_control(
    state: Dict[str, Any],
    control_id: str,
    *,
    status: Optional[str] = None,
    implementation_narrative: Optional[str] = None,
    assessor_notes: Optional[str] = None,
    owner: Optional[str] = None,
    target_date: Optional[str] = None,
    remediation_plan: Optional[str] = None,
    operating_status: Optional[str] = None,
    frequency: Optional[str] = None,
    last_review_date: Optional[str] = None,
    next_review_date: Optional[str] = None,
    linked_policies: Optional[List[Dict[str, Any]]] = None,
    linked_assets: Optional[List[Dict[str, Any]]] = None,
    linked_team: Optional[List[str]] = None,
    points_of_focus: Optional[Dict[str, Dict[str, str]]] = None,
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise ValueError(f"Unknown control: {control_id}")
    scope = state.get("tsc_scope") or DEFAULT_SCOPE
    if not is_in_scope(control_id, scope):
        raise ValueError(f"Control {control_id} is not in scope")

    require_workspace_editable(state)

    ws = deepcopy(state)
    ans = ws["answers"].setdefault(control_id, default_control_answer())
    updates = {
        "status": status,
        "implementation_narrative": implementation_narrative,
        "assessor_notes": assessor_notes,
        "owner": owner,
        "target_date": target_date,
        "remediation_plan": remediation_plan,
        "operating_status": operating_status,
        "frequency": frequency,
        "last_review_date": last_review_date,
        "next_review_date": next_review_date,
        "linked_policies": linked_policies,
        "linked_assets": linked_assets,
        "linked_team": linked_team,
        "points_of_focus": points_of_focus,
    }
    for field, new_val in updates.items():
        if new_val is not None:
            if field == "status" and new_val != ans.get("status"):
                ans["status_changed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            if field == "operating_status" and new_val != ans.get("operating_status"):
                ans["operating_status_changed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            ans[field] = new_val
    save_workspace(ws)
    return ws


def patch_pof(
    state: Dict[str, Any],
    control_id: str,
    pof_id: str,
    *,
    status: str,
    justification: str = "",
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise ValueError(f"Unknown control: {control_id}")
    scope = state.get("tsc_scope") or DEFAULT_SCOPE
    if not is_in_scope(control_id, scope):
        raise ValueError(f"Control {control_id} is not in scope")
    catalog_pofs = SOC2_CONTROLS[control_id].get("points_of_focus", [])
    if not any(p["id"] == pof_id for p in catalog_pofs):
        raise ValueError(f"Unknown Point of Focus: {pof_id}")
    if status not in ("not_applicable", "addressed"):
        raise ValueError(f"Invalid PoF status: {status}")

    require_workspace_editable(state)
    ws = deepcopy(state)
    ans = ws["answers"].setdefault(control_id, default_control_answer())
    pofs = dict(ans.get("points_of_focus") or {})
    pofs[pof_id] = {"status": status, "justification": justification}
    ans["points_of_focus"] = pofs
    save_workspace(ws)
    return ws


def bulk_patch_pofs(
    state: Dict[str, Any],
    control_id: str,
    pof_updates: Dict[str, Dict[str, str]],
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise ValueError(f"Unknown control: {control_id}")
    scope = state.get("tsc_scope") or DEFAULT_SCOPE
    if not is_in_scope(control_id, scope):
        raise ValueError(f"Control {control_id} is not in scope")

    require_workspace_editable(state)
    ws = deepcopy(state)
    ans = ws["answers"].setdefault(control_id, default_control_answer())
    pofs = dict(ans.get("points_of_focus") or {})
    for pof_id, update in pof_updates.items():
        pofs[pof_id] = update
    ans["points_of_focus"] = pofs
    save_workspace(ws)
    return ws


def detach_evidence(state: Dict[str, Any], control_id: str, *, filename: str) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise ValueError(f"Unknown control: {control_id}")
    scope = state.get("tsc_scope") or DEFAULT_SCOPE
    if not is_in_scope(control_id, scope):
        raise ValueError(f"Control {control_id} is not in scope")
    require_workspace_editable(state)
    ws = deepcopy(state)
    ans = ws["answers"].get(control_id)
    if not ans:
        raise ValueError("Evidence not found")
    evs = list(ans.get("evidence") or [])
    kept = [e for e in evs if e.get("filename") != filename]
    if len(kept) == len(evs):
        raise ValueError("Evidence not found")
    ans["evidence"] = kept
    save_workspace(ws)
    return ws


def pof_coverage_stats(ans: Dict[str, Any], cid: str) -> Dict[str, Any]:
    catalog_pofs = SOC2_CONTROLS.get(cid, {}).get("points_of_focus", [])
    total = len(catalog_pofs)
    if total == 0:
        return {"pof_total": 0, "pof_addressed": 0, "pof_not_applicable": 0, "pof_coverage_pct": 0}
    user_pofs = ans.get("points_of_focus") or {}
    addressed = sum(1 for p in catalog_pofs if user_pofs.get(p["id"], {}).get("status") == "addressed")
    not_applicable = sum(1 for p in catalog_pofs if user_pofs.get(p["id"], {}).get("status") == "not_applicable")
    applicable = total - not_applicable
    coverage_pct = round((addressed / applicable) * 100) if applicable > 0 else 100
    return {
        "pof_total": total,
        "pof_addressed": addressed,
        "pof_not_applicable": not_applicable,
        "pof_coverage_pct": coverage_pct,
    }


def list_control_summaries(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    rows: List[Dict[str, Any]] = []
    for cid, meta in get_in_scope_controls(scope).items():
        ans = ws["answers"].get(cid, default_control_answer())
        status = ans.get("status", "NOT STARTED")
        narrative = (ans.get("implementation_narrative") or "").strip()
        evidence = ans.get("evidence") or []
        has_auto = any(e.get("filename", "").startswith("collector_") for e in evidence)
        pof = pof_coverage_stats(ans, cid)
        rows.append(
            {
                "id": cid,
                "code": cid,
                "category": meta["category"],
                "name": meta["title"],
                "description": meta["description"],
                "status": status,
                "has_narrative": bool(narrative),
                "evidence_count": len(evidence),
                "auto_evidence_count": sum(1 for e in evidence if e.get("filename", "").startswith("collector_")),
                "last_evidence_date": max((e.get("upload_date") or "") for e in evidence) if evidence else None,
                "has_auto_evidence": has_auto,
                "owner": ans.get("owner") or "",
                "target_date": ans.get("target_date") or "",
                "operating_status": ans.get("operating_status", "NOT TESTED"),
                **pof,
            }
        )
    return rows


def list_all_evidence(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    items: List[Dict[str, Any]] = []
    for cid in get_in_scope_criteria_ids(scope):
        ans = ws["answers"].get(cid, default_control_answer())
        for ev in ans.get("evidence") or []:
            item = {
                "id": str(uuid.uuid4()),
                "control_id": cid,
                "filename": ev.get("filename", ""),
                "upload_date": ev.get("upload_date", ""),
                "sha256": ev.get("sha256", ""),
                "is_auto": ev.get("filename", "").startswith("collector_"),
                "source": ev.get("source", "manual"),
                "review_status": ev.get("review_status", "pending"),
                "valid_from": ev.get("valid_from"),
                "valid_to": ev.get("valid_to"),
            }
            items.append(item)
    items.sort(key=lambda x: x["upload_date"], reverse=True)
    return items


def attach_evidence_multi(
    state: Dict[str, Any],
    control_ids: List[str],
    *,
    filename: str,
    data: bytes,
    sha256: Optional[str] = None,
    upload_date: Optional[str] = None,
    source: str = "manual",
    valid_from: Optional[str] = None,
    valid_to: Optional[str] = None,
) -> Dict[str, Any]:
    require_workspace_editable(state)
    ws = deepcopy(state)
    stamp = upload_date or datetime.now().strftime("%Y-%m-%d %H:%M")
    digest = sha256 or hashlib.sha256(data).hexdigest()
    for cid in control_ids:
        if cid not in SOC2_CONTROLS:
            continue
        ans = ws["answers"].setdefault(cid, default_control_answer())
        evs = [e for e in (ans.get("evidence") or []) if e.get("filename") != filename]
        entry = {
            "filename": filename,
            "upload_date": stamp,
            "sha256": digest,
            "data_bytes": data,
            "source": source,
            "review_status": "pending",
        }
        if valid_from:
            entry["valid_from"] = valid_from
        if valid_to:
            entry["valid_to"] = valid_to
        evs.append(entry)
        ans["evidence"] = evs
    return ws


def review_evidence(
    state: Dict[str, Any],
    control_id: str,
    filename: str,
    *,
    reviewer: str,
    status: str,
    comment: str = "",
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise ValueError(f"Unknown control: {control_id}")
    scope = state.get("tsc_scope") or DEFAULT_SCOPE
    if not is_in_scope(control_id, scope):
        raise ValueError(f"Control {control_id} is not in scope")
    require_workspace_editable(state)
    ws = deepcopy(state)
    ans = ws["answers"].setdefault(control_id, default_control_answer())
    evs = list(ans.get("evidence") or [])
    for ev in evs:
        if ev.get("filename") == filename:
            ev["review_status"] = status
            ev["reviewer"] = reviewer
            ev["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            ev["review_comment"] = comment
    ans["evidence"] = evs
    return ws


def list_audit_periods(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    return ws.get("audit_periods") or []


def create_audit_period(
    ws: Dict[str, Any],
    *,
    name: str,
    start_date: str,
    end_date: str,
) -> Dict[str, Any]:
    period = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "start_date": start_date,
        "end_date": end_date,
        "frozen": False,
        "frozen_at": None,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }
    periods = list(ws.get("audit_periods") or [])
    periods.append(period)
    ws["audit_periods"] = periods
    save_workspace(ws)
    return period


def freeze_audit_period(ws: Dict[str, Any], period_id: str) -> Optional[Dict[str, Any]]:
    periods = list(ws.get("audit_periods") or [])
    for p in periods:
        if p["id"] == period_id:
            p["frozen"] = True
            p["frozen_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            ws["audit_periods"] = periods
            save_workspace(ws)
            return p
    return None


def generate_manifest(ws: Dict[str, Any]) -> Dict[str, Any]:
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    items: List[Dict[str, Any]] = []
    for cid in get_in_scope_criteria_ids(scope):
        ans = ws["answers"].get(cid, default_control_answer())
        for ev in ans.get("evidence") or []:
            items.append({
                "control_id": cid,
                "filename": ev.get("filename", ""),
                "sha256": ev.get("sha256", ""),
                "upload_date": ev.get("upload_date", ""),
                "review_status": ev.get("review_status", "pending"),
                "valid_from": ev.get("valid_from"),
                "valid_to": ev.get("valid_to"),
            })
    manifest_digest = hashlib.sha256(
        json.dumps(items, sort_keys=True).encode()
    ).hexdigest()
    return {
        "generated_at": datetime.now().isoformat(),
        "total_evidence": len(items),
        "controls_covered": len({i["control_id"] for i in items}),
        "manifest_hash": manifest_digest,
        "items": items,
    }


def evidence_coverage_for_period(ws: Dict[str, Any], period: Dict[str, Any]) -> Dict[str, Any]:
    """Returns per-control coverage analysis for a given audit period.
    Evidence is in-scope if valid_from <= period_end AND (valid_to IS NULL OR valid_to >= period_start).
    """
    start = period["start_date"]
    end = period["end_date"]
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    in_scope = get_in_scope_controls(scope)
    total = len(in_scope)
    covered = 0
    per_control: Dict[str, Any] = {}
    for cid in in_scope:
        ans = ws["answers"].get(cid, default_control_answer())
        in_scope = []
        for ev in ans.get("evidence") or []:
            vf = ev.get("valid_from") or ev.get("upload_date", "").split(" ")[0]
            vt = ev.get("valid_to")
            if vf <= end and (vt is None or vt >= start):
                in_scope.append(ev)
        per_control[cid] = {
            "evidence_count": len(in_scope),
            "has_evidence": len(in_scope) > 0,
            "valid_from_range": min((e.get("valid_from") or e.get("upload_date", "").split(" ")[0]) for e in in_scope) if in_scope else None,
            "valid_to_range": max((e.get("valid_to") or "") for e in in_scope) if in_scope else None,
        }
        if per_control[cid]["has_evidence"]:
            covered += 1
    return {
        "period_id": period["id"],
        "period_name": period["name"],
        "start_date": start,
        "end_date": end,
        "total_controls": total,
        "controls_covered": covered,
        "coverage_pct": round((covered / total) * 100) if total else 0,
        "per_control": per_control,
    }


def list_evidence_requests(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    return ws.get("evidence_requests") or []


def create_evidence_request(
    ws: Dict[str, Any],
    *,
    control_id: str,
    title: str,
    assigned_to: str = "",
    due_date: str = "",
    description: str = "",
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise ValueError(f"Unknown control: {control_id}")
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    if not is_in_scope(control_id, scope):
        raise ValueError(f"Control {control_id} is not in scope")
    require_workspace_editable(ws)
    req = {
        "id": str(uuid.uuid4())[:8],
        "control_id": control_id,
        "title": title,
        "description": description,
        "assigned_to": assigned_to,
        "due_date": due_date,
        "status": "open",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }
    reqs = list(ws.get("evidence_requests") or [])
    reqs.append(req)
    ws["evidence_requests"] = reqs
    save_workspace(ws)
    return req


def patch_evidence_request(
    ws: Dict[str, Any],
    request_id: str,
    *,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    require_workspace_editable(ws)
    reqs = list(ws.get("evidence_requests") or [])
    for r in reqs:
        if r["id"] == request_id:
            if status is not None:
                r["status"] = status
            if assigned_to is not None:
                r["assigned_to"] = assigned_to
            if due_date is not None:
                r["due_date"] = due_date
            ws["evidence_requests"] = reqs
            save_workspace(ws)
            return r
    return None


# ── Exception / POA&M management ────────────────────────────

def default_exception() -> Dict[str, Any]:
    return {
        "id": "",
        "control_id": "",
        "status": "pending_approval",
        "risk_level": "medium",
        "description": "",
        "compensating_controls": "",
        "risk_acceptance": "",
        "created_by": "",
        "approved_by": "",
        "expiry_date": "",
        "created_at": "",
        "updated_at": "",
        "approved_at": "",
    }


def list_exceptions(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    return ws.get("exceptions") or []


def get_exception(ws: Dict[str, Any], exception_id: str) -> Optional[Dict[str, Any]]:
    for exc in ws.get("exceptions") or []:
        if exc["id"] == exception_id:
            return exc
    return None


def create_exception(ws: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    require_workspace_editable(ws)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exc = default_exception()
    exc["id"] = uuid.uuid4().hex[:12]
    exc["control_id"] = data.get("control_id", "")
    exc["status"] = data.get("status", "pending_approval")
    exc["risk_level"] = data.get("risk_level", "medium")
    exc["description"] = data.get("description", "")
    exc["compensating_controls"] = data.get("compensating_controls", "")
    exc["risk_acceptance"] = data.get("risk_acceptance", "")
    exc["created_by"] = data.get("created_by", ws.get("current_user_name", ""))
    exc["approved_by"] = ""
    exc["expiry_date"] = data.get("expiry_date", "")
    exc["created_at"] = now
    exc["updated_at"] = now
    exc["approved_at"] = ""
    ws.setdefault("exceptions", []).append(exc)
    ws.setdefault("audit_log", []).append({
        "timestamp": now,
        "event": "exception_created",
        "exception_id": exc["id"],
        "control_id": exc["control_id"],
        "user": ws.get("current_user_name", ""),
    })
    save_workspace(ws)
    return exc


def update_exception(ws: Dict[str, Any], exception_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    require_workspace_editable(ws)
    excs = ws.get("exceptions") or []
    for exc in excs:
        if exc["id"] == exception_id:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for field in ("status", "risk_level", "description", "compensating_controls",
                          "risk_acceptance", "expiry_date", "approved_by"):
                if field in data:
                    exc[field] = data[field]
            if exc["status"] == "approved" and not exc.get("approved_at"):
                exc["approved_at"] = now
                exc["approved_by"] = data.get("approved_by", ws.get("current_user_name", ""))
            exc["updated_at"] = now
            ws.setdefault("audit_log", []).append({
                "timestamp": now,
                "event": "exception_updated",
                "exception_id": exc["id"],
                "control_id": exc["control_id"],
                "status": exc["status"],
                "user": ws.get("current_user_name", ""),
            })
            save_workspace(ws)
            return exc
    return None


def delete_exception(ws: Dict[str, Any], exception_id: str) -> bool:
    require_workspace_editable(ws)
    excs = ws.get("exceptions") or []
    for i, exc in enumerate(excs):
        if exc["id"] == exception_id:
            excs.pop(i)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws.setdefault("audit_log", []).append({
                "timestamp": now,
                "event": "exception_deleted",
                "exception_id": exception_id,
                "control_id": exc.get("control_id", ""),
                "user": ws.get("current_user_name", ""),
            })
            save_workspace(ws)
            return True
    return False


# ── Risk Register ────────────────────────────────────────────

def _calc_risk_score(likelihood: str, impact: str) -> int:
    score: dict = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    return score.get(likelihood, 1) * score.get(impact, 1)


def _risk_level(score: int) -> str:
    if score >= 12: return "critical"
    if score >= 6: return "high"
    if score >= 3: return "medium"
    return "low"


def default_risk() -> Dict[str, Any]:
    return {
        "id": "",
        "control_id": "",
        "title": "",
        "description": "",
        "category": "operational",
        "inherent_likelihood": "medium",
        "inherent_impact": "medium",
        "residual_likelihood": "low",
        "residual_impact": "low",
        "treatment": "mitigate",
        "controls": "",
        "owner": "",
        "status": "identified",
        "inherent_score": 0,
        "residual_score": 0,
        "inherent_level": "",
        "residual_level": "",
        "review_date": "",
        "created_at": "",
        "updated_at": "",
        "closed_at": "",
    }


def list_risks(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    return ws.get("risks") or []


def create_risk(ws: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    require_workspace_editable(ws)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risk = default_risk()
    risk["id"] = uuid.uuid4().hex[:12]
    risk["control_id"] = data.get("control_id", "")
    risk["title"] = data.get("title", "")
    risk["description"] = data.get("description", "")
    risk["category"] = data.get("category", "operational")
    risk["inherent_likelihood"] = data.get("inherent_likelihood", "medium")
    risk["inherent_impact"] = data.get("inherent_impact", "medium")
    risk["residual_likelihood"] = data.get("residual_likelihood", "low")
    risk["residual_impact"] = data.get("residual_impact", "low")
    risk["treatment"] = data.get("treatment", "mitigate")
    risk["controls"] = data.get("controls", "")
    risk["owner"] = data.get("owner", ws.get("current_user_name", ""))
    risk["status"] = data.get("status", "identified")
    risk["review_date"] = data.get("review_date", "")
    risk["created_at"] = now
    risk["updated_at"] = now
    risk["inherent_score"] = _calc_risk_score(risk["inherent_likelihood"], risk["inherent_impact"])
    risk["residual_score"] = _calc_risk_score(risk["residual_likelihood"], risk["residual_impact"])
    risk["inherent_level"] = _risk_level(risk["inherent_score"])
    risk["residual_level"] = _risk_level(risk["residual_score"])
    ws.setdefault("risks", []).append(risk)
    ws.setdefault("audit_log", []).append({
        "timestamp": now, "event": "risk_created", "risk_id": risk["id"],
        "title": risk["title"], "user": ws.get("current_user_name", ""),
    })
    save_workspace(ws)
    return risk


def update_risk(ws: Dict[str, Any], risk_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    require_workspace_editable(ws)
    for risk in ws.get("risks") or []:
        if risk["id"] == risk_id:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for field in ("title", "description", "category", "inherent_likelihood",
                          "inherent_impact", "residual_likelihood", "residual_impact",
                          "treatment", "controls", "owner", "status", "review_date"):
                if field in data:
                    risk[field] = data[field]
            risk["inherent_score"] = _calc_risk_score(risk["inherent_likelihood"], risk["inherent_impact"])
            risk["residual_score"] = _calc_risk_score(risk["residual_likelihood"], risk["residual_impact"])
            risk["inherent_level"] = _risk_level(risk["inherent_score"])
            risk["residual_level"] = _risk_level(risk["residual_score"])
            if risk["status"] == "closed" and not risk.get("closed_at"):
                risk["closed_at"] = now
            risk["updated_at"] = now
            ws.setdefault("audit_log", []).append({
                "timestamp": now, "event": "risk_updated", "risk_id": risk["id"],
                "title": risk["title"], "user": ws.get("current_user_name", ""),
            })
            save_workspace(ws)
            return risk
    return None


def delete_risk(ws: Dict[str, Any], risk_id: str) -> bool:
    require_workspace_editable(ws)
    risks = ws.get("risks") or []
    for i, risk in enumerate(risks):
        if risk["id"] == risk_id:
            risks.pop(i)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws.setdefault("audit_log", []).append({
                "timestamp": now, "event": "risk_deleted", "risk_id": risk_id,
                "user": ws.get("current_user_name", ""),
            })
            save_workspace(ws)
            return True
    return False


# ── Policy Management ─────────────────────────────────────────

def list_policies(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    return ws.get("policies") or []


def create_policy(ws: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    require_workspace_editable(ws)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    policy = {
        "id": uuid.uuid4().hex[:12],
        "name": data.get("name", ""),
        "version": data.get("version", "1.0"),
        "description": data.get("description", ""),
        "content": data.get("content", ""),
        "filename": data.get("filename", ""),
        "file_uploaded": bool(data.get("filename")),
        "mapped_controls": data.get("mapped_controls", []),
        "created_at": now,
        "updated_at": now,
    }
    ws.setdefault("policies", []).append(policy)
    ws.setdefault("audit_log", []).append({
        "timestamp": now, "event": "policy_created", "policy_id": policy["id"],
        "name": policy["name"], "user": ws.get("current_user_name", ""),
    })
    save_workspace(ws)
    return policy


def update_policy(ws: Dict[str, Any], policy_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    require_workspace_editable(ws)
    for policy in ws.get("policies") or []:
        if policy["id"] == policy_id:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for field in ("name", "version", "description", "content", "filename", "file_uploaded", "mapped_controls"):
                if field in data:
                    policy[field] = data[field]
            policy["updated_at"] = now
            save_workspace(ws)
            return policy
    return None


def delete_policy(ws: Dict[str, Any], policy_id: str) -> bool:
    require_workspace_editable(ws)
    policies = ws.get("policies") or []
    for i, p in enumerate(policies):
        if p["id"] == policy_id:
            policies.pop(i)
            ws["policy_attestations"] = [a for a in (ws.get("policy_attestations") or []) if a.get("policy_id") != policy_id]
            save_workspace(ws)
            return True
    return False


# ── Policy Attestations ──────────────────────────────────────

def list_attestations(ws: Dict[str, Any], policy_id: Optional[str] = None) -> List[Dict[str, Any]]:
    atts = ws.get("policy_attestations") or []
    if policy_id:
        return [a for a in atts if a.get("policy_id") == policy_id]
    return atts


def create_attestation(ws: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    require_workspace_editable(ws)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    att = {
        "id": uuid.uuid4().hex[:12],
        "policy_id": data.get("policy_id", ""),
        "user_name": data.get("user_name", ws.get("current_user_name", "")),
        "date": now,
        "acknowledged": True,
    }
    ws.setdefault("policy_attestations", []).append(att)
    save_workspace(ws)
    return att


def policy_coverage(ws: Dict[str, Any]) -> Dict[str, Any]:
    """Return per-criterion policy coverage counts."""
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    policies = ws.get("policies") or []
    coverage: Dict[str, int] = {}
    for p in policies:
        for cid in p.get("mapped_controls") or []:
            coverage[cid] = coverage.get(cid, 0) + 1
    total_with_policies = len(coverage)
    in_scope = get_in_scope_controls(scope)
    return {
        "policies_total": len(policies),
        "controls_with_policy": total_with_policies,
        "controls_total": len(in_scope),
        "coverage_pct": round((total_with_policies / len(in_scope)) * 100) if len(in_scope) else 0,
        "by_control": coverage,
    }


# ── Audit Findings ────────────────────────────────────────────

def list_findings(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    return ws.get("findings") or []


def create_finding(ws: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    finding = {
        "id": uuid.uuid4().hex[:12],
        "control_id": data.get("control_id", ""),
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "severity": data.get("severity", "observation"),
        "status": data.get("status", "open"),
        "auditor_name": data.get("auditor_name", ws.get("current_user_name", "")),
        "created_at": now,
        "updated_at": now,
        "remediation_plan": data.get("remediation_plan", ""),
        "remediation_deadline": data.get("remediation_deadline", ""),
        "closed_at": "",
    }
    ws.setdefault("findings", []).append(finding)
    save_workspace(ws)
    return finding


def update_finding(ws: Dict[str, Any], finding_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for f in ws.get("findings") or []:
        if f["id"] == finding_id:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for field in ("title", "description", "severity", "status", "auditor_name",
                          "remediation_plan", "remediation_deadline"):
                if field in data:
                    f[field] = data[field]
            if data.get("status") == "closed" and not f.get("closed_at"):
                f["closed_at"] = now
            f["updated_at"] = now
            save_workspace(ws)
            return f
    return None


def delete_finding(ws: Dict[str, Any], finding_id: str) -> bool:
    findings = ws.get("findings") or []
    for i, f in enumerate(findings):
        if f["id"] == finding_id:
            findings.pop(i)
            save_workspace(ws)
            return True
    return False


def get_recent_activity(ws: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    events: List[Dict[str, Any]] = []
    for cid in get_in_scope_criteria_ids(scope):
        ans = ws["answers"].get(cid, default_control_answer())
        for ev in ans.get("evidence") or []:
            events.append({
                "type": "evidence_uploaded",
                "control_id": cid,
                "filename": ev.get("filename", ""),
                "timestamp": ev.get("upload_date", ""),
                "is_auto": ev.get("filename", "").startswith("collector_"),
            })
        if ans.get("status") and ans["status"] not in ("NOT STARTED",):
            events.append({
                "type": "status_change",
                "control_id": cid,
                "status": ans["status"],
                "timestamp": ans.get("status_changed_at", ""),
            })
    for req in ws.get("evidence_requests") or []:
        events.append({
            "type": "request_created",
            "request_id": req["id"],
            "control_id": req["control_id"],
            "title": req["title"],
            "timestamp": req.get("created_at", ""),
        })
    for exc in ws.get("exceptions") or []:
        events.append({
            "type": f"exception_{exc.get('status', 'unknown')}",
            "exception_id": exc["id"],
            "control_id": exc.get("control_id", ""),
            "description": exc.get("description", ""),
            "timestamp": exc.get("updated_at", exc.get("created_at", "")),
        })
    for risk in ws.get("risks") or []:
        events.append({
            "type": "risk_created",
            "risk_id": risk["id"],
            "title": risk.get("title", ""),
            "level": risk.get("residual_level", ""),
            "timestamp": risk.get("updated_at", risk.get("created_at", "")),
        })
    events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return events[:limit]
