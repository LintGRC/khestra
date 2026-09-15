"""My Work — aggregated work items for the current user."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from soc2_catalog import SOC2_CONTROLS
from tsc_scoping import DEFAULT_SCOPE, get_in_scope_controls, get_in_scope_criteria_ids


def _parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def _days_until(date_str: str) -> int | None:
    d = _parse_date(date_str)
    if not d:
        return None
    return (d - datetime.now()).days


def get_my_work(ws: Dict[str, Any], user_name: str) -> Dict[str, Any]:
    """Build a personalized work queue for the given user."""
    answers = ws.get("answers") or {}
    exceptions = ws.get("exceptions") or []
    evidence_requests = ws.get("evidence_requests") or []
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    in_scope = get_in_scope_controls(scope)
    now = datetime.now()

    assigned_controls: List[Dict[str, Any]] = []
    due_soon: List[Dict[str, Any]] = []
    overdue: List[Dict[str, Any]] = []
    missing_evidence: List[Dict[str, Any]] = []
    needs_review: List[Dict[str, Any]] = []
    pending_exceptions: List[Dict[str, Any]] = []

    for cid, meta in in_scope.items():
        ans = answers.get(cid, {})
        owner = (ans.get("owner") or "").strip()
        target_date = (ans.get("target_date") or "").strip()
        status = ans.get("status", "NOT STARTED")
        evidence = ans.get("evidence") or []

        # Assigned to me
        if owner and owner.lower() == user_name.lower():
            item = {
                "control_id": cid,
                "category": meta["category"],
                "name": meta["title"],
                "status": status,
                "target_date": target_date,
                "evidence_count": len(evidence),
            }
            assigned_controls.append(item)

            # Due soon (within 7 days)
            days = _days_until(target_date) if target_date else None
            if days is not None and 0 <= days <= 7:
                due_soon.append({**item, "days_left": days})

            # Overdue
            if days is not None and days < 0:
                overdue.append({**item, "days_overdue": abs(days)})

        # Missing evidence (MET but no evidence)
        if status in ("MET", "NOT APPLICABLE", "INHERITED") and not evidence:
            missing_evidence.append({
                "control_id": cid,
                "category": meta["category"],
                "name": meta["title"],
                "status": status,
                "owner": owner,
            })

        # Evidence needs review
        for ev in evidence:
            if ev.get("review_status") == "pending":
                needs_review.append({
                    "control_id": cid,
                    "filename": ev.get("filename", ""),
                    "upload_date": ev.get("upload_date", ""),
                    "source": ev.get("source", "manual"),
                })

    # Pending evidence requests assigned to me
    for req in evidence_requests:
        if req.get("status") == "open":
            assigned_to = (req.get("assigned_to") or "").strip()
            if not assigned_to or assigned_to.lower() == user_name.lower():
                pending_exceptions.append({
                    "request_id": req["id"],
                    "control_id": req.get("control_id", ""),
                    "title": req.get("title", ""),
                    "due_date": req.get("due_date", ""),
                    "created_at": req.get("created_at", ""),
                })

    # Pending exceptions needing approval
    pending_approval = [
        e for e in exceptions if e.get("status") == "pending_approval"
    ]

    return {
        "assigned_controls": assigned_controls,
        "assigned_count": len(assigned_controls),
        "due_soon": due_soon,
        "due_soon_count": len(due_soon),
        "overdue": overdue,
        "overdue_count": len(overdue),
        "missing_evidence": missing_evidence,
        "missing_evidence_count": len(missing_evidence),
        "needs_review": needs_review,
        "needs_review_count": len(needs_review),
        "pending_requests": pending_exceptions,
        "pending_requests_count": len(pending_exceptions),
        "pending_approval": pending_approval,
        "pending_approval_count": len(pending_approval),
    }
