"""Readiness review — evidence gaps, narrative quality, contradictions, remediation roadmap."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple

from annex_weights import annex_weight
from controls import CMMC_FRAMEWORK
from official_800_171 import build_control_objectives

MIN_NARRATIVE_CHARS = 80
CLOSED_STATUSES = frozenset({"MET", "NOT APPLICABLE", "INHERITED"})
OPEN_GAP_STATUSES = frozenset(
    {"NOT MET", "PARTIALLY MET", "IN PROGRESS", "PLANNED", "NOT STARTED"}
)

WIRELESS_CONTROLS = ("AC.L2-3.1.16", "AC.L2-3.1.17", "AC.L2-3.1.18")
REMOTE_CONTROLS = ("AC.L2-3.1.12", "AC.L2-3.1.13", "AC.L2-3.1.14")

REMEDIATION_DIFFICULTY: Dict[str, str] = {
    "IA.L2-3.5.3": "Medium",
    "SC.L2-3.13.11": "High",
    "SC.L2-3.13.8": "Medium",
    "SC.L2-3.13.16": "Medium",
    "AC.L2-3.1.8": "Low",
    "AU.L2-3.3.4": "Medium",
    "AU.L2-3.3.5": "High",
    "CM.L2-3.4.7": "Medium",
    "SI.L2-3.14.2": "Low",
    "SI.L2-3.14.6": "High",
    "IR.L2-3.6.1": "Medium",
    "RA.L2-3.11.2": "Medium",
}


def _narrative(ans: dict) -> str:
    return (
        ans.get("implementation_narrative", "").strip()
        or ans.get("assessor_notes", "").strip()
    )


def _has_evidence_or_examine(ans: dict) -> bool:
    return bool(ans.get("evidence")) or bool((ans.get("examine") or "").strip())


def assessment_fingerprint(answers: Dict[str, Any], scoped_controls: List[str]) -> str:
    parts: List[str] = []
    for cid in sorted(scoped_controls):
        ans = answers.get(cid, {})
        narrative = _narrative(ans)[:240]
        parts.append(f"{cid}|{ans.get('status', '')}|{narrative}")
    digest = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
    return digest[:16]


def met_evidence_breakdown(
    answers: Dict[str, Any], scoped_controls: List[str]
) -> Dict[str, Any]:
    met = [c for c in scoped_controls if answers.get(c, {}).get("status") == "MET"]
    with_support = [c for c in met if _has_evidence_or_examine(answers[c])]
    without = [c for c in met if c not in with_support]
    return {
        "met_count": len(met),
        "with_evidence_count": len(with_support),
        "without_evidence_count": len(without),
        "without_evidence_ids": without[:25],
    }


def short_narrative_controls(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    min_chars: int = MIN_NARRATIVE_CHARS,
) -> List[str]:
    out: List[str] = []
    for cid in scoped_controls:
        ans = answers.get(cid, {})
        if ans.get("status") != "MET":
            continue
        if len(_narrative(ans)) < min_chars:
            out.append(cid)
    return out


def _text_blob(*chunks: str) -> str:
    return " ".join((c or "").lower() for c in chunks)


def _find_contradictions(
    answers: Dict[str, Any],
    org_profile: Dict[str, str],
    scoped_controls: List[str],
    env_scope: Optional[Dict[str, str]] = None,
    asset_scope: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    if env_scope:
        from env_scope import env_scope_contradictions

        findings.extend(
            env_scope_contradictions(
                env_scope, answers, scoped_controls, asset_scope, org_profile
            )
        )
    arch = _text_blob(
        org_profile.get("architecture_summary", ""),
        org_profile.get("boundary_description", ""),
        org_profile.get("system_description", ""),
    )

    wireless_in_scope = any(
        answers.get(c, {}).get("status") in ("MET", "NOT MET", "PARTIALLY MET", "IN PROGRESS")
        for c in WIRELESS_CONTROLS
        if c in scoped_controls
    )
    wireless_all_na = all(
        answers.get(c, {}).get("status") in ("NOT APPLICABLE", "INHERITED")
        for c in WIRELESS_CONTROLS
        if c in scoped_controls
    )
    if wireless_all_na and re.search(r"\b(wifi|wi-fi|wireless)\b", arch):
        findings.append(
            {
                "severity": "high",
                "title": "Wireless marked N/A but environment mentions wireless",
                "detail": (
                    "Architecture or boundary text references Wi-Fi/wireless, but "
                    "3.1.16–3.1.18 are Not Applicable/Inherited. Align scope or narratives."
                ),
            }
        )

    if not wireless_in_scope and wireless_all_na and re.search(r"\b(vpn|remote access)\b", arch):
        remote_open = [
            c
            for c in REMOTE_CONTROLS
            if c in scoped_controls
            and answers.get(c, {}).get("status") not in CLOSED_STATUSES
        ]
        if remote_open:
            findings.append(
                {
                    "severity": "medium",
                    "title": "Remote access gaps while wireless is N/A",
                    "detail": (
                        f"Environment mentions remote access/VPN; review {', '.join(remote_open[:3])} "
                        "and wireless scope for consistency."
                    ),
                }
            )

    for cid in scoped_controls:
        ans = answers.get(cid, {})
        status = ans.get("status", "NOT STARTED")
        narrative = _narrative(ans).lower()
        if status == "MET" and not _has_evidence_or_examine(ans):
            findings.append(
                {
                    "severity": "high",
                    "title": f"{cid}: MET without evidence or examine reference",
                    "detail": "Attach evidence or cite a policy/SOP in Examine before audit.",
                }
            )
        if status == "MET" and len(_narrative(ans)) < MIN_NARRATIVE_CHARS:
            findings.append(
                {
                    "severity": "medium",
                    "title": f"{cid}: MET with very short narrative",
                    "detail": f"Implementation text is under {MIN_NARRATIVE_CHARS} characters — expand for SSP export.",
                }
            )
        if status in ("NOT MET", "PARTIALLY MET") and not (
            ans.get("assessor_notes", "").strip() or ans.get("remediation_plan", "").strip()
        ):
            findings.append(
                {
                    "severity": "medium",
                    "title": f"{cid}: Open gap without POA&M notes",
                    "detail": "Add assessor notes or remediation plan for POA&M export.",
                }
            )
        if status == "MET" and cid == "IA.L2-3.5.3":
            if narrative and not re.search(r"\b(mfa|multifactor|multi-factor|authenticator)\b", narrative):
                findings.append(
                    {
                        "severity": "medium",
                        "title": "3.5.3 MET but narrative does not mention MFA",
                        "detail": "MFA control marked MET — narrative should describe MFA implementation.",
                    }
                )

    # De-duplicate by title (MET without evidence fires per control — keep those)
    return findings


def summarize_review_findings(findings: List[Dict[str, str]]) -> Dict[str, Any]:
    """Group repetitive findings for clearer UI (not one row per control at top level)."""
    met_no_proof: List[str] = []
    short_narrative: List[str] = []
    gap_no_poam: List[str] = []
    scope_checks: List[Dict[str, str]] = []
    narrative_checks: List[Dict[str, str]] = []
    other: List[Dict[str, str]] = []

    for f in findings:
        title = f["title"]
        cid_match = re.match(r"^([A-Z]{2}\.L2-[\d.]+)", title)
        cid = cid_match.group(1) if cid_match else None
        if "MET without evidence" in title:
            if cid:
                met_no_proof.append(cid)
        elif "short narrative" in title:
            if cid:
                short_narrative.append(cid)
        elif "Open gap without POA&M" in title:
            if cid:
                gap_no_poam.append(cid)
        elif cid and "narrative does not mention" in title:
            narrative_checks.append(f)
        elif f["severity"] == "high" and not cid:
            scope_checks.append(f)
        elif f["severity"] == "high":
            other.append(f)
        else:
            other.append(f)

    return {
        "met_no_proof_ids": met_no_proof,
        "met_no_proof_count": len(met_no_proof),
        "short_narrative_ids": short_narrative,
        "short_narrative_count": len(short_narrative),
        "gap_no_poam_ids": gap_no_poam,
        "gap_no_poam_count": len(gap_no_poam),
        "scope_checks": scope_checks,
        "narrative_checks": narrative_checks,
        "other": other,
    }


def package_quality_explanation(
    evidence: Dict[str, Any], summary: Dict[str, Any]
) -> str:
    """One plain-language sentence for the package quality score."""
    parts: List[str] = []
    if summary["met_no_proof_count"]:
        parts.append(
            f"{summary['met_no_proof_count']} MET control(s) lack an uploaded file or Examine reference"
        )
    if summary["short_narrative_count"]:
        parts.append(
            f"{summary['short_narrative_count']} MET control(s) have very short implementation text"
        )
    if summary["gap_no_poam_count"]:
        parts.append(
            f"{summary['gap_no_poam_count']} open gap(s) need POA&M notes"
        )
    if summary["scope_checks"] or summary["narrative_checks"]:
        parts.append("environment or narrative consistency checks flagged")
    if not parts and evidence["met_count"]:
        return "MET controls have proof attached and no major consistency flags."
    if not evidence["met_count"]:
        return "Mark controls MET on the Controls screen to track proof and narratives."
    return "; ".join(parts[:3]) + "."


def _difficulty_for(cid: str) -> str:
    if cid in REMEDIATION_DIFFICULTY:
        return REMEDIATION_DIFFICULTY[cid]
    w = annex_weight(cid)
    if w >= 5:
        return "Medium"
    if w >= 3:
        return "Medium"
    return "Low"


def _priority_label(weight: int, difficulty: str) -> str:
    if weight >= 5:
        return "High"
    if weight >= 3 and difficulty == "High":
        return "High"
    if weight >= 3:
        return "Medium"
    return "Low"


def build_compliance_roadmap(
    answers: Dict[str, Any], scoped_controls: List[str], limit: int = 20
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for cid in scoped_controls:
        status = answers.get(cid, {}).get("status", "NOT STARTED")
        if status in CLOSED_STATUSES:
            continue
        weight = annex_weight(cid)
        difficulty = _difficulty_for(cid)
        rows.append(
            {
                "control_id": cid,
                "gap": CMMC_FRAMEWORK[cid]["name"][:70],
                "status": status,
                "score_impact": weight,
                "difficulty": difficulty,
                "priority": _priority_label(weight, difficulty),
            }
        )
    rows.sort(key=lambda r: (-r["score_impact"], r["priority"] != "High", r["control_id"]))
    return rows[:limit]


def run_readiness_review(
    answers: Dict[str, Any],
    org_profile: Dict[str, str],
    scoped_controls: List[str],
    env_scope: Optional[Dict[str, str]] = None,
    asset_scope: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    evidence = met_evidence_breakdown(answers, scoped_controls)
    short_narratives = short_narrative_controls(answers, scoped_controls)
    findings = _find_contradictions(
        answers, org_profile, scoped_controls, env_scope, asset_scope
    )
    high = [f for f in findings if f["severity"] == "high"]
    medium = [f for f in findings if f["severity"] == "medium"]
    roadmap = build_compliance_roadmap(answers, scoped_controls)
    finding_summary = summarize_review_findings(findings)
    obj_stats = _compute_objective_stats(answers, scoped_controls)

    met = evidence["met_count"]
    with_ev = evidence["with_evidence_count"]
    review_score = 100
    if met:
        review_score -= min(40, round(40 * (met - with_ev) / met))
    review_score -= min(25, len(short_narratives) * 2)
    review_score -= min(35, len(high) * 5 + len(medium) * 2)
    # objective completion penalty: up to 10 points deduction
    if obj_stats["total"]:
        review_score -= min(10, round(10 * (1 - obj_stats["met"] / obj_stats["total"])))

    review_score = max(0, min(100, review_score))

    return {
        "review_score": review_score,
        "evidence": evidence,
        "short_narrative_count": len(short_narratives),
        "short_narrative_ids": short_narratives[:15],
        "findings": findings,
        "high_findings": high,
        "medium_findings": medium,
        "high_count": len(high),
        "medium_count": len(medium),
        "roadmap": roadmap,
        "finding_summary": finding_summary,
        "quality_explanation": package_quality_explanation(evidence, finding_summary),
        "objectives": obj_stats,
    }


def _compute_objective_stats(
    answers: Dict[str, Any], scoped_controls: List[str]
) -> Dict[str, Any]:
    total = 0
    met = 0
    for cid in scoped_controls:
        objs = build_control_objectives(cid, answers.get(cid))
        for o in objs:
            total += 1
            if o.get("status", "").upper() in ("MET", "COMPLIANT"):
                met += 1
    return {
        "total": total,
        "met": met,
        "pct": round(met / total * 100) if total else 0,
        "controls_with_objectives": sum(
            1 for cid in scoped_controls
            if build_control_objectives(cid, answers.get(cid))
        ),
    }


def format_readiness_review_report(review: Dict[str, Any], org_name: str = "") -> str:
    ev = review["evidence"]
    lines = [
        f"Audit Package Review — {org_name or 'Organization'}",
        "",
        "This is a rule-based package quality check — NOT your SPRS score.",
        "",
        f"Package quality (heuristic): {review['review_score']}%",
        f"MET with file or Examine ref: {ev['with_evidence_count']}/{ev['met_count']}",
        f"MET missing proof: {ev['without_evidence_count']}",
        "",
        review.get("quality_explanation", ""),
        "",
    ]
    obj = review.get("objectives", {})
    if obj.get("total"):
        lines.append(f"Assessment objectives: {obj['met']}/{obj['total']} MET ({obj['pct']}%) — {obj['controls_with_objectives']} controls with objectives")
        lines.append("")
    lines.append("ISSUE SUMMARY")
    fs = review.get("finding_summary", {})
    if fs.get("met_no_proof_count"):
        lines.append(
            f"  - {fs['met_no_proof_count']} MET control(s) without file or Examine reference"
        )
    if fs.get("short_narrative_count"):
        lines.append(f"  - {fs['short_narrative_count']} MET control(s) with short narrative")
    if fs.get("gap_no_poam_count"):
        lines.append(f"  - {fs['gap_no_poam_count']} open gap(s) without POA&M notes")
    lines.extend(["", "DETAILED FINDINGS (sample)"])
    for f in review["findings"][:30]:
        lines.append(f"  [{f['severity'].upper()}] {f['title']}")
        lines.append(f"      {f['detail']}")
    lines.extend(["", "COMPLIANCE ROADMAP (top gaps)"])
    for row in review["roadmap"][:15]:
        lines.append(
            f"  - {row['control_id']} | -{row['score_impact']} pts | "
            f"{row['difficulty']} difficulty | {row['priority']} priority | {row['status']}"
        )
    return "\n".join(lines)


def assessment_changed_since_export(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    fingerprint_at_export: Optional[str],
) -> bool:
    if not fingerprint_at_export:
        return False
    return assessment_fingerprint(answers, scoped_controls) != fingerprint_at_export


def export_stamp_fields(
    answers: Dict[str, Any], scoped_controls: List[str]
) -> Dict[str, str]:
    from datetime import datetime

    return {
        "last_export_at": datetime.now().isoformat(timespec="seconds"),
        "assessment_fingerprint_at_export": assessment_fingerprint(answers, scoped_controls),
    }


def record_export_stamp(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    save_fn=None,
) -> None:
    """Persist export time + assessment fingerprint after SSP/POA&M build."""
    import streamlit as st

    fields = export_stamp_fields(answers, scoped_controls)
    st.session_state["last_export_at"] = fields["last_export_at"]
    st.session_state["assessment_fingerprint_at_export"] = fields[
        "assessment_fingerprint_at_export"
    ]
    if save_fn:
        save_fn()
