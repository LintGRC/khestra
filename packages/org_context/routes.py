"""Organizational context routes — /api/org-context (ISO 27001 4.1/4.2/4.3)."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import store

router = APIRouter()


class InterestedParty(BaseModel):
    name: str = ""
    requirements: list[str] = []
    addressed_via_isms: bool = True
    notes: str = ""


class ContextCreate(BaseModel):
    label: str = ""
    internal_issues: list[str] = []
    external_issues: list[str] = []
    interested_parties: list[InterestedParty] = []
    climate_relevant: bool = False
    climate_note: str = ""
    climate_status: str = "not_assessed"
    scope_statement: str = ""
    boundaries: str = ""
    interfaces_dependencies: list[str] = []


class ContextUpdate(BaseModel):
    label: Optional[str] = None
    internal_issues: Optional[list[str]] = None
    external_issues: Optional[list[str]] = None
    interested_parties: Optional[list[InterestedParty]] = None
    climate_relevant: Optional[bool] = None
    climate_note: Optional[str] = None
    climate_status: Optional[str] = None
    scope_statement: Optional[str] = None
    boundaries: Optional[str] = None
    interfaces_dependencies: Optional[list[str]] = None


def _parties_to_dicts(parties: list[InterestedParty]) -> list[dict]:
    return [p.model_dump() for p in parties]


@router.get("/api/org-context")
def list_context():
    records = store.list_records()
    return {"records": records, "latest": records[0] if records else None}


@router.get("/api/org-context/stats")
def context_stats():
    return store.stats()


@router.get("/api/org-context/{rid}")
def get_context(rid: str):
    record = store.get_record(rid)
    if not record:
        raise HTTPException(status_code=404, detail="Context record not found")
    return {"record": record}


@router.post("/api/org-context")
def create_context(body: ContextCreate):
    return {"record": store.create_record(
        label=body.label,
        internal_issues=body.internal_issues,
        external_issues=body.external_issues,
        interested_parties=_parties_to_dicts(body.interested_parties),
        climate_relevant=body.climate_relevant,
        climate_note=body.climate_note,
        climate_status=body.climate_status,
        scope_statement=body.scope_statement,
        boundaries=body.boundaries,
        interfaces_dependencies=body.interfaces_dependencies,
    )}


@router.patch("/api/org-context/{rid}")
def update_context(rid: str, body: ContextUpdate):
    # model_dump() already converts nested models (InterestedParty) to dicts
    payload = body.model_dump(exclude_none=True)
    record = store.update_record(rid, **payload)
    if not record:
        raise HTTPException(status_code=404, detail="Context record not found")
    return {"record": record}


@router.delete("/api/org-context/{rid}")
def delete_context(rid: str):
    if not store.delete_record(rid):
        raise HTTPException(status_code=404, detail="Context record not found")
    return {"ok": True}
