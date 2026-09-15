"""SOC 2 readiness metrics."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from soc2_catalog import SOC2_CONTROLS
from workspace_service import policy_coverage
from tsc_scoping import DEFAULT_SCOPE, get_in_scope_controls

COMPLETE = frozenset({"MET", "NOT APPLICABLE", "INHERITED"})
GAP = frozenset({"NOT MET", "NOT STARTED"})

STALE_DAYS = 90
EXPIRED_DAYS = 180


def _freshness_score(upload_date_str: Optional[str]) -> str:
    if not upload_date_str:
        return "never"
    try:
        dt = datetime.strptime(upload_date_str.split(" ")[0], "%Y-%m-%d")
    except (ValueError, IndexError):
        return "unknown"
    days = (datetime.now() - dt).days
    if days <= STALE_DAYS:
        return "fresh"
    if days <= EXPIRED_DAYS:
        return "stale"
    return "expired"


def _evidence_quality_score(evidence: List[Dict[str, Any]]) -> int:
    """Score evidence quality 0-3: +1 collector, +1 reviewed, +1 fresh."""
    if not evidence:
        return 0
    best = 0
    for e in evidence:
        score = 0
        if e.get("filename", "").startswith("collector_") or e.get("is_hub_evidence"):
            score += 1
        if e.get("review_status") == "approved":
            score += 1
        upload = e.get("upload_date") or e.get("uploaded_at", "")
        try:
            dt = datetime.strptime(upload.split(" ")[0], "%Y-%m-%d")
            if (datetime.now() - dt).days <= STALE_DAYS:
                score += 1
        except (ValueError, IndexError):
            pass
        best = max(best, score)
    return min(best, 3)


def compute_dashboard(ws: Dict[str, Any]) -> Dict[str, Any]:
    answers = ws.get("answers") or {}
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    in_scope_controls = get_in_scope_controls(scope)
    total = len(in_scope_controls)
    met = 0
    assessed = 0
    gaps = 0
    with_evidence = 0
    with_auto_evidence = 0
    with_quality_evidence = 0
    coverage: List[Dict[str, Any]] = []
    freshness_counts: Dict[str, int] = {"fresh": 0, "stale": 0, "expired": 0, "never": 0, "unknown": 0}
    category_totals: Dict[str, int] = {}
    category_met: Dict[str, int] = {}

    pof_total_all = 0
    pof_addressed_all = 0
    pof_not_applicable_all = 0

    for cid in in_scope_controls:
        meta = in_scope_controls[cid]
        cat = meta["category"]
        category_totals[cat] = category_totals.get(cat, 0) + 1
        ans = answers.get(cid) or {}
        status = (ans.get("status") or "NOT STARTED").upper()
        if status in COMPLETE:
            met += 1
            assessed += 1
            category_met[cat] = category_met.get(cat, 0) + 1
        elif status not in GAP:
            assessed += 1
        if status in GAP:
            gaps += 1
        evidence = ans.get("evidence") or []
        has_any = len(evidence) > 0
        has_auto = any(e.get("filename", "").startswith("collector_") for e in evidence)
        if has_any:
            with_evidence += 1
        if has_auto:
            with_auto_evidence += 1
        if _evidence_quality_score(evidence) >= 2:
            with_quality_evidence += 1
        last_date = max((e.get("upload_date") or "") for e in evidence) if evidence else None
        freshness = _freshness_score(last_date) if evidence else "never"
        freshness_counts[freshness] = freshness_counts.get(freshness, 0) + 1
        coverage.append({
            "id": cid,
            "category": cat,
            "status": status,
            "has_evidence": has_any,
            "has_auto_evidence": has_auto,
            "evidence_count": len(evidence),
            "freshness": freshness,
            "last_evidence_date": last_date,
        })

        catalog_pofs = meta.get("points_of_focus", [])
        user_pofs = ans.get("points_of_focus") or {}
        for p in catalog_pofs:
            pof_total_all += 1
            st = user_pofs.get(p["id"], {}).get("status")
            if st == "addressed":
                pof_addressed_all += 1
            elif st == "not_applicable":
                pof_not_applicable_all += 1

    readiness_pct = round((met / total) * 100) if total else 0
    evidence_pct = round((with_evidence / total) * 100) if total else 0
    auto_pct = round((with_auto_evidence / total) * 100) if total else 0
    quality_evidence_pct = round((with_quality_evidence / total) * 100) if total else 0

    category_readiness = []
    for cat in sorted(category_totals.keys()):
        cat_total = category_totals[cat]
        cat_met = category_met.get(cat, 0)
        category_readiness.append({
            "category": cat,
            "total": cat_total,
            "met": cat_met,
            "readiness_pct": round((cat_met / cat_total) * 100) if cat_total else 0,
        })

    exceptions = ws.get("exceptions") or []
    open_exceptions = [e for e in exceptions if e.get("status") in ("pending_approval", "approved")]
    expired_exceptions = [e for e in exceptions if e.get("status") == "approved" and e.get("expiry_date") and e["expiry_date"] < datetime.now().strftime("%Y-%m-%d")]

    risks = ws.get("risks") or []
    active_risks = [r for r in risks if r.get("status") not in ("closed",)]
    critical_risks = [r for r in active_risks if r.get("residual_level") == "critical"]
    high_risks = [r for r in active_risks if r.get("residual_level") == "high"]

    pk_coverage = policy_coverage(ws)

    pof_applicable = pof_total_all - pof_not_applicable_all
    pof_coverage_pct = round((pof_addressed_all / pof_applicable) * 100) if pof_applicable > 0 else 100

    findings = ws.get("findings") or []
    open_findings = [f for f in findings if f.get("status") == "open"]
    material_findings = [f for f in open_findings if f.get("severity") in ("major", "material")]

    active_incidents_by_control: Dict[str, int] = {}
    try:
        from incident_impact import get_active_incidents_by_control
        active_incidents_by_control = get_active_incidents_by_control()
    except Exception:
        pass
    controls_with_incidents = len(active_incidents_by_control)
    total_incidents = sum(active_incidents_by_control.values())

    # Enrich coverage entries with incident counts
    for c in coverage:
        c["active_incidents"] = active_incidents_by_control.get(c["id"], 0)

    return {
        "client_id": ws.get("client_id", "default"),
        "org_name": ws.get("org_name", "Your Organization"),
        "readiness_pct": readiness_pct,
        "evidence_coverage_pct": evidence_pct,
        "quality_evidence_pct": quality_evidence_pct,
        "auto_coverage_pct": auto_pct,
        "controls_met": met,
        "controls_total": total,
        "controls_assessed": assessed,
        "open_gaps": gaps,
        "open_exceptions": len(open_exceptions),
        "expired_exceptions": len(expired_exceptions),
        "active_risks": len(active_risks),
        "critical_risks": len(critical_risks),
        "high_risks": len(high_risks),
        "open_findings": len(open_findings),
        "material_findings": len(material_findings),
        "active_incidents_by_control": active_incidents_by_control,
        "controls_with_incidents": controls_with_incidents,
        "total_incidents": total_incidents,
        "policy_coverage": pk_coverage,
        "coverage": coverage,
        "category_readiness": category_readiness,
        "freshness": freshness_counts,
        "pof_total": pof_total_all,
        "pof_addressed": pof_addressed_all,
        "pof_not_applicable": pof_not_applicable_all,
        "pof_applicable": pof_applicable,
        "pof_coverage_pct": pof_coverage_pct,
        "is_demo": bool(ws.get("is_demo")),
        "demo_id": ws.get("demo_id"),
        "scoping_completed": bool(ws.get("scoping_completed")),
    }
