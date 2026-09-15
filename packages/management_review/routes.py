"""Management review routes — /api/management-reviews (ISO 27001 clause 9.3)."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import store

router = APIRouter()


class Attendee(BaseModel):
    name: str = ""
    role: str = ""


class ReviewInput(BaseModel):
    key: str = ""
    label: str = ""
    reviewed: bool = False
    note: str = ""


class ReviewOutput(BaseModel):
    decision: str = ""
    category: str = "other"
    owner: str = ""
    target_date: str = ""


class ActionItem(BaseModel):
    description: str = ""
    owner: str = ""
    target_date: str = ""
    status: str = "open"


class ReviewCreate(BaseModel):
    title: str = ""
    date: str = ""
    status: str = "scheduled"
    attendees: list[Attendee] = []
    inputs: list[ReviewInput] = []
    outputs: list[ReviewOutput] = []
    action_items: list[ActionItem] = []
    minutes: str = ""


class ReviewUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    status: Optional[str] = None
    attendees: Optional[list[Attendee]] = None
    inputs: Optional[list[ReviewInput]] = None
    outputs: Optional[list[ReviewOutput]] = None
    action_items: Optional[list[ActionItem]] = None
    minutes: Optional[str] = None


def _models(d: BaseModel) -> list[dict]:
    return [x.model_dump() for x in d]


@router.get("/api/management-reviews")
def list_reviews(status: Optional[str] = None):
    records = store.list_reviews(status)
    return {"records": records}


@router.get("/api/management-reviews/stats")
def review_stats():
    return store.stats()


@router.get("/api/management-reviews/inputs")
def review_inputs():
    return {"inputs": [{"key": k, "label": label} for k, label in store.DEFAULT_INPUTS],
            "output_categories": store.OUTPUT_CATEGORIES}


@router.get("/api/management-reviews/{rid}")
def get_review(rid: str):
    record = store.get_review(rid)
    if not record:
        raise HTTPException(status_code=404, detail="Management review not found")
    return {"record": record}


@router.post("/api/management-reviews")
def create_review(body: ReviewCreate):
    return {"record": store.create_review(
        title=body.title,
        date=body.date,
        status=body.status,
        attendees=_models(body.attendees),
        inputs=_models(body.inputs),
        outputs=_models(body.outputs),
        action_items=_models(body.action_items),
        minutes=body.minutes,
    )}


@router.patch("/api/management-reviews/{rid}")
def update_review(rid: str, body: ReviewUpdate):
    # model_dump() already converts nested models to dicts
    payload = body.model_dump(exclude_none=True)
    record = store.update_review(rid, **payload)
    if not record:
        raise HTTPException(status_code=404, detail="Management review not found")
    return {"record": record}


@router.delete("/api/management-reviews/{rid}")
def delete_review(rid: str):
    if not store.delete_review(rid):
        raise HTTPException(status_code=404, detail="Management review not found")
    return {"ok": True}
