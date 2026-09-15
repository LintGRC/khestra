"""Bulk org-aware narrative prefill and export-time starter resolution."""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Literal, Optional

from assessment_nav_api import priority_controls
from controls import CMMC_FRAMEWORK
from guidance import starter_narrative

PrefillScope = Literal["priority", "missing_met", "all_empty"]

_MET_OR_NA = frozenset({"MET", "NOT APPLICABLE", "INHERITED"})


def has_implementation_narrative(ans: Dict[str, Any]) -> bool:
    return bool((ans.get("implementation_narrative") or "").strip())


def starter_text_for_control(
    control_id: str,
    org_profile: Dict[str, str],
    env_scope: Dict[str, str],
    scoped_controls: List[str],
) -> str:
    return starter_narrative(
        control_id,
        org_profile=org_profile,
        env_scope=env_scope,
        scoped_controls=scoped_controls,
    )


def _controls_for_scope(
    scope: PrefillScope,
    answers: Dict[str, Any],
    scoped_controls: List[str],
    priority_limit: int = 12,
) -> List[str]:
    scoped = [c for c in scoped_controls if c in CMMC_FRAMEWORK]
    if scope == "priority":
        return [c for c in priority_controls(answers, scoped, limit=priority_limit) if c in scoped]
    if scope == "missing_met":
        out: List[str] = []
        for cid in scoped:
            status = answers.get(cid, {}).get("status", "NOT STARTED")
            if status in _MET_OR_NA and not has_implementation_narrative(answers.get(cid, {})):
                out.append(cid)
        return out
    # all_empty
    return [cid for cid in scoped if not has_implementation_narrative(answers.get(cid, {}))]


def prefill_preview(
    scope: PrefillScope,
    answers: Dict[str, Any],
    scoped_controls: List[str],
    org_profile: Dict[str, str],
    env_scope: Dict[str, str],
    *,
    only_empty: bool = True,
    priority_limit: int = 12,
) -> Dict[str, Any]:
    candidates = _controls_for_scope(scope, answers, scoped_controls, priority_limit)
    items: List[Dict[str, Any]] = []
    apply_ids: List[str] = []
    for cid in candidates:
        ans = answers.get(cid, {})
        empty = not has_implementation_narrative(ans)
        if only_empty and not empty:
            continue
        apply_ids.append(cid)
        preview = starter_text_for_control(cid, org_profile, env_scope, scoped_controls)
        items.append(
            {
                "id": cid,
                "name": CMMC_FRAMEWORK[cid]["name"][:80],
                "status": ans.get("status", "NOT STARTED"),
                "has_narrative": not empty,
                "preview_chars": len(preview),
            }
        )
    return {
        "scope": scope,
        "only_empty": only_empty,
        "apply_count": len(apply_ids),
        "control_ids": apply_ids,
        "controls": items[:40],
    }


def apply_prefill(
    state: Dict[str, Any],
    scope: PrefillScope,
    org_profile: Dict[str, str],
    env_scope: Dict[str, str],
    *,
    only_empty: bool = True,
    priority_limit: int = 12,
) -> Dict[str, Any]:
    from workspace_service import patch_control

    answers = state["answers"]
    scoped = state["scoped_controls"]
    preview = prefill_preview(
        scope, answers, scoped, org_profile, env_scope, only_empty=only_empty, priority_limit=priority_limit
    )
    applied = 0
    ws = state
    for cid in preview["control_ids"]:
        text = starter_text_for_control(cid, org_profile, env_scope, scoped)
        ws = patch_control(ws, cid, implementation_narrative=text)
        applied += 1
    return {"applied": applied, "scope": scope, "control_ids": preview["control_ids"]}


def ssp_narrative_stats(answers: Dict[str, Any], scoped_controls: List[str]) -> Dict[str, Any]:
    scoped = [c for c in scoped_controls if c in answers]
    documented = 0
    missing_met = 0
    empty_any = 0
    for cid in scoped:
        ans = answers[cid]
        if has_implementation_narrative(ans):
            documented += 1
        else:
            empty_any += 1
            if ans.get("status", "NOT STARTED") in _MET_OR_NA:
                missing_met += 1
    total = len(scoped)
    pct = round(100 * documented / total) if total else 0
    return {
        "documented_count": documented,
        "empty_count": empty_any,
        "missing_met_narrative_count": missing_met,
        "scoped_count": total,
        "documented_pct": pct,
    }


def answers_with_export_starters(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    org_profile: Dict[str, str],
    env_scope: Dict[str, str],
    *,
    fill_empty: bool,
) -> Dict[str, Any]:
    """Copy answers; optionally inject starter text for empty narratives (export only)."""
    if not fill_empty:
        return answers
    out = copy.deepcopy(answers)
    scoped = [c for c in scoped_controls if c in CMMC_FRAMEWORK]
    for cid in scoped:
        ans = out.setdefault(cid, {})
        if has_implementation_narrative(ans):
            continue
        status = ans.get("status", "NOT STARTED")
        if status not in _MET_OR_NA and status != "NOT STARTED":
            continue
        if status == "NOT STARTED":
            continue
        ans["implementation_narrative"] = starter_text_for_control(cid, org_profile, env_scope, scoped)
    return out
