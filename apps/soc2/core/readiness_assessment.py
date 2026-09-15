"""SOC 2 readiness gap assessment — multi-dimensional scoring with PoF coverage."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from soc2_catalog import SOC2_CONTROLS
from policy_export import list_templates as _list_templates
from tsc_scoping import DEFAULT_SCOPE, get_in_scope_controls, get_in_scope_criteria_ids


COMPLETE = frozenset({"MET", "NOT APPLICABLE", "INHERITED"})
GAP = frozenset({"NOT MET", "NOT STARTED"})
ASSESSABLE = frozenset({"MET", "NOT MET", "NOT APPLICABLE", "IN PROGRESS", "PARTIALLY MET", "PLANNED"})

STALE_DAYS = 90

OE_PASS = "PASS"
TYPE_LABELS = {"type1": "Type I", "type2": "Type II"}


def _freshness_score(upload_date_str: Optional[str]) -> int:
    if not upload_date_str:
        return 0
    try:
        dt = datetime.strptime(upload_date_str.split(" ")[0], "%Y-%m-%d")
    except (ValueError, IndexError):
        return 0
    days = (datetime.now() - dt).days
    return 0 if days > STALE_DAYS else 1


def _evidence_quality_score(evidence: List[Dict[str, Any]]) -> int:
    """Score evidence quality 0-3 based on collector trust, review, and freshness."""
    if not evidence:
        return 0
    best = 0
    for e in evidence:
        score = 0
        if e.get("filename", "").startswith("collector_") or e.get("is_hub_evidence"):
            score += 1
        if e.get("review_status") == "approved":
            score += 1
        score += _freshness_score(e.get("upload_date") or e.get("uploaded_at", ""))
        best = max(best, score)
    return min(best, 3)


def _category_controls(category: str, controls: Optional[Dict[str, Any]] = None) -> List[str]:
    ref = controls if controls is not None else SOC2_CONTROLS
    return [cid for cid, m in ref.items() if m["category"] == category]


def _control_has_narrative(ans: Dict[str, Any]) -> bool:
    return bool((ans.get("implementation_narrative") or "").strip())


def _control_has_evidence(ans: Dict[str, Any]) -> bool:
    return len(ans.get("evidence") or []) > 0


def _control_has_owner(ans: Dict[str, Any]) -> bool:
    return bool((ans.get("owner") or "").strip())


def _control_has_target(ans: Dict[str, Any]) -> bool:
    return bool((ans.get("target_date") or "").strip())


def _pof_stats(ans: Dict[str, Any], cid: str) -> Dict[str, int]:
    catalog_pofs = SOC2_CONTROLS.get(cid, {}).get("points_of_focus", [])
    total = len(catalog_pofs)
    if total == 0:
        return {"pof_total": 0, "pof_addressed": 0, "pof_not_applicable": 0, "pof_applicable": 0, "pof_coverage_pct": 100}
    user_pofs = ans.get("points_of_focus") or {}
    addressed = sum(1 for p in catalog_pofs if user_pofs.get(p["id"], {}).get("status") == "addressed")
    not_applicable = sum(1 for p in catalog_pofs if user_pofs.get(p["id"], {}).get("status") == "not_applicable")
    applicable = total - not_applicable
    coverage_pct = round((addressed / applicable) * 100) if applicable > 0 else 100
    return {
        "pof_total": total,
        "pof_addressed": addressed,
        "pof_not_applicable": not_applicable,
        "pof_applicable": applicable,
        "pof_coverage_pct": coverage_pct,
    }


def _global_pof_stats(answers: Dict[str, Any], controls: Dict[str, Any]) -> Dict[str, int]:
    total = 0
    addressed = 0
    not_applicable = 0
    applicable = 0
    for cid, meta in controls.items():
        catalog_pofs = meta.get("points_of_focus", [])
        if not catalog_pofs:
            continue
        ans = answers.get(cid, {})
        user_pofs = ans.get("points_of_focus") or {}
        total += len(catalog_pofs)
        for p in catalog_pofs:
            status = user_pofs.get(p["id"], {}).get("status")
            if status == "addressed":
                addressed += 1
                applicable += 1
            elif status == "not_applicable":
                not_applicable += 1
            else:
                applicable += 1
    applicable_total = total - not_applicable
    coverage_pct = round((addressed / applicable_total) * 100) if applicable_total > 0 else 100
    return {
        "pof_total": total,
        "pof_addressed": addressed,
        "pof_not_applicable": not_applicable,
        "pof_applicable": applicable_total,
        "pof_coverage_pct": coverage_pct,
    }


def engagement_type(ws: Dict[str, Any]) -> str:
    return ((ws.get("soc2_engagement") or {}).get("type") or "").strip()


def operating_effectiveness_gaps(
    answers: Dict[str, Any],
    in_scope_controls: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """MET/INHERITED controls whose operating effectiveness is not PASS.

    Type I (design only) ignores this list. Type II requires OE tests before ready.
    Does not write operating_status — the human still scores.
    """
    gaps: List[Dict[str, Any]] = []
    for cid, meta in in_scope_controls.items():
        status = (answers.get(cid) or {}).get("status", "NOT STARTED")
        if status not in ("MET", "INHERITED"):
            continue
        oe = (answers.get(cid) or {}).get("operating_status") or "NOT TESTED"
        if oe != OE_PASS:
            gaps.append({
                "control_id": cid,
                "title": meta.get("title") or cid,
                "status": status,
                "operating_status": oe,
            })
    return gaps


def engagement_validation(ws: Dict[str, Any]) -> Dict[str, Any]:
    """How engagement type changes the ready bar (TSC Type I vs Type II)."""
    eng = ws.get("soc2_engagement") or {}
    etype = (eng.get("type") or "").strip()
    answers = ws.get("answers") or {}
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    in_scope = get_in_scope_controls(scope)
    oe_gaps = operating_effectiveness_gaps(answers, in_scope)
    period_ok = bool((eng.get("engagement_start") or "").strip() and (eng.get("engagement_end") or "").strip())
    type2 = etype == "type2"
    return {
        "type": etype,
        "type_label": TYPE_LABELS.get(etype) or (etype or "unset"),
        "period_ok": period_ok,
        "oe_gaps": oe_gaps,
        "oe_gap_count": len(oe_gaps),
        "oe_required": type2,
        "period_required": type2,
        "design_only": etype == "type1",
    }


def run_readiness_assessment(ws: Dict[str, Any], test_pass_rate: float = 0.0, test_total: int = 0) -> Dict[str, Any]:
    """Multi-dimensional readiness assessment for SOC 2 with PoF coverage."""

    answers = ws.get("answers") or {}
    policies = ws.get("policies") or []
    exceptions = ws.get("exceptions") or []
    org_profile = ws.get("org_profile") or {}
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    in_scope_controls = get_in_scope_controls(scope)
    eng_v = engagement_validation(ws)

    profile_fields = [
        "org_name", "system_name", "system_description", "architecture_summary",
        "boundary_description", "system_owner", "compliance_officer", "it_admin",
    ]
    profile_filled = sum(1 for f in profile_fields if (org_profile.get(f) or "").strip())
    profile_score = round((profile_filled / len(profile_fields)) * 100) if profile_fields else 0

    controls_met = 0
    controls_assessed = 0
    controls_with_narrative = 0
    controls_with_evidence = 0
    controls_with_quality_evidence = 0
    controls_with_owner = 0
    controls_with_target = 0
    open_gaps: List[Dict[str, Any]] = []
    missing_evidence: List[Dict[str, Any]] = []
    missing_narrative: List[Dict[str, Any]] = []
    stale_controls: List[Dict[str, Any]] = []

    for cid, meta in in_scope_controls.items():
        ans = answers.get(cid, {})
        status = ans.get("status", "NOT STARTED")
        evidence = ans.get("evidence") or []

        if status in COMPLETE:
            controls_met += 1
        if status in ASSESSABLE:
            controls_assessed += 1
        if _control_has_narrative(ans):
            controls_with_narrative += 1
        if _control_has_evidence(ans):
            controls_with_evidence += 1
        if _evidence_quality_score(evidence) >= 2:
            controls_with_quality_evidence += 1
        if _control_has_owner(ans):
            controls_with_owner += 1
        if _control_has_target(ans):
            controls_with_target += 1

        if status in GAP:
            open_gaps.append({
                "control_id": cid,
                "category": meta["category"],
                "name": meta["title"],
                "status": status,
                "has_narrative": _control_has_narrative(ans),
                "has_evidence": _control_has_evidence(ans),
                "owner": ans.get("owner", ""),
                "target_date": ans.get("target_date", ""),
            })

        if status in COMPLETE and not _control_has_evidence(ans):
            missing_evidence.append({
                "control_id": cid,
                "category": meta["category"],
                "name": meta["title"],
                "status": status,
            })

        if status in COMPLETE and not _control_has_narrative(ans):
            missing_narrative.append({
                "control_id": cid,
                "category": meta["category"],
                "name": meta["title"],
                "status": status,
            })

    total = len(in_scope_controls)
    readiness_pct = round((controls_met / total) * 100) if total else 0
    narrative_coverage_pct = round((controls_with_narrative / total) * 100) if total else 0
    evidence_coverage_pct = round((controls_with_evidence / total) * 100) if total else 0
    quality_evidence_pct = round((controls_with_quality_evidence / total) * 100) if total else 0
    assessment_pct = round((controls_assessed / total) * 100) if total else 0

    pof = _global_pof_stats(answers, in_scope_controls)

    categories = sorted({m["category"] for m in in_scope_controls.values()})
    category_readiness: List[Dict[str, Any]] = []
    for cat in categories:
        cat_ids = _category_controls(cat, in_scope_controls)
        cat_met = sum(1 for cid in cat_ids if answers.get(cid, {}).get("status", "NOT STARTED") in COMPLETE)
        cat_total = len(cat_ids)
        cat_pof_total = 0
        cat_pof_addressed = 0
        cat_pof_na = 0
        for cid in cat_ids:
            s = _pof_stats(answers.get(cid, {}), cid)
            cat_pof_total += s["pof_total"]
            cat_pof_addressed += s["pof_addressed"]
            cat_pof_na += s["pof_not_applicable"]
        cat_pof_applicable = cat_pof_total - cat_pof_na
        cat_pof_pct = round((cat_pof_addressed / cat_pof_applicable) * 100) if cat_pof_applicable > 0 else 100
        category_readiness.append({
            "category": cat,
            "total": cat_total,
            "met": cat_met,
            "gap": cat_total - cat_met,
            "readiness_pct": round((cat_met / cat_total) * 100) if cat_total else 0,
            "pof_total": cat_pof_total,
            "pof_addressed": cat_pof_addressed,
            "pof_not_applicable": cat_pof_na,
            "pof_coverage_pct": cat_pof_pct,
        })

    policy_mapped_controls = set()
    for p in policies:
        for cid in p.get("mapped_controls") or []:
            policy_mapped_controls.add(cid)
    policy_coverage_pct = round((len(policy_mapped_controls) / len(in_scope_controls)) * 100) if len(in_scope_controls) else 0

    open_exceptions = [e for e in exceptions if e.get("status") in ("pending_approval", "approved")]

    weights = {"assessment": 0.25, "evidence": 0.20, "pof": 0.15, "narrative": 0.15, "policy": 0.10, "tests": 0.15}
    if test_total == 0:
        weights["tests"] = 0.0
        redistribute = 0.15 / sum(1 for k in weights if weights[k] > 0)
        for k in weights:
            if weights[k] > 0:
                weights[k] += redistribute
    composite_score = round(
        assessment_pct * weights["assessment"]
        + quality_evidence_pct * weights["evidence"]
        + pof["pof_coverage_pct"] * weights["pof"]
        + narrative_coverage_pct * weights["narrative"]
        + policy_coverage_pct * weights["policy"]
        + test_pass_rate * weights["tests"]
    )

    checklist = [
        {
            "key": "profile",
            "label": "Organization profile complete",
            "done": profile_score >= 75,
            "detail": f"{profile_score}% of key fields populated",
            "required": True,
        },
        {
            "key": "assessment",
            "label": "All controls assessed",
            "done": assessment_pct >= 90,
            "detail": f"{controls_assessed}/{total} controls assessed ({assessment_pct}%)",
            "required": True,
        },
        {
            "key": "gaps",
            "label": "No open gaps (NOT MET / NOT STARTED)",
            "done": len(open_gaps) == 0,
            "detail": f"{len(open_gaps)} open gaps remain",
            "required": True,
        },
        {
            "key": "evidence",
            "label": "Quality evidence (collector/reviewed/fresh) for assessed controls",
            "done": quality_evidence_pct >= 50,
            "detail": f"{quality_evidence_pct}% quality evidence coverage ({controls_with_quality_evidence}/{total})",
            "required": True,
        },
        {
            "key": "pof_coverage",
            "label": "Points of Focus coverage > 80%",
            "done": pof["pof_coverage_pct"] >= 80,
            "detail": f"{pof['pof_coverage_pct']}% PoF coverage ({pof['pof_addressed']}/{pof['pof_applicable']} addressed)",
            "required": False,
        },
        {
            "key": "narrative",
            "label": "Implementation narratives documented",
            "done": narrative_coverage_pct >= 80,
            "detail": f"{narrative_coverage_pct}% narrative coverage",
            "required": False,
        },
        {
            "key": "policy",
            "label": "Policies mapped to controls",
            "done": policy_coverage_pct >= 50,
            "detail": f"{policy_coverage_pct}% policy coverage ({len(policies)} policies)",
            "required": False,
        },
        {
            "key": "owner",
            "label": "All controls have an owner",
            "done": controls_with_owner >= total * 0.8,
            "detail": f"{controls_with_owner}/{total} controls assigned",
            "required": False,
        },
        {
            "key": "tests",
            "label": "Tests of controls passing (operating effectiveness)",
            "done": test_pass_rate >= 80 if test_total else not eng_v["oe_required"],
            "detail": (
                f"{test_pass_rate}% test pass rate"
                if test_total else
                ("Not required for Type I (design only)" if eng_v["design_only"]
                 else "No control-test runs recorded")
            ),
            "required": False,
        },
        {
            "key": "engagement_type",
            "label": "SOC 2 engagement type selected (Type I or Type II)",
            "done": bool(eng_v["type"]),
            "detail": f"Current: {eng_v['type_label']}",
            "required": True,
        },
        {
            "key": "type2_period",
            "label": "Type II engagement window (start → end)",
            "done": (not eng_v["period_required"]) or eng_v["period_ok"],
            "detail": (
                "Not required for Type I (point in time)"
                if eng_v["design_only"]
                else ("Period recorded" if eng_v["period_ok"] else "Set engagement start and end dates")
            ),
            "required": eng_v["period_required"],
        },
        {
            "key": "operating_effectiveness",
            "label": "Operating effectiveness PASS on MET controls",
            "done": (not eng_v["oe_required"]) or eng_v["oe_gap_count"] == 0,
            "detail": (
                "Not required for Type I (design / point-in-time)"
                if not eng_v["oe_required"]
                else (
                    f"{eng_v['oe_gap_count']} MET control(s) missing OE PASS"
                    if eng_v["oe_gap_count"]
                    else "All MET controls have OE PASS"
                )
            ),
            "required": eng_v["oe_required"],
        },
    ]

    checklist_done = sum(1 for c in checklist if c["done"])
    required_blocks = [c for c in checklist if c["required"] and not c["done"]]
    blockers = [f"{c['label']}: {c['detail']}" for c in required_blocks]

    gap_count = len(open_gaps)
    if gap_count == 0:
        effort = "Audit-ready"
    elif gap_count <= 5:
        effort = "Near ready — small remediation effort"
    elif gap_count <= 15:
        effort = "Moderate — plan 2-4 weeks for remediation"
    elif gap_count <= 30:
        effort = "Significant — plan 1-2 months"
    else:
        effort = "Major effort — plan 2+ months"

    return {
        "readiness_pct": readiness_pct,
        "composite_score": composite_score,
        "controls_total": total,
        "controls_met": controls_met,
        "controls_assessed": controls_assessed,
        "open_gaps": open_gaps,
        "gap_count": gap_count,
        "missing_evidence": missing_evidence,
        "missing_evidence_count": len(missing_evidence),
        "missing_narrative": missing_narrative,
        "missing_narrative_count": len(missing_narrative),
        "category_readiness": category_readiness,
        "profile_score": profile_score,
        "evidence_coverage_pct": evidence_coverage_pct,
        "quality_evidence_pct": quality_evidence_pct,
        "controls_with_quality_evidence": controls_with_quality_evidence,
        "narrative_coverage_pct": narrative_coverage_pct,
        "assessment_pct": assessment_pct,
        "policy_coverage_pct": policy_coverage_pct,
        "policy_mapped_count": len(policy_mapped_controls),
        "open_exceptions_count": len(open_exceptions),
        "pof": pof,
        "checklist": checklist,
        "checklist_done": checklist_done,
        "checklist_total": len(checklist),
        "blockers": blockers,
        "effort": effort,
        "audit_ready": checklist_done >= 6 and len(blockers) == 0,
        "test_pass_rate": test_pass_rate,
        "engagement_validation": eng_v,
    }
