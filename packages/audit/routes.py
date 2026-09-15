from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from .store import log_action as _log_action

router = APIRouter(tags=["audit"])


class AuditLogBody(BaseModel):
    action: str
    resource_type: str
    resource_id: str
    resource_name: str = ""
    user: str = ""
    details: str = ""
    framework: str = ""
    source: str = ""


@router.get("/api/audit")
def list_audit_entries(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    user: Optional[str] = Query(None),
    framework: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
):
    from .store import list_entries
    return list_entries(
        action=action, resource_type=resource_type, resource_id=resource_id,
        user=user, framework=framework, source=source,
        limit=limit, offset=offset,
    )


@router.get("/api/audit/stats")
def audit_stats(
    framework: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    from .store import get_stats
    return get_stats(framework=framework, source=source)


@router.get("/api/audit/{entry_id}")
def get_audit_entry(entry_id: str):
    from .store import get_entry
    entry = get_entry(entry_id)
    if not entry:
        raise HTTPException(404, "Audit entry not found")
    return {"entry": entry.to_dict()}


@router.post("/api/audit")
def create_audit_entry(body: AuditLogBody):
    entry = _log_action(
        action=body.action,
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        resource_name=body.resource_name,
        user=body.user,
        details=body.details,
        framework=body.framework,
        source=body.source,
    )
    return {"entry": entry.to_dict()}
