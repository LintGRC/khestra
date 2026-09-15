"""Reviews API routes — polymorphic review object for access, vendor, policy, BCP/DR, risk, firewall reviews."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .store import (
    create_review,
    delete_review,
    get_review,
    init_store,
    list_reviews,
    update_review,
    REVIEW_TYPES,
    REVIEW_FREQUENCIES,
    REVIEW_STATUSES,
)

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


class ReviewCreateBody(BaseModel):
    title: str
    type: str = ""
    description: str = ""
    frequency: str = ""
    owner_id: str = ""
    owner_name: str = ""
    scheduled_date: str = ""
    framework_id: str = ""
    workspace_id: str = ""
    org_id: str = ""
    control_ids: Optional[List[str]] = None


class ReviewUpdateBody(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    scheduled_date: Optional[str] = None
    completed_date: Optional[str] = None
    status: Optional[str] = None
    evidence_ids: Optional[List[str]] = None
    findings: Optional[List[dict]] = None
    control_ids: Optional[List[str]] = None


@router.get("")
def get_reviews(
    type: Optional[str] = Query(None),
    framework_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    workspace_id: Optional[str] = Query(None),
):
    items = list_reviews(review_type=type, framework_id=framework_id, status=status, workspace_id=workspace_id)
    return {"reviews": items, "total": len(items)}


@router.get("/types")
def get_review_types():
    return {"types": REVIEW_TYPES, "frequencies": REVIEW_FREQUENCIES, "statuses": REVIEW_STATUSES}


@router.get("/{review_id}")
def get_review_endpoint(review_id: str):
    r = get_review(review_id)
    if not r:
        raise HTTPException(404, "Review not found")
    return {"review": r}


@router.post("")
def create_review_endpoint(body: ReviewCreateBody):
    r = create_review(
        title=body.title,
        review_type=body.type,
        description=body.description,
        frequency=body.frequency,
        owner_id=body.owner_id,
        owner_name=body.owner_name,
        scheduled_date=body.scheduled_date,
        framework_id=body.framework_id,
        workspace_id=body.workspace_id,
        org_id=body.org_id,
        control_ids=body.control_ids,
    )
    return {"review": r}


@router.patch("/{review_id}")
def update_review_endpoint(review_id: str, body: ReviewUpdateBody):
    existing = get_review(review_id)
    if not existing:
        raise HTTPException(404, "Review not found")
    updates = body.model_dump(exclude_none=True)
    if not updates:
        return {"review": existing}
    r = update_review(review_id, **updates)
    return {"review": r}


@router.delete("/{review_id}")
def delete_review_endpoint(review_id: str):
    if not delete_review(review_id):
        raise HTTPException(404, "Review not found")
    return {"status": "ok"}
