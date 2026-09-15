"""Policy review reminders — identifies policies that need review."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List


def get_policies_due_review(policy_ids: List[str] | None = None) -> List[Dict[str, Any]]:
    """Return policies that are approaching or past their review date."""
    from .store import list_documents, get_document

    docs = list_documents() if policy_ids is None else []
    if policy_ids:
        for pid in policy_ids:
            d = get_document(pid)
            if d:
                docs.append(d)

    now = datetime.now()
    results: List[Dict[str, Any]] = []
    for doc in docs:
        status = doc.get("status", "draft")

        # Use next_review_date if available, fall back to updated_at
        review_date_str = doc.get("next_review_date", "") or doc.get("updated_at", "")
        try:
            review_date = datetime.strptime(review_date_str.split(".")[0].split("T")[0], "%Y-%m-%d")
        except (ValueError, IndexError):
            continue

        days_until_review = (review_date - now.date()).days if hasattr(now, 'date') else (review_date - now).days
        # For updated_at fallback, calculate days_since_update
        updated_str = doc.get("updated_at", "")
        days_since_update = 0
        try:
            updated = datetime.strptime(updated_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            days_since_update = (now - updated).days
        except (ValueError, IndexError):
            pass

        cadence = int(doc.get("review_cadence_days", 365))

        if doc.get("next_review_date"):
            # Using explicit next_review_date
            if status == "published" and days_until_review < 0:
                results.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "status": status,
                    "days_since_update": days_since_update,
                    "days_remaining": 0,
                    "urgency": "overdue",
                    "next_review_date": doc.get("next_review_date", ""),
                })
            elif status == "published" and days_until_review <= 30:
                results.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "status": status,
                    "days_since_update": days_since_update,
                    "days_remaining": max(0, days_until_review),
                    "urgency": "upcoming",
                    "next_review_date": doc.get("next_review_date", ""),
                })
        else:
            # Fallback to updated_at-based calculation
            try:
                updated = datetime.strptime(updated_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            except (ValueError, IndexError):
                continue
            days_since = (now - updated).days

            if status == "published" and days_since >= cadence:
                results.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "status": status,
                    "days_since_update": days_since,
                    "days_remaining": 0,
                    "urgency": "overdue",
                })
            elif status == "published" and days_since >= (cadence - 30):
                results.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "status": status,
                    "days_since_update": days_since,
                    "days_remaining": cadence - days_since,
                    "urgency": "upcoming",
                })

        # Stale review check (applies regardless of date source)
        if status == "under_review" and days_since_update >= 30:
            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "status": status,
                "days_since_update": days_since_update,
                "days_remaining": 0,
                "urgency": "stale_review",
            })

    return results
