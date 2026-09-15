"""SSP narrative suggestions from attached collector evidence (template + optional AI polish)."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from ai_config import is_available as ai_is_available
from controls import CMMC_FRAMEWORK
from evidence_store import get_evidence_bytes

from cmmc_collectors.ai_narrative import polish_ssp_narrative_with_ai
from cmmc_collectors.narrative_fact_bundle import build_narrative_fact_bundle, compute_ingested_from_bundle
from cmmc_collectors.narrative_merge import is_starter_template_narrative, merge_ssp_narrative, preview_merges
from cmmc_collectors.ssp_draft_linter import lint_ssp_draft
from cmmc_collectors.evidence_summarize import (
    _format_collected_at,
    _parse_collector_payload,
    collector_evidence_bytes,
    summarize_control_collector_evidence,
)

logger = logging.getLogger(__name__)

_GAP_STATUSES = frozenset({"NOT MET", "PARTIALLY MET", "IN PROGRESS", "PLANNED"})

_CONNECTOR_LABELS = {
    "entra": "Microsoft Entra ID",
    "aws": "Amazon Web Services",
}


def _short_date(value: str) -> str:
    s = (value or "").strip()
    if not s:
        return ""
    if "T" in s:
        return s.split("T", 1)[0]
    if len(s) >= 10 and s[4] == "-":
        return s[:10]
    return s.split(" ", 1)[0]


def _stack_label(connectors: List[str]) -> str:
    if not connectors:
        return "integrated systems"
    if len(connectors) == 1:
        return _CONNECTOR_LABELS.get(connectors[0], connectors[0])
    labels = [_CONNECTOR_LABELS.get(c, c) for c in connectors]
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


def _control_topic(control_name: str) -> str:
    name = (control_name or "").strip()
    if not name:
        return "this control requirement"
    if name[0].isupper() and name.split(" ", 1)[0].isalpha():
        lowered = name[0].lower() + name[1:]
        return lowered.rstrip(".")
    return name.rstrip(".")


def _collector_findings(
    control_id: str,
    answers: Dict[str, Any],
    restored_evidence: Optional[Dict[str, bytes]] = None,
) -> List[str]:
    ans = answers.get(control_id) or {}
    findings: List[str] = []
    for ev in ans.get("evidence") or []:
        filename = ev.get("filename") or ""
        if not str(filename).startswith("collector_"):
            continue
        data = collector_evidence_bytes(control_id, ev, restored_evidence)
        if not data:
            continue
        payload = _parse_collector_payload(data)
        if not payload:
            continue
        check_name = payload.get("check_name") or payload.get("check_id") or "check"
        evidence = (payload.get("evidence") or "").strip()
        status = payload.get("status") or "unknown"
        collected = _format_collected_at(payload, ev)
        date_part = f" (verified {_short_date(collected)})" if collected else ""
        if status == "pass":
            findings.append(f"{check_name}: {evidence}{date_part}")
        else:
            findings.append(f"{check_name}: {evidence} — collector status {status}{date_part}")
    return findings


def _build_fact_bundle(
    control_id: str,
    answers: Dict[str, Any],
    summary: Dict[str, Any],
    findings: List[str],
    org_profile: Optional[Dict[str, str]],
    org_name: str,
    env_scope: Optional[Dict[str, Any]] = None,
    additional_evidence: Optional[List[Dict[str, Any]]] = None,
    *,
    include_current_narrative: bool = False,
) -> Dict[str, Any]:
    profile = dict(org_profile or {})
    if org_name and not profile.get("org_name"):
        profile["org_name"] = org_name
    connectors = sorted({line["connector"] for line in summary["lines"] if line.get("connector")})
    return build_narrative_fact_bundle(
        control_id,
        answers.get(control_id) or {},
        org_profile=profile,
        env_scope=env_scope,
        additional_evidence=additional_evidence,
        collector_findings=findings,
        collector_summary=summary,
        stack_label=_stack_label(connectors),
        include_current_narrative=include_current_narrative,
    )


def deterministic_ssp_from_bundle(bundle: Dict[str, Any]) -> str:
    existing = (bundle.get("existing_narrative_facts") or "").strip()
    if existing:
        draft = existing
    else:
        topic = _control_topic(bundle.get("control_name") or "")
        paragraphs: List[str] = [
            f"{bundle['org_name']} implements {topic} using {bundle['stack_label']}."
        ]
        findings = bundle.get("collector_findings_only") or [
            f
            for f in (bundle.get("findings") or [])
            if not str(f).startswith(
                (
                    "System description:",
                    "Architecture summary:",
                    "System boundary:",
                    "Hardware inventory:",
                    "Software inventory:",
                    "Environment scope:",
                )
            )
        ]
        if findings:
            paragraphs.append("Technical verification: " + "; ".join(findings) + ".")

        status = bundle.get("status") or ""
        if status in _GAP_STATUSES:
            gap_bits: List[str] = []
            if bundle.get("remediation_plan"):
                gap_bits.append(f"Remediation: {bundle['remediation_plan']}")
            if bundle.get("target_date"):
                gap_bits.append(f"Target completion: {bundle['target_date']}")
            if bundle.get("owner"):
                gap_bits.append(f"Owner: {bundle['owner']}")
            if gap_bits:
                paragraphs.append(" ".join(gap_bits) + ".")

        artifacts = bundle.get("evidence_artifacts") or []
        if artifacts:
            titles = [a.get("title") for a in artifacts[:6] if a.get("title")]
            if titles:
                paragraphs.append("Supporting evidence on file includes: " + "; ".join(titles) + ".")
        elif bundle.get("collector_count"):
            paragraphs.append(
                f"Supporting collector exports are attached to this control ({bundle['collector_count']} file(s))."
            )
        policies = [
            str(p.get("title") or "").strip()
            for p in (bundle.get("linked_policies") or [])
            if isinstance(p, dict) and p.get("title")
        ]
        if policies:
            paragraphs.append("Mapped policies: " + "; ".join(policies) + ".")
        team_names: List[str] = []
        for t in bundle.get("linked_team") or []:
            if isinstance(t, str) and t.strip():
                team_names.append(t.strip())
            elif isinstance(t, dict) and t.get("name"):
                team_names.append(str(t["name"]).strip())
        if team_names:
            paragraphs.append("Linked personnel: " + ", ".join(team_names) + ".")
        draft = "\n\n".join(paragraphs)

    fips = str(bundle.get("fips_certificate_number") or "").strip()
    cloud = str(bundle.get("cloud_authorization_status") or "").strip()
    dfars = bundle.get("dfars_72hr_reporting_enabled")
    bits: List[str] = []
    if fips:
        bits.append(f"FIPS certificate: {fips}")
    if cloud:
        bits.append(f"Cloud authorization: {cloud}")
    if dfars:
        bits.append("DFARS 72-hour reporting: enabled")
    if bits:
        draft = draft + "\n\n" + "; ".join(bits) + "."
    return draft


def suggest_ssp_narrative_from_evidence(
    control_id: str,
    answers: Dict[str, Any],
    restored_evidence: Optional[Dict[str, bytes]] = None,
    org_profile: Optional[Dict[str, str]] = None,
    org_name: str = "",
    env_scope: Optional[Dict[str, Any]] = None,
    additional_evidence: Optional[List[Dict[str, Any]]] = None,
    *,
    use_ai: bool = True,
    include_current_narrative: bool = False,
) -> Dict[str, Any]:
    """Build an SSP paragraph from collector JSON; polish with AI when env key is set."""
    if control_id not in CMMC_FRAMEWORK:
        raise ValueError("Control not found")

    summary = summarize_control_collector_evidence(control_id, answers, restored_evidence)
    if summary["collector_count"] == 0:
        raise ValueError("No collector evidence attached to this control")

    findings = _collector_findings(control_id, answers, restored_evidence)
    bundle = _build_fact_bundle(
        control_id,
        answers,
        summary,
        findings,
        org_profile,
        org_name,
        env_scope=env_scope,
        additional_evidence=additional_evidence,
        include_current_narrative=include_current_narrative,
    )
    deterministic = deterministic_ssp_from_bundle(bundle)

    method = "deterministic"
    suggested = deterministic
    ai_error: Optional[str] = None

    if use_ai and ai_is_available():
        try:
            suggested = polish_ssp_narrative_with_ai(bundle, deterministic)
            lint_probe = lint_ssp_draft(suggested, bundle)
            if any(
                "does not look like SSP prose" in w or "assessor gap essay" in w
                for w in lint_probe["warnings"]
            ):
                raise RuntimeError("AI returned non-SSP content; using template draft")
            method = "ai"
        except Exception as exc:
            logger.warning("AI SSP polish failed, using template: %s", exc)
            ai_error = str(exc)
            suggested = deterministic
            method = "deterministic"

    current = bundle["current_narrative"]
    merges = preview_merges(current, suggested, sources=bundle["sources"])
    lint_result = lint_ssp_draft(suggested, bundle) if method == "ai" else {"passed": True, "warnings": []}

    return {
        "control_id": control_id,
        "status": bundle["status"],
        "collector_count": bundle["collector_count"],
        "current_narrative": current,
        "suggested_narrative": suggested,
        "deterministic_narrative": deterministic,
        "sources": bundle["sources"],
        "method": method,
        "ai_available": ai_is_available(),
        "ai_error": ai_error,
        "narrative_format": merges["narrative_format"],
        "lint_passed": lint_result["passed"],
        "lint_warnings": lint_result["warnings"],
        "ingested": compute_ingested_from_bundle(bundle),
        "bundle": bundle,
        "merge_preview": {
            "append": merges["append"],
            "replace": merges["replace"],
            "append_strategy": merges["append_strategy"],
            "replace_strategy": merges["replace_strategy"],
        },
    }


def apply_ssp_suggestion_to_control(
    state: Dict[str, Any],
    control_id: str,
    *,
    mode: str = "replace",
    use_ai: bool = True,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    from workspace_service import patch_control

    suggestion = suggest_ssp_narrative_from_evidence(
        control_id,
        state["answers"],
        state.get("restored_evidence"),
        org_profile=state.get("org_profile") or {},
        org_name=(state.get("org_name") or "").strip(),
        use_ai=use_ai,
    )
    ans = state["answers"].get(control_id) or {}
    existing = ans.get("implementation_narrative") or ""
    new_narrative, merge_strategy = merge_ssp_narrative(
        existing,
        suggestion["suggested_narrative"],
        mode,
        sources=suggestion.get("sources") or [],
    )
    ws = patch_control(state, control_id, implementation_narrative=new_narrative)
    return ws, {
        **suggestion,
        "implementation_narrative": new_narrative,
        "mode": mode,
        "merge_strategy": merge_strategy,
        "narrative_format": suggestion.get("narrative_format")
        or ("starter" if is_starter_template_narrative(existing) else "prose"),
    }
