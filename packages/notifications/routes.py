from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

router = APIRouter()


class MarkReadBody(BaseModel):
    notification_id: str = ""


@router.get("/api/notifications")
def get_notifications(
    recipient: Optional[str] = Query("admin"),
    unread_only: bool = Query(False),
    limit: int = Query(50),
):
    from .store import list_notifications, unread_count
    return {
        "notifications": list_notifications(recipient=recipient or "", unread_only=unread_only, limit=limit),
        "unread_count": unread_count(recipient=recipient or ""),
    }


@router.patch("/api/notifications/{notification_id}/read")
def mark_read(notification_id: str):
    from .store import mark_read
    if not mark_read(notification_id):
        raise HTTPException(404, "Notification not found")
    return {"status": "read"}


@router.patch("/api/notifications/read-all")
def mark_all_read(recipient: Optional[str] = Query("admin")):
    from .store import mark_all_read
    count = mark_all_read(recipient=recipient or "")
    return {"status": "ok", "marked_read": count}


@router.post("/api/notifications/check-triggers")
def check_triggers():
    from .store import check_all_triggers
    count = check_all_triggers()
    return {"new_notifications": count}
