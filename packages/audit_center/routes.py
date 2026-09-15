from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class AuditCreateBody(BaseModel):
    title: str
    framework: str = ""
    audit_type: str = ""
    start_date: str = ""
    end_date: str = ""
    auditor_name: str = ""
    auditor_email: str = ""
    scope_notes: str = ""
    preparation_notes: str = ""
    control_id: str = ""
    created_by: str = ""


class AuditUpdateBody(BaseModel):
    title: Optional[str] = None
    framework: Optional[str] = None
    audit_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    auditor_name: Optional[str] = None
    auditor_email: Optional[str] = None
    scope_notes: Optional[str] = None
    preparation_notes: Optional[str] = None
    control_id: Optional[str] = None


class RequestCreateBody(BaseModel):
    title: str
    control_id: str = ""
    description: str = ""
    requested_by: str = ""
    assigned_to: str = ""
    evidence_notes: str = ""
    due_date: str = ""


class RequestUpdateBody(BaseModel):
    title: Optional[str] = None
    control_id: Optional[str] = None
    description: Optional[str] = None
    requested_by: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    evidence_id: Optional[str] = None
    evidence_notes: Optional[str] = None
    due_date: Optional[str] = None


# ─── Audits ──────────────────────────


@router.get("/api/audit-center/audits")
def get_audits(
    framework: Optional[str] = Query(None),
    audit_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    auditor_name: Optional[str] = Query(None),
    control_id: Optional[str] = Query(None),
):
    from .store import list_audits
    return {"audits": list_audits(
        framework=framework,
        audit_type=audit_type,
        status=status,
        auditor_name=auditor_name,
        control_id=control_id,
    )}


@router.post("/api/audit-center/audits")
def create_audit(body: AuditCreateBody):
    from .store import create_audit
    return {"audit": create_audit(
        title=body.title,
        framework=body.framework,
        audit_type=body.audit_type,
        start_date=body.start_date,
        end_date=body.end_date,
        auditor_name=body.auditor_name,
        auditor_email=body.auditor_email,
        scope_notes=body.scope_notes,
        preparation_notes=body.preparation_notes,
        control_id=body.control_id,
        created_by=body.created_by,
    )}


@router.get("/api/audit-center/audits/{audit_id}")
def get_audit(audit_id: str):
    from .store import get_audit
    a = get_audit(audit_id)
    if not a:
        raise HTTPException(404, "Audit not found")
    return {"audit": a}


@router.patch("/api/audit-center/audits/{audit_id}")
def update_audit(audit_id: str, body: AuditUpdateBody):
    from .store import update_audit
    a = update_audit(
        audit_id,
        title=body.title,
        framework=body.framework,
        audit_type=body.audit_type,
        start_date=body.start_date,
        end_date=body.end_date,
        status=body.status,
        auditor_name=body.auditor_name,
        auditor_email=body.auditor_email,
        scope_notes=body.scope_notes,
        preparation_notes=body.preparation_notes,
        control_id=body.control_id,
    )
    if not a:
        raise HTTPException(404, "Audit not found")
    return {"audit": a}


@router.delete("/api/audit-center/audits/{audit_id}")
def delete_audit(audit_id: str):
    from .store import delete_audit
    if not delete_audit(audit_id):
        raise HTTPException(404, "Audit not found")
    return {"status": "deleted"}


@router.post("/api/audit-center/audits/{audit_id}/freeze")
def freeze_audit(audit_id: str):
    from .store import freeze_audit
    a = freeze_audit(audit_id)
    if not a:
        raise HTTPException(404, "Audit not found")
    return {"audit": a}


# ─── Evidence Requests ────────────────


@router.get("/api/audit-center/audits/{audit_id}/requests")
def get_requests(audit_id: str):
    from .store import list_requests
    return {"requests": list_requests(audit_id=audit_id)}


@router.post("/api/audit-center/audits/{audit_id}/requests")
def create_request(audit_id: str, body: RequestCreateBody):
    from .store import create_request
    return {"request": create_request(
        audit_id=audit_id,
        title=body.title,
        control_id=body.control_id,
        description=body.description,
        requested_by=body.requested_by,
        assigned_to=body.assigned_to,
        evidence_notes=body.evidence_notes,
        due_date=body.due_date,
    )}


@router.get("/api/audit-center/audits/{audit_id}/requests/{request_id}")
def get_request(audit_id: str, request_id: str):
    from .store import get_request
    r = get_request(request_id)
    if not r or r.get("audit_id") != audit_id:
        raise HTTPException(404, "Evidence request not found")
    return {"request": r}


@router.patch("/api/audit-center/audits/{audit_id}/requests/{request_id}")
def update_request(audit_id: str, request_id: str, body: RequestUpdateBody):
    from .store import update_request
    r = update_request(
        request_id,
        title=body.title,
        control_id=body.control_id,
        description=body.description,
        requested_by=body.requested_by,
        assigned_to=body.assigned_to,
        status=body.status,
        evidence_id=body.evidence_id,
        evidence_notes=body.evidence_notes,
        due_date=body.due_date,
    )
    if not r or r.get("audit_id") != audit_id:
        raise HTTPException(404, "Evidence request not found")
    return {"request": r}


@router.delete("/api/audit-center/audits/{audit_id}/requests/{request_id}")
def delete_request(audit_id: str, request_id: str):
    from .store import delete_request
    r = delete_request(request_id)
    if not r:
        raise HTTPException(404, "Evidence request not found")
    return {"status": "deleted"}


# ─── Stats ─────────────────────────────


@router.get("/api/audit-center/stats")
def get_stats():
    from .store import get_stats
    return get_stats()
