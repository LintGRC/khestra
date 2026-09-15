"""Compliance calendar — shared FastAPI router."""

from __future__ import annotations

from fastapi import APIRouter, Query

router = APIRouter(tags=["compliance-calendar"])


@router.get("/api/compliance-calendar")
def get_compliance_calendar(
    framework_id: str = Query(""),
    window_days: int = Query(30),
):
    from .collect import collect_items

    return collect_items(framework_id=framework_id, window_days=window_days)


@router.get("/api/compliance-calendar/reminders")
def preview_reminders(
    framework_id: str = Query(""),
    window_days: int = Query(7),
):
    from .collect import collect_items

    data = collect_items(framework_id=framework_id, window_days=window_days)
    return {
        "window_days": data["window_days"],
        "due_count": len(data["items"]),
        "due": data["items"],
    }


@router.post("/api/compliance-calendar/reminders/run")
def run_reminders(
    framework_id: str = Query(""),
    window_days: int = Query(7),
):
    from .sweep import run_reminder_sweep

    return run_reminder_sweep(framework_id=framework_id, window_days=window_days)
