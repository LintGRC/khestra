"""Unified SSP narrative generator — evidence first, starter fallback, optional AI polish."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Literal, Optional

from ai_config import is_available as ai_is_available
from cmmc_collectors.narrative_fact_bundle import (
    build_narrative_fact_bundle,
    compute_ingested_from_bundle,
)
from cmmc_collectors.ssp_narrative_suggest import suggest_ssp_narrative_from_evidence
from controls import CMMC_FRAMEWORK
from guidance import starter_narrative

logger = logging.getLogger(__name__)

GenerateScope = Literal["missing_met", "all_empty", "all"]

_MET_OR_NA = frozenset({"MET", "NOT APPLICABLE", "INHERITED"})


def _controls_for_scope(
    scope: GenerateScope,
    answers: Dict[str, Any],
    scoped_controls: List[str],
) -> List[str]:
    scoped = [c for c in scoped_controls if c in CMMC_FRAMEWORK]
    if scope == "missing_met":
        return [
            cid for cid in scoped
            if answers.get(cid, {}).get("status", "NOT STARTED") in _MET_OR_NA
            and not (answers.get(cid, {}).get("implementation_narrative") or "").strip()
        ]
    if scope == "all_empty":
        return [
            cid for cid in scoped
            if not (answers.get(cid, {}).get("implementation_narrative") or "").strip()
        ]
    return scoped


def _safe_strip(val: Any) -> str:
    return str(val or "").strip()


def generate_narrative(
    control_id: str,
    answers: Dict[str, Any],
    org_profile: Dict[str, str],
    env_scope: Dict[str, Any],
    scoped_controls: List[str],
    restored_evidence: Optional[Dict[str, bytes]] = None,
    additional_evidence: Optional[List[Dict[str, Any]]] = None,
    *,
    use_ai: bool = False,
    force: bool = False,
    include_current_narrative: bool = False,
) -> Dict[str, Any]:
    """Generate best-effort SSP narrative from available data.

    By default (include_current_narrative=False) drafts from org profile, 171A
    objectives, evidence, mappings, and assessment plan — not the current text
    being replaced. Set include_current_narrative=True to tighten existing prose.
    """
    ans = answers.get(control_id) or {}
    current = _safe_strip(ans.get("implementation_narrative"))
    human_edited = ans.get("human_edited", False)

    preview_bundle = build_narrative_fact_bundle(
        control_id,
        ans,
        org_profile=org_profile,
        env_scope=env_scope,
        additional_evidence=additional_evidence,
        include_current_narrative=include_current_narrative,
    )
    preview_ingested = compute_ingested_from_bundle(preview_bundle)

    if human_edited and not force:
        return _result(current, ["existing_human"], "preserved", 0, ingested=preview_ingested)

    suggestion = None
    collector_count = 0
    try:
        suggestion = suggest_ssp_narrative_from_evidence(
            control_id,
            answers,
            restored_evidence,
            org_profile=org_profile,
            org_name=(org_profile or {}).get("org_name") or "",
            env_scope=env_scope,
            additional_evidence=additional_evidence,
            use_ai=use_ai,
            include_current_narrative=include_current_narrative,
        )
        collector_count = suggestion["collector_count"]
    except ValueError:
        pass

    if collector_count > 0 and suggestion:
        draft = suggestion["suggested_narrative"]
        method = suggestion["method"]
        sources = ["evidence"]
        if method == "ai":
            sources.append("ai")
        ingested = suggestion.get("ingested") or compute_ingested_from_bundle(
            suggestion.get("bundle") or preview_bundle
        )
        return _result(
            draft,
            sources,
            method,
            collector_count,
            ingested=ingested,
            ai_error=suggestion.get("ai_error"),
        )

    # Evidence-only: start from starter (or empty template), never seed AI with
    # the current narrative unless polish mode is on.
    if include_current_narrative and preview_bundle.get("has_existing_prose") and current:
        draft = current
        sources = ["existing_narrative"]
        method = "existing"
    else:
        draft = starter_narrative(
            control_id,
            org_profile=org_profile,
            env_scope=env_scope,
            scoped_controls=scoped_controls,
            ans=ans,
        )
        sources = ["starter"]
        method = "starter"
    bundle = preview_bundle
    ingested = preview_ingested

    fips = _safe_strip(ans.get("fips_certificate_number"))
    cloud = _safe_strip(ans.get("cloud_authorization_status"))
    dfars = ans.get("dfars_72hr_reporting_enabled")
    compliance_bits: List[str] = []
    if fips:
        compliance_bits.append(f"FIPS certificate: {fips}")
    if cloud:
        compliance_bits.append(f"Cloud authorization: {cloud}")
    if dfars:
        compliance_bits.append("DFARS 72-hour reporting: enabled")
    if compliance_bits:
        draft = draft + "\n\n" + "; ".join(compliance_bits) + "."

    ai_error: Optional[str] = None
    if use_ai and ai_is_available():
        try:
            from cmmc_collectors.ai_narrative import polish_ssp_narrative_with_ai
            from cmmc_collectors.ssp_draft_linter import lint_ssp_draft

            polished = polish_ssp_narrative_with_ai(bundle, draft)
            lint_result = lint_ssp_draft(polished, bundle)
            if not any(
                "does not look like SSP prose" in w or "assessor gap essay" in w
                for w in lint_result["warnings"]
            ):
                draft = polished
                method = "ai"
                sources = list(dict.fromkeys([*sources, "ai"]))
        except Exception as exc:
            logger.warning("AI polish of starter narrative failed: %s", exc)
            ai_error = str(exc)

    return _result(draft, sources, method, 0, ingested=ingested, ai_error=ai_error)


def generate_all_narratives(
    state: Dict[str, Any],
    *,
    scope: GenerateScope = "missing_met",
    use_ai: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    """Generate and save narratives for all controls matching the given scope."""
    from workspace_service import patch_control

    answers = state["answers"]
    scoped_controls = state["scoped_controls"]
    org_profile = state.get("org_profile") or {}
    env_scope = state.get("env_scope") or {}
    restored_evidence = state.get("restored_evidence")

    candidates = _controls_for_scope(scope, answers, scoped_controls)
    generated = 0
    skipped = 0
    ws = state
    for cid in candidates:
        ans = answers.get(cid) or {}
        if ans.get("human_edited") and not force:
            skipped += 1
            continue
        result = generate_narrative(
            cid, answers, org_profile, env_scope, scoped_controls, restored_evidence, use_ai=use_ai, force=force,
        )
        if result["method"] == "preserved":
            skipped += 1
        else:
            ws = patch_control(ws, cid, implementation_narrative=result["narrative"], human_edited=False)
            generated += 1
    return {"scope": scope, "candidate_count": len(candidates), "generated": generated, "skipped": skipped}


def _result(
    narrative: str, sources: List[str], method: str, collector_count: int,
    ingested: Optional[List[str]] = None,
    ai_error: Optional[str] = None,
) -> Dict[str, Any]:
    result = {
        "narrative": narrative,
        "sources": sources,
        "method": method,
        "collector_count": collector_count,
        "ai_available": ai_is_available(),
        "ai_error": ai_error,
    }
    if ingested is not None:
        result["ingested"] = ingested
    return result
