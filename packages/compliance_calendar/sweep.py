"""Compliance reminder sweep — in-app notifications for due calendar items.

Policy-review reminders are already produced by the notifications trigger
system (notifications.store.check_all_triggers), so the sweep covers only
the other calendar sources: evidence requests, expiring/stale evidence, and
risk reviews. Idempotent: title embeds the due date and unread
notifications are unique on (type, title).
"""

from __future__ import annotations

from typing import Any, Dict, List


def run_reminder_sweep(
    framework_id: str = "",
    window_days: int = 7,
    recipient: str = "admin",
) -> Dict[str, Any]:
    from .collect import collect_items

    data = collect_items(framework_id=framework_id, window_days=window_days)
    created = 0
    tried = 0
    errors: List[str] = []
    try:
        from notifications.store import create_notification, list_notifications

        existing = {
            (n.get("type", ""), n.get("title", ""))
            for n in list_notifications(recipient=recipient, unread_only=True, limit=500)
        }
        for item in data["items"]:
            title = f"{item['type'].replace('_', ' ').title()} {item['status']}: {item['title']} ({item['date']})"
            if ("compliance_reminder", title) in existing:
                continue
            tried += 1
            try:
                create_notification(
                    recipient=recipient,
                    type="compliance_reminder",
                    title=title,
                    body=f"{item['details']} — due {item['date']}.",
                    link=item.get("link") or "",
                    metadata={"calendar_item": item},
                )
                created += 1
            except Exception as exc:
                errors.append(str(exc))
    except Exception as exc:
        errors.append(str(exc))

    return {
        "created": created,
        "tried": tried,
        "due_count": len(data["items"]),
        "framework_id": framework_id,
        "window_days": window_days,
        "errors": errors,
    }
