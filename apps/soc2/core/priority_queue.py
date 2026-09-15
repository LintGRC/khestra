"""Priority queue — intelligently sort controls by impact and effort."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from soc2_catalog import SOC2_CONTROLS
from tsc_scoping import DEFAULT_SCOPE, get_in_scope_controls


def _days_until(date_str: str) -> int | None:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            d = datetime.strptime(date_str, fmt)
            return (d - datetime.now()).days
        except ValueError:
            continue
    return None


def _control_priority_score(
    cid: str,
    ans: Dict[str, Any],
    risks: List[Dict[str, Any]],
    exceptions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate a priority score for a control. Lower = work on first."""
    status = ans.get("status", "NOT STARTED")
    owner = (ans.get("owner") or "").strip()
    target_date = (ans.get("target_date") or "").strip()
    narrative = (ans.get("implementation_narrative") or "").strip()
    evidence = ans.get("evidence") or []
    comments = ans.get("comments") or []

    score = 50  # baseline
    reasons: List[str] = []
    priority_tier = "normal"

    # ── Risk signals (highest priority) ───────────────────────
    for exc in exceptions:
        if exc.get("control_id") == cid and exc.get("status") in ("pending_approval", "approved"):
            risk = exc.get("risk_level", "medium")
            if risk == "critical":
                score -= 30
                reasons.append("Critical exception active")
                priority_tier = "risk"
            elif risk == "high":
                score -= 20
                reasons.append("High-risk exception active")
                priority_tier = "risk"

    for risk in risks:
        if cid in (risk.get("controls") or ""):
            if risk.get("residual_level") == "critical":
                score -= 25
                reasons.append("Critical risk linked")
                priority_tier = "risk"
            elif risk.get("residual_level") == "high":
                score -= 15
                reasons.append("High risk linked")

    # ── Deadline signals ──────────────────────────────────────
    days = _days_until(target_date) if target_date else None
    if days is not None:
        if days < 0:
            score -= 25
            reasons.append(f"Overdue by {abs(days)} days")
            priority_tier = "urgent"
        elif days <= 3:
            score -= 15
            reasons.append(f"Due in {days} day(s)")
            if priority_tier == "normal":
                priority_tier = "urgent"
        elif days <= 7:
            score -= 8
            reasons.append(f"Due in {days} days")

    # ── Effort signals (fastest wins) ─────────────────────────
    if status in ("NOT STARTED",):
        has_narrative = bool(narrative)
        has_evidence = len(evidence) > 0
        has_owner = bool(owner)

        if has_narrative and has_evidence:
            score -= 12
            reasons.append("Just needs status update")
            if priority_tier == "normal":
                priority_tier = "fast"
        elif has_narrative or has_evidence:
            score -= 6
            reasons.append("Partially documented")

    # ── Blocked signals ───────────────────────────────────────
    if status in ("MET", "NOT APPLICABLE", "INHERITED") and not evidence:
        score += 10
        reasons.append("MET but no evidence")
        priority_tier = "blocked"

    if status in ("NOT STARTED",) and not owner:
        score += 5
        reasons.append("No owner assigned")

    # ── Collaboration signals ─────────────────────────────────
    for c in comments:
        text = (c.get("text") or "").lower()
        if any(w in text for w in ["blocked", "waiting", "need", "help"]):
            score -= 5
            reasons.append("Has blocking comment")
            break

    return {
        "control_id": cid,
        "category": SOC2_CONTROLS[cid]["category"],
        "name": SOC2_CONTROLS[cid]["title"],
        "status": status,
        "owner": owner,
        "target_date": target_date,
        "evidence_count": len(evidence),
        "narrative": bool(narrative),
        "score": max(0, score),
        "tier": priority_tier,
        "reasons": reasons[:3],
    }


def get_priority_queue(
    answers: Dict[str, Any],
    risks: List[Dict[str, Any]],
    exceptions: List[Dict[str, Any]],
    scope: Optional[Dict[str, bool]] = None,
    limit: int = 30,
) -> Dict[str, Any]:
    """Return controls sorted by priority."""

    in_scope = get_in_scope_controls(scope or DEFAULT_SCOPE)
    items: List[Dict[str, Any]] = []
    for cid in in_scope:
        ans = answers.get(cid, {})
        status = ans.get("status", "NOT STARTED")
        if status in ("MET", "NOT APPLICABLE", "INHERITED"):
            continue  # skip completed controls
        item = _control_priority_score(cid, ans, risks, exceptions)
        items.append(item)

    items.sort(key=lambda x: x["score"])

    tiers = {
        "risk": [i for i in items if i["tier"] == "risk"],
        "urgent": [i for i in items if i["tier"] == "urgent"],
        "fast": [i for i in items if i["tier"] == "fast"],
        "blocked": [i for i in items if i["tier"] == "blocked"],
        "normal": [i for i in items if i["tier"] == "normal"],
    }

    return {
        "items": items[:limit],
        "total": len(items),
        "tiers": {
            "risk": tiers["risk"][:10],
            "urgent": tiers["urgent"][:10],
            "fast": tiers["fast"][:10],
            "blocked": tiers["blocked"][:10],
        },
        "tier_counts": {
            "risk": len(tiers["risk"]),
            "urgent": len(tiers["urgent"]),
            "fast": len(tiers["fast"]),
            "blocked": len(tiers["blocked"]),
            "normal": len(tiers["normal"]),
        },
    }
