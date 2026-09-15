"""Vendor SOC report review reminders — identifies vendors with upcoming/overdue reviews."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List


def get_vendors_due_review() -> List[Dict[str, Any]]:
    """Return vendors whose next_review_due is past or within 30 days."""
    from .store import list_vendors

    vendors = list_vendors()
    now = datetime.now()
    results: List[Dict[str, Any]] = []

    for v in vendors:
        due_str = v.get("next_review_due", "") or ""
        if not due_str:
            continue
        try:
            due = datetime.strptime(due_str[:10], "%Y-%m-%d")
        except (ValueError, IndexError):
            continue

        days = (due - now).days
        if days < 0:
            results.append({
                "id": v["id"],
                "name": v.get("name", ""),
                "days_overdue": abs(days),
                "next_review_due": due_str,
                "urgency": "overdue",
            })
        elif days <= 30:
            results.append({
                "id": v["id"],
                "name": v.get("name", ""),
                "days_remaining": days,
                "next_review_due": due_str,
                "urgency": "upcoming",
            })

    results.sort(key=lambda r: r.get("days_overdue", r.get("days_remaining", 0)))
    return results
