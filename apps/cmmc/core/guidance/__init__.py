"""Unified CMMC control guidance — single place to manage summaries, objectives, and starter text."""

from __future__ import annotations

from typing import Any, Dict, List

from controls import CMMC_FRAMEWORK
def linking_profile_for_control(control_id: str) -> dict:
    """Linking profiles are part of the collectors edition."""
    return {}
def minimum_proof_for_control(control_id: str) -> dict:
    """Minimum-proof rules are part of the collectors edition."""
    return {}

from official_800_171 import OFFICIAL_OBJECTIVES

from .objectives_data import GENERATED_CONTROL_OBJECTIVES
from .overrides import (
    CONTROL_OBJECTIVE_OVERRIDES,
    DEFAULT_EVIDENCE_HINTS,
    FAMILY_PROMPTS,
    PLAIN_SUMMARY_OVERRIDES,
)
from .org_context import (
    context_evidence_hints,
    has_org_context,
    inheritance_block,
    stack_context_lines,
    stack_pattern_label,
    tailored_implementation,
)
from .summaries_data import PLAIN_SUMMARIES

def _official_objective_strings(control_id: str) -> List[str]:
    """NIST SP 800-171A determination statements (authoritative when present)."""
    rows = OFFICIAL_OBJECTIVES.get(control_id) or []
    return [f"[{letter}] {text}" for letter, text in rows]


# Prefer official 171A determination statements over generated examine/interview/test
# prompts and hand overrides (authoritative NIST SP 800-171A text).
CONTROL_OBJECTIVES: Dict[str, List[str]] = {
    **GENERATED_CONTROL_OBJECTIVES,
    **CONTROL_OBJECTIVE_OVERRIDES,
    **{cid: _official_objective_strings(cid) for cid in OFFICIAL_OBJECTIVES},
}


def plain_summary(control_id: str) -> str:
    """One-line plain-English summary for a control."""
    if control_id in PLAIN_SUMMARY_OVERRIDES:
        return PLAIN_SUMMARY_OVERRIDES[control_id]
    if control_id in PLAIN_SUMMARIES:
        return PLAIN_SUMMARIES[control_id]
    info = CMMC_FRAMEWORK.get(control_id, {})
    name = (info.get("name") or "").strip()
    if not name:
        return "Document how your organization meets this requirement."
    if len(name) <= 100:
        return name
    return name[:97] + "…"


def objectives_for_control(control_id: str) -> List[str]:
    """800-171A-style examine/interview/test prompts for one control."""
    return list(CONTROL_OBJECTIVES.get(control_id, []))


def family_prompts(family: str) -> List[str]:
    """Family-level assessment prompts."""
    return list(FAMILY_PROMPTS.get(family, []))


def prompts_for_family(family: str) -> List[str]:
    """Alias used by Pre-C3PAO and control editor."""
    return family_prompts(family)


def get_control_guidance(
    control_id: str,
    org_profile: Optional[Dict[str, str]] = None,
    env_scope: Optional[Dict[str, str]] = None,
    scoped_controls: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Full guidance bundle for API / UI — one call, one source of truth."""
    info = CMMC_FRAMEWORK.get(control_id, {})
    name = (info.get("name") or "").strip()
    plain = plain_summary(control_id)
    if plain.strip() == name.strip():
        plain = ""
    catalog = (info.get("description") or "").strip()
    objectives = objectives_for_control(control_id)
    profile_evidence = linking_profile_for_control(control_id).get("evidence_types", [])
    evidence_hints = profile_evidence if profile_evidence else list(DEFAULT_EVIDENCE_HINTS)
    family = info.get("family", "")
    profile = org_profile or {}
    env = env_scope or {}
    scoped = scoped_controls or []
    org_ctx = has_org_context(profile, env)
    extra_evidence = context_evidence_hints(control_id, env, scoped) if org_ctx else []
    merged_hints = list(dict.fromkeys(profile_evidence + extra_evidence))[:6]

    return {
        "control_id": control_id,
        "name": name,
        "family": family,
        "weight": info.get("weight"),
        "plain_summary": plain,
        "catalog_description": catalog,
        "objectives": objectives,
        "evidence_hints": merged_hints,
        "minimum_proof": minimum_proof_for_control(control_id),
        "family_prompts": family_prompts(family),
        "starter_narrative": starter_narrative(control_id, family, profile, env, scoped),
        "org_context_used": org_ctx,
        "stack_pattern": stack_pattern_label(env),
    }


def starter_narrative(
    control_id: str,
    family: str = "",
    org_profile: Optional[Dict[str, str]] = None,
    env_scope: Optional[Dict[str, str]] = None,
    scoped_controls: Optional[List[str]] = None,
    ans: Optional[Dict[str, Any]] = None,
) -> str:
    """Draft SSP narrative — org context + tailored implementation + 800-171A objectives."""
    info = CMMC_FRAMEWORK.get(control_id, {})
    fam = family or info.get("family", "")
    profile = org_profile or {}
    env = env_scope or {}
    scoped = scoped_controls or []
    answer = ans or {}

    lines = [f"Control {control_id}: {info.get('name', '')}", ""]

    context_lines = stack_context_lines(profile, env) if has_org_context(profile, env) else []
    if context_lines:
        lines.extend(["Organization context:"])
        for line in context_lines:
            lines.append(f"- {line}")
        lines.append("")

    tailored = tailored_implementation(control_id, fam, profile, env) if has_org_context(profile, env) else None
    catalog = info.get("description", "Describe your implementation here.")
    lines.append("Implementation summary:")
    if tailored:
        lines.append(tailored)
        lines.append("")
        lines.append(f"Catalog reference: {catalog}")
    else:
        lines.append(catalog)

    # Inject real details from control inputs when available
    evidence = answer.get("evidence") or []
    policies = answer.get("linked_policies") or []
    assets = answer.get("linked_assets") or []
    examine = str(answer.get("examine") or "").strip()
    interview = str(answer.get("interview") or "").strip()
    test = str(answer.get("test") or "").strip()
    if evidence or policies or assets or examine or interview or test:
        lines.append("")
        lines.append("Mapped evidence and resources:")
        if evidence:
            for e in evidence[:10]:
                title = e.get("display_title") or e.get("filename", "Untitled")
                summary = (e.get("auto_summary") or e.get("description") or "").strip()
                line = f"  - {title[:120]}"
                if summary:
                    line += f": {summary[:200]}"
                lines.append(line)
        if policies:
            for p in policies[:10]:
                title = p.get("title", "Untitled")
                ver = p.get("version", "")
                lines.append(f"  - Policy: {title}" + (f" v{ver}" if ver else ""))
        if assets:
            for a in assets[:10]:
                name = a.get("name", "Unknown")
                atype = a.get("type", "")
                cui = a.get("cui", False)
                lines.append(f"  - Asset: {name}" + (f" ({atype})" if atype else "") + (" [CUI]" if cui else ""))
        if examine:
            lines.append(f"  - Examine: {examine[:400]}")
        if interview:
            lines.append(f"  - Interview: {interview[:400]}")
        if test:
            lines.append(f"  - Test: {test[:400]}")
    fips = str(answer.get("fips_certificate_number") or "").strip()
    cloud = str(answer.get("cloud_authorization_status") or "").strip()
    dfars = answer.get("dfars_72hr_reporting_enabled")
    if fips:
        lines.append(f"  - FIPS certificate: {fips[:200]}")
    if cloud:
        lines.append(f"  - Cloud authorization: {cloud[:200]}")
    if dfars:
        lines.append("  - DFARS 72-hour reporting: enabled")

    inherited = inheritance_block(control_id, env, scoped) if scoped else None
    if inherited:
        org_text, provider_text, citation = inherited
        lines.extend(["", "Shared responsibility:"])
        if org_text:
            lines.append(f"- Organization: {org_text}")
        if provider_text:
            lines.append(f"- Provider: {provider_text}")
        if citation:
            lines.append(f"- Suggested evidence: {citation}")

    lines.extend(["", "Assessment approach (800-171A):"])
    for prompt in objectives_for_control(control_id) or [f"Document implementation for {control_id}."]:
        lines.append(f"- {prompt}")
    if fam:
        lines.extend(["", f"Family context ({fam}):"])
        for fp in family_prompts(fam)[:2]:
            lines.append(f"- {fp}")

    evidence_lines = ["", "Evidence / references:"]
    for hint in context_evidence_hints(control_id, env, scoped):
        evidence_lines.append(f"- {hint}")
    evidence_lines.append("- [Add policy name, config export, or ticket ID]")
    lines.extend(evidence_lines)
    return "\n".join(lines)


def objective_coverage(answers: dict, scoped_controls: list) -> dict:
    """How many scoped controls have narrative or E/I/T fields filled."""
    covered = []
    missing = []
    for cid in scoped_controls:
        ans = answers.get(cid, {})
        has = bool(
            (ans.get("implementation_narrative") or "").strip()
            or (ans.get("examine") or "").strip()
            or (ans.get("interview") or "").strip()
            or (ans.get("test") or "").strip()
        )
        (covered if has else missing).append(cid)
    total = len(scoped_controls)
    pct = round(100 * len(covered) / total) if total else 0
    return {
        "covered_count": len(covered),
        "missing_count": len(missing),
        "total": total,
        "pct": pct,
        "missing_sample": missing[:10],
        "catalog_objectives_count": len(CONTROL_OBJECTIVES),
    }
