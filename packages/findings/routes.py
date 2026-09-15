from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from .models import (
    FINDING_SOURCES, FINDING_SEVERITIES, FINDING_STATUSES, ACTION_STATUSES,
)

router = APIRouter()


class FindingCreateBody(BaseModel):
    title: str
    description: str = ""
    remediation: str = ""
    source: str = ""
    source_id: str = ""
    severity: str = "medium"
    status: str = "open"
    owner: str = ""
    framework: str = ""
    control_ids: list[str] = []
    evidence_ids: list[str] = []
    tags: list[str] = []
    created_by: str = ""


class FindingUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    remediation: Optional[str] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    framework: Optional[str] = None
    control_ids: Optional[list[str]] = None
    evidence_ids: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    changed_by: str = ""


class ActionCreateBody(BaseModel):
    title: str
    description: str = ""
    owner: str = ""
    target_date: str = ""
    status: str = "open"
    evidence_id: str = ""
    notes: str = ""
    created_by: str = ""


class ActionUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    target_date: Optional[str] = None
    status: Optional[str] = None
    completed_at: Optional[str] = None
    evidence_id: Optional[str] = None
    notes: Optional[str] = None
    changed_by: str = ""


@router.get("/api/findings")
def get_findings(
    source: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    framework: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    control_id: Optional[str] = Query(None),
):
    from .store import list_findings
    return {"findings": list_findings(
        source=source,
        severity=severity,
        status=status,
        framework=framework,
        owner=owner,
        control_id=control_id,
    )}


@router.post("/api/findings")
def create_finding(body: FindingCreateBody):
    from .store import create_finding
    return {"finding": create_finding(
        title=body.title,
        description=body.description,
        remediation=body.remediation,
        source=body.source,
        source_id=body.source_id,
        severity=body.severity,
        status=body.status,
        owner=body.owner,
        framework=body.framework,
        control_ids=body.control_ids,
        evidence_ids=body.evidence_ids,
        tags=body.tags,
        created_by=body.created_by,
    )}


@router.get("/api/findings/stats")
def get_stats():
    from .store import by_severity, by_status, by_framework, by_source
    return {
        "by_severity": by_severity(),
        "by_status": by_status(),
        "by_framework": by_framework(),
        "by_source": by_source(),
    }


@router.get("/api/findings/{finding_id}")
def get_finding(finding_id: str):
    from .store import get_finding
    f = get_finding(finding_id)
    if not f:
        raise HTTPException(404, "Finding not found")
    return {"finding": f}


@router.patch("/api/findings/{finding_id}")
def update_finding(finding_id: str, body: FindingUpdateBody):
    from .store import update_finding
    f = update_finding(
        finding_id,
        title=body.title,
        description=body.description,
        remediation=body.remediation,
        source=body.source,
        source_id=body.source_id,
        severity=body.severity,
        status=body.status,
        owner=body.owner,
        framework=body.framework,
        control_ids=body.control_ids,
        evidence_ids=body.evidence_ids,
        tags=body.tags,
        changed_by=body.changed_by,
    )
    if not f:
        raise HTTPException(404, "Finding not found")
    return {"finding": f}


@router.delete("/api/findings/{finding_id}")
def delete_finding(finding_id: str):
    from .store import delete_finding
    if not delete_finding(finding_id):
        raise HTTPException(404, "Finding not found")
    return {"status": "deleted"}


@router.get("/api/findings/{finding_id}/actions")
def get_actions(finding_id: str):
    from .store import list_actions
    return {"actions": list_actions(finding_id)}


@router.post("/api/findings/{finding_id}/actions")
def create_action(finding_id: str, body: ActionCreateBody):
    from .store import create_action
    a = create_action(
        finding_id=finding_id,
        title=body.title,
        description=body.description,
        owner=body.owner,
        target_date=body.target_date,
        status=body.status,
        evidence_id=body.evidence_id,
        notes=body.notes,
        created_by=body.created_by,
    )
    if not a:
        raise HTTPException(404, "Finding not found")
    return {"action": a}


@router.get("/api/findings/{finding_id}/actions/{action_id}")
def get_action(finding_id: str, action_id: str):
    from .store import get_action
    a = get_action(action_id)
    if not a or a.get("finding_id") != finding_id:
        raise HTTPException(404, "Action not found")
    return {"action": a}


@router.patch("/api/findings/{finding_id}/actions/{action_id}")
def update_action(finding_id: str, action_id: str, body: ActionUpdateBody):
    from .store import update_action
    a = update_action(
        action_id,
        title=body.title,
        description=body.description,
        owner=body.owner,
        target_date=body.target_date,
        status=body.status,
        completed_at=body.completed_at,
        evidence_id=body.evidence_id,
        notes=body.notes,
        changed_by=body.changed_by,
    )
    if not a or a.get("finding_id") != finding_id:
        raise HTTPException(404, "Action not found")
    return {"action": a}


@router.delete("/api/findings/{finding_id}/actions/{action_id}")
def delete_action(finding_id: str, action_id: str):
    from .store import get_action, delete_action
    a = get_action(action_id)
    if not a or a.get("finding_id") != finding_id:
        raise HTTPException(404, "Action not found")
    delete_action(action_id)
    return {"status": "deleted"}
