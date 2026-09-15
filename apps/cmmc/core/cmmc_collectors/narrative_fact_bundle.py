"""Unified fact bundle for control SSP AI drafts (linking + evidence + 171A objectives)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from controls import CMMC_FRAMEWORK
from official_800_171 import build_control_objectives

from cmmc_collectors.narrative_sanitize import (
    existing_narrative_facts_for_ai,
    resolve_narrative_org_name,
)


def _safe_strip(val: Any) -> str:
    return str(val or "").strip()


def _merge_evidence(
    base: List[Dict[str, Any]],
    extra: Optional[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    if not extra:
        return list(base or [])
    seen = {e.get("sha256") for e in (base or []) if e.get("sha256")}
    merged = list(base or [])
    for e in extra:
        if e.get("sha256") and e["sha256"] not in seen:
            seen.add(e["sha256"])
            merged.append(e)
        elif not e.get("sha256"):
            merged.append(e)
    return merged


def _org_profile_findings(profile: Dict[str, Any], env_scope: Optional[Dict[str, Any]]) -> List[str]:
    findings: List[str] = []
    for key, label in [
        ("system_description", "System description"),
        ("architecture_summary", "Architecture summary"),
        ("boundary_description", "System boundary"),
        ("hardware_inventory", "Hardware inventory"),
        ("software_inventory", "Software inventory"),
        ("system_name", "Assessed system"),
    ]:
        val = _safe_strip(profile.get(key))
        if val:
            findings.append(f"{label}: {val[:600]}")
    env = env_scope or {}
    env_entries = [f"{key}: {val}" for key, val in env.items() if val]
    if env_entries:
        findings.append(f"Environment scope: {'; '.join(env_entries)}")
    return findings


def _evidence_artifacts(evidence_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compact artifact cards for the AI (titles + summaries, no hashes)."""
    cards: List[Dict[str, Any]] = []
    for e in evidence_files or []:
        title = _safe_strip(e.get("display_title") or e.get("name") or e.get("filename"))
        if not title:
            continue
        card: Dict[str, Any] = {
            "title": title[:200],
            "evidence_type": _safe_strip(e.get("evidence_type")),
            "auto_status": _safe_strip(e.get("auto_status")),
            "period_covered": _safe_strip(e.get("period_covered") or e.get("evidence_version")),
        }
        summary = _safe_strip(e.get("auto_summary") or e.get("description"))
        if summary:
            card["summary"] = summary[:400]
        prov = e.get("provenance") if isinstance(e.get("provenance"), dict) else {}
        if prov:
            bits = [
                _safe_strip(prov.get("connector_name") or prov.get("connector_id")),
                _safe_strip(prov.get("check_name") or prov.get("check_id")),
                _safe_strip(prov.get("method")),
            ]
            bits = [b for b in bits if b]
            if bits:
                card["provenance"] = " · ".join(bits)[:200]
        cards.append(card)
        if len(cards) >= 40:
            break
    return cards


def build_narrative_fact_bundle(
    control_id: str,
    ans: Dict[str, Any],
    *,
    org_profile: Optional[Dict[str, Any]] = None,
    env_scope: Optional[Dict[str, Any]] = None,
    additional_evidence: Optional[List[Dict[str, Any]]] = None,
    collector_findings: Optional[List[str]] = None,
    collector_summary: Optional[Dict[str, Any]] = None,
    stack_label: str = "configured systems",
    include_current_narrative: bool = False,
) -> Dict[str, Any]:
    """Build the full fact pack for AI/template SSP drafts.

    include_current_narrative: when False (default), do not feed the control's
    current implementation narrative into AI/context pills — draft from org
    profile, 171A objectives, evidence, mappings, and assessment plan only.
    """
    profile = org_profile or {}
    info = CMMC_FRAMEWORK.get(control_id, {})
    summary = collector_summary or {}
    collector_count = int(summary.get("collector_count") or 0)

    findings = list(collector_findings or [])
    org_findings = _org_profile_findings(profile, env_scope)

    objectives = [
        {
            "letter": o.get("letter") or "",
            "text": o.get("text") or "",
            "status": o.get("status") or "NOT_STARTED",
        }
        for o in build_control_objectives(control_id, ans)
    ]

    evidence_files = _merge_evidence(list(ans.get("evidence") or []), additional_evidence)
    collector_lines = [
        line.get("filename")
        for line in (summary.get("lines") or [])
        if line.get("filename")
    ]
    has_collector = collector_count > 0 or bool(collector_findings)
    current = _safe_strip(ans.get("implementation_narrative"))
    raw_existing = existing_narrative_facts_for_ai({"current_narrative": current})
    # Only feed current prose when explicitly polishing it.
    existing_facts = raw_existing if include_current_narrative else ""
    has_existing_prose = bool(existing_facts)
    profile_org = _safe_strip(profile.get("org_name")) or "The organization"
    narrative_org = resolve_narrative_org_name(
        profile_org,
        existing_facts if include_current_narrative else "",
        allow_narrative_subject=include_current_narrative,
    )

    return {
        "control_id": control_id,
        "control_name": (info.get("name") or control_id).strip(),
        "catalog_description": (info.get("description") or "").strip(),
        "org_name": narrative_org,
        "profile_org_name": profile_org,
        "stack_label": stack_label,
        "status": _safe_strip(ans.get("status")) or "NOT STARTED",
        "findings": findings + org_findings,
        "collector_findings_only": findings,
        "org_profile_findings": org_findings,
        "current_narrative": current,
        "existing_narrative_facts": existing_facts,
        "has_existing_prose": has_existing_prose,
        "include_current_narrative": include_current_narrative,
        "assessor_notes": _safe_strip(ans.get("assessor_notes")),
        "remediation_plan": _safe_strip(ans.get("remediation_plan")),
        "owner": _safe_strip(ans.get("owner")),
        "target_date": _safe_strip(ans.get("target_date")),
        "linked_policies": ans.get("linked_policies") or [],
        "linked_assets": ans.get("linked_assets") or [],
        "linked_team": ans.get("linked_team") or [],
        "linked_subcontractors": ans.get("linked_subcontractors") or [],
        "evidence_files": evidence_files,
        "evidence_artifacts": _evidence_artifacts(evidence_files),
        "examine": _safe_strip(ans.get("examine")),
        "interview": _safe_strip(ans.get("interview")),
        "test": _safe_strip(ans.get("test")),
        "fips_certificate_number": _safe_strip(ans.get("fips_certificate_number")),
        "cloud_authorization_status": _safe_strip(ans.get("cloud_authorization_status")),
        "dfars_72hr_reporting_enabled": bool(ans.get("dfars_72hr_reporting_enabled")),
        "objectives": objectives,
        "collector_count": collector_count,
        "sources": collector_lines if has_collector else (["org_profile"] if org_findings else []),
        "has_org_profile_text": bool(org_findings)
        or bool(profile_org and profile_org != "The organization"),
        "has_collector_evidence": has_collector,
    }


def compute_ingested_from_bundle(bundle: Dict[str, Any]) -> List[str]:
    """Pill keys for inputs actually packed into this generation / AI prompt."""
    from official_800_171 import OFFICIAL_OBJECTIVES

    ingested: List[str] = []
    if bundle.get("has_existing_prose") or bundle.get("existing_narrative_facts"):
        ingested.append("existing_narrative")
    if (
        bundle.get("has_org_profile_text")
        or bundle.get("org_profile_findings")
        or bundle.get("profile_org_name")
        or (bundle.get("org_name") and bundle.get("org_name") != "The organization")
    ):
        ingested.append("org_profile")
    cid = str(bundle.get("control_id") or "")
    # Objectives are always injected into the AI prompt when the catalog has 171A letters.
    if bundle.get("objectives") or OFFICIAL_OBJECTIVES.get(cid):
        ingested.append("objectives")
    if bundle.get("linked_policies") or bundle.get("linked_assets"):
        ingested.append("mappings")
    artifacts = bundle.get("evidence_artifacts") or []
    files = bundle.get("evidence_files") or []
    if bundle.get("has_collector_evidence") or artifacts or files:
        ingested.append("evidence")
    if bundle.get("linked_team"):
        ingested.append("team")
    if bundle.get("linked_subcontractors"):
        ingested.append("subcontractors")
    if bundle.get("examine") or bundle.get("interview") or bundle.get("test"):
        ingested.append("assessment_plan")
    if bundle.get("remediation_plan") or bundle.get("assessor_notes"):
        ingested.append("remediation")
    return ingested
