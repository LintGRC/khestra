from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Request
from fastapi.responses import Response, StreamingResponse
from typing import Optional
from pydantic import BaseModel

router = APIRouter()


class EvidenceCreate(BaseModel):
    name: str = ""
    filename: str = ""
    description: str = ""
    tags: list[str] = []
    uploaded_by: str = ""


class MapBody(BaseModel):
    framework_id: str = ""
    control_id: str = ""
    mapped_by: str = ""


class ReviewBody(BaseModel):
    status: str = "approved"
    reviewer: str = ""
    comment: str = ""


class AssignReviewerBody(BaseModel):
    reviewer: str
    due_date: str = ""


class RemediationBody(BaseModel):
    instructions: str


class BulkReviewBody(BaseModel):
    eids: list[str]
    status: str
    reviewer: str = ""
    comment: str = ""


class RequestCreate(BaseModel):
    framework_id: str = ""
    control_id: str = ""
    title: str = ""
    description: str = ""
    assigned_to: str = ""
    due_date: str = ""


class RequestPatch(BaseModel):
    status: str = ""
    assigned_to: str = ""
    due_date: str = ""


def _log(req: Request, eid: str, action: str, meta: Optional[dict] = None):
    from .store import log_access
    ip = req.client.host if req.client else ""
    log_access(eid, action, performed_by="api", metadata=meta or {}, ip_address=ip)


# ─── Evidence CRUD ─────────────────────────────────


@router.get("/api/evidence-hub")
def list_evidence(
    framework_id: Optional[str] = Query(None),
    control_id: Optional[str] = Query(None),
    view: str = Query("latest"),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    from .store import list_evidence as _list
    items = _list(framework_id=framework_id, control_id=control_id, view=view, limit=limit, offset=offset, date_from=date_from, date_to=date_to)
    return {"evidence": items, "view": view, "count": len(items)}


@router.get("/api/evidence-hub/stats")
def evidence_stats():
    from .store import get_stats
    return get_stats()


@router.get("/api/evidence-hub/export")
def export_audit_package(
    framework_id: Optional[str] = Query(None),
    control_id: Optional[str] = Query(None),
):
    from .store import export_audit_package as _export
    data = _export(framework_id=framework_id, control_id=control_id)
    fw_part = f"_{framework_id}" if framework_id else ""
    ctrl_part = f"_{control_id}" if control_id else ""
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="evidence_hub{fw_part}{ctrl_part}.zip"'},
    )


@router.post("/api/evidence-hub")
def create_evidence(body: EvidenceCreate, request: Request):
    from .store import create_evidence
    ev = create_evidence(
        name=body.name, filename=body.filename,
        description=body.description, tags=body.tags,
        uploaded_by=body.uploaded_by,
    )
    _log(request, ev["id"], "created", {"name": body.name})
    return {"evidence": ev}


@router.post("/api/evidence-hub/upload")
async def upload_evidence(request: Request,
    name: str = Form(""),
    description: str = Form(""),
    tags: str = Form("[]"),
    uploaded_by: str = Form(""),
    valid_until: str = Form(""),
    file: UploadFile = File(...),
):
    from .store import upload_evidence_file
    import json
    data = await file.read()
    tag_list = json.loads(tags) if isinstance(tags, str) else tags
    ev = upload_evidence_file(
        name=name or (file.filename or "evidence"),
        file_data=data, filename=file.filename or "evidence.bin",
        description=description, tags=tag_list,
        uploaded_by=uploaded_by, mime_type=file.content_type or "application/octet-stream",
        valid_until=valid_until,
    )
    _log(request, ev["id"], "uploaded", {"filename": file.filename})
    return {"evidence": ev}


@router.post("/api/evidence-hub/upload-and-map")
async def upload_and_map(request: Request,
    framework_id: str = Form(...),
    control_id: str = Form(...),
    name: str = Form(""), description: str = Form(""),
    tags: str = Form("[]"), uploaded_by: str = Form(""),
    evidence_type: str = Form(""), display_title: str = Form(""),
    evidence_version: str = Form(""), valid_until: str = Form(""),
    file: UploadFile = File(...),
):
    from .store import upload_evidence_file, map_evidence
    import json
    data = await file.read()
    tag_list = json.loads(tags) if isinstance(tags, str) else tags
    ev = upload_evidence_file(
        name=name or (file.filename or "evidence"), file_data=data,
        filename=file.filename or "evidence.bin", description=description,
        tags=tag_list, uploaded_by=uploaded_by,
        mime_type=file.content_type or "application/octet-stream",
        evidence_type=evidence_type, display_title=display_title,
        evidence_version=evidence_version, valid_until=valid_until,
    )
    map_evidence(ev["id"], framework_id, control_id, mapped_by=uploaded_by)
    _log(request, ev["id"], "uploaded_and_mapped", {"framework_id": framework_id, "control_id": control_id})
    return {"evidence": ev}


# ─── Metadata & Analysis ───────────────────────────


@router.get("/api/evidence-hub/freshness")
def evidence_freshness(framework_id: Optional[str] = Query(None)):
    from .store import get_freshness_stats
    return get_freshness_stats(framework_id=framework_id)


@router.get("/api/evidence-hub/requests/overdue")
def overdue_evidence_requests(framework_id: Optional[str] = Query(None)):
    from .store import get_overdue_requests
    return {"requests": get_overdue_requests(framework_id=framework_id)}


@router.get("/api/evidence-hub/sufficiency")
def sufficiency_score(framework_id: str = Query("soc2"), control_id: str = Query("")):
    from .store import get_sufficiency_score
    if control_id:
        return get_sufficiency_score(framework_id, control_id)
    from .store import get_sufficiency_matrix
    return get_sufficiency_matrix(framework_id)


@router.get("/api/evidence-hub/unmapped-coverage")
def unmapped_coverage(framework_id: str = Query("soc2")):
    from .store import get_unmapped_coverage
    return {"unmapped": get_unmapped_coverage(framework_id)}


# ─── Single Evidence Operations ─────────────────────


@router.get("/api/evidence-hub/{eid}")
def get_evidence(eid: str, request: Request):
    from .store import get_evidence
    ev = get_evidence(eid)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    _log(request, eid, "viewed")
    return {"evidence": ev}


@router.get("/api/evidence-hub/{eid}/download")
def download_evidence(eid: str, request: Request):
    from .store import get_evidence, get_evidence_file_path
    ev = get_evidence(eid)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    path = get_evidence_file_path(eid)
    if not path:
        raise HTTPException(404, "File not found on disk")
    data = path.read_bytes()
    _log(request, eid, "downloaded", {"filename": ev["filename"]})
    return Response(
        content=data,
        media_type=ev.get("mime_type") or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{ev["filename"]}"'},
    )


@router.get("/api/evidence-hub/{eid}/verify")
def verify_evidence(eid: str, request: Request):
    from .store import get_evidence, get_evidence_file_path
    import hashlib
    ev = get_evidence(eid)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    path = get_evidence_file_path(eid)
    if not path:
        raise HTTPException(404, "File not found on disk")
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    expected = ev.get("sha256", "")
    _log(request, eid, "verified", {"result": actual == expected})
    return {"verified": actual == expected, "expected_sha256": expected, "filename": ev["filename"]}


@router.get("/api/evidence-hub/{eid}/content")
def evidence_content(eid: str):
    from .store import get_evidence, get_evidence_file_path
    ev = get_evidence(eid)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    path = get_evidence_file_path(eid)
    if not path:
        raise HTTPException(404, "File not found on disk")
    mime = ev.get("mime_type") or ""
    if mime != "application/json" and not ev.get("filename", "").endswith(".json"):
        raise HTTPException(400, "Only JSON files can be previewed inline")
    data = path.read_bytes()
    return Response(content=data, media_type="application/json",
        headers={"Content-Disposition": f'inline; filename="{ev["filename"]}"'})


@router.get("/api/evidence-hub/{eid}/history")
def evidence_history(eid: str):
    from .store import get_evidence_history
    history = get_evidence_history(eid)
    return {"history": history}


@router.get("/api/evidence-hub/{eid}/cross-framework-suggestions")
def cross_framework_suggestions(eid: str):
    from .store import get_cross_framework_suggestions
    return {"suggestions": get_cross_framework_suggestions(eid)}


@router.delete("/api/evidence-hub/{eid}")
def delete_evidence(eid: str, request: Request):
    from .store import delete_evidence
    if not delete_evidence(eid):
        raise HTTPException(404, "Evidence not found")
    _log(request, eid, "deleted")
    return {"status": "deleted"}


@router.post("/api/evidence-hub/{eid}/review")
def review_evidence(eid: str, body: ReviewBody, request: Request):
    from .store import review_evidence
    ev = review_evidence(eid, body.status, reviewer=body.reviewer, comment=body.comment)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    _log(request, eid, f"reviewed:{body.status}", {"status": body.status})
    return {"evidence": ev}


@router.post("/api/evidence-hub/{eid}/assign-reviewer")
def assign_reviewer(eid: str, body: AssignReviewerBody, request: Request):
    from .store import assign_reviewer
    ev = assign_reviewer(eid, body.reviewer, body.due_date)
    if not ev:
        raise HTTPException(404, "Evidence not found or already reviewed")
    _log(request, eid, "assigned_reviewer", {"reviewer": body.reviewer})
    return {"evidence": ev}


@router.post("/api/evidence-hub/{eid}/request-remediation")
def request_remediation(eid: str, body: RemediationBody, request: Request):
    from .store import request_remediation
    ev = request_remediation(eid, body.instructions)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    _log(request, eid, "remediation_requested", {"instructions": body.instructions})
    return {"evidence": ev}


@router.post("/api/evidence-hub/{eid}/map")
def map_evidence(eid: str, body: MapBody, request: Request):
    from .store import map_evidence
    result = map_evidence(eid, body.framework_id, body.control_id, mapped_by=body.mapped_by)
    _log(request, eid, "mapped", {"framework_id": body.framework_id, "control_id": body.control_id})
    return {"mapping": result}


@router.delete("/api/evidence-hub/{eid}/map/{framework_id}/{control_id}")
def unmap_evidence(eid: str, framework_id: str, control_id: str, request: Request):
    from .store import unmap_evidence
    if not unmap_evidence(eid, framework_id, control_id):
        raise HTTPException(404, "Mapping not found")
    _log(request, eid, "unmapped", {"framework_id": framework_id, "control_id": control_id})
    return {"status": "unmapped"}


# ─── Bulk Review ──────────────────────────────────────


@router.post("/api/evidence-hub/bulk-review")
def bulk_review_evidence(body: BulkReviewBody, request: Request):
    from .store import bulk_review_evidence as _bulk_review
    count = _bulk_review(body.eids, body.status, reviewer=body.reviewer, comment=body.comment)
    for eid in body.eids:
        _log(request, eid, f"bulk_reviewed:{body.status}")
    return {"updated": count}


# ─── Coverage Analysis ────────────────────────────────


@router.get("/api/evidence-hub/coverage")
def get_coverage_gaps(
    framework_id: str = Query(...),
    control_id: str = Query(...),
    days: int = Query(90),
):
    from .store import check_coverage_gaps
    return check_coverage_gaps(framework_id, control_id, days=days)


@router.get("/api/evidence-hub/coverage/summary")
def get_collector_period_summary(
    framework_id: str = Query(...),
    control_id: str = Query(...),
):
    from .store import collector_period_summary
    return {"summary": collector_period_summary(framework_id, control_id)}


# ─── Evidence Requests ────────────────────────────────


@router.get("/api/evidence-hub/requests")
def list_evidence_requests(framework_id: Optional[str] = Query(None), control_id: Optional[str] = Query(None)):
    from .store import list_requests
    return {"requests": list_requests(framework_id=framework_id, control_id=control_id)}


@router.post("/api/evidence-hub/requests")
def create_evidence_request(body: RequestCreate):
    from .store import create_request
    return {"request": create_request(
        framework_id=body.framework_id, control_id=body.control_id, title=body.title,
        description=body.description, assigned_to=body.assigned_to, due_date=body.due_date,
    )}


@router.patch("/api/evidence-hub/requests/{rid}")
def patch_evidence_request(rid: str, body: RequestPatch):
    from .store import patch_request
    req = patch_request(rid, status=body.status or None, assigned_to=body.assigned_to or None, due_date=body.due_date or None)
    if not req:
        raise HTTPException(404, "Request not found")
    return {"request": req}


@router.delete("/api/evidence-hub/requests/{rid}")
def delete_evidence_request(rid: str):
    from .store import delete_request
    if not delete_request(rid):
        raise HTTPException(404, "Request not found")
    return {"status": "deleted"}
