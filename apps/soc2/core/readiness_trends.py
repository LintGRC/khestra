"""Readiness trend tracking — snapshots on audit period freeze."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def snapshot_readiness(ws: Dict[str, Any], event: str = "period_freeze") -> Dict[str, Any]:
    """Take a readiness snapshot and append it to the workspace."""
    from readiness_assessment import run_readiness_assessment
    from soc2_catalog import get_points_of_focus

    try:
        assessment = run_readiness_assessment(ws)
    except Exception:
        assessment = {}

    pof_total = 0
    pof_addressed = 0
    pof_applicable = 0
    for cid in list(ws.get("answers") or {}):
        ans = ws["answers"][cid]
        for pof in get_points_of_focus(cid):
            pof_total += 1
            st = (ans.get("points_of_focus") or {}).get(pof["id"], {})
            st_val = st.get("status", "not_applicable")
            if st_val != "not_applicable":
                pof_applicable += 1
            if st_val == "addressed":
                pof_addressed += 1

    snapshot = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "readiness_pct": assessment.get("readiness_pct", 0),
        "composite_score": assessment.get("composite_score", 0),
        "evidence_coverage_pct": assessment.get("evidence_coverage_pct", 0),
        "quality_evidence_pct": assessment.get("quality_evidence_pct", 0),
        "gap_count": assessment.get("gap_count", 0),
        "controls_total": assessment.get("controls_total", 0),
        "controls_met": assessment.get("controls_met", 0),
        "pof_total": pof_total,
        "pof_addressed": pof_addressed,
        "pof_applicable": pof_applicable,
        "pof_coverage_pct": round(pof_addressed / max(pof_applicable, 1) * 100, 1),
    }

    trends = ws.get("readiness_trends") or []
    trends.append(snapshot)
    ws["readiness_trends"] = trends
    return snapshot


def get_readiness_trends(ws: Dict[str, Any]) -> Dict[str, Any]:
    """Return readiness trend data for the dashboard chart."""
    trends = ws.get("readiness_trends") or []
    return {
        "trends": trends,
        "latest": trends[-1] if trends else None,
        "count": len(trends),
        "improvement": (
            round(trends[-1]["readiness_pct"] - trends[0]["readiness_pct"], 1)
            if len(trends) >= 2 else 0
        ),
    }
