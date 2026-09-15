from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

from .models import FRAMEWORKS


class ExceptionCreateBody(BaseModel):
    title: str = ""
    description: str = ""
    org_id: str = ""
    workspace_id: str = ""
    framework: str = ""
    control_id: str = ""
    control_reference: str = ""
    risk_level: str = "medium"
    likelihood: int = 0
    impact: int = 0
    compensating_controls: str = ""
    risk_acceptance: str = ""
    owner: str = ""
    created_by: str = ""
    expiry_date: str = ""
    expiry_days: int = 0
    notes: str = ""
    model_id: str = ""
    justification: str = ""


class ExceptionUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    framework: Optional[str] = None
    control_id: Optional[str] = None
    control_reference: Optional[str] = None
    status: Optional[str] = None
    risk_level: Optional[str] = None
    likelihood: Optional[int] = None
    impact: Optional[int] = None
    compensating_controls: Optional[str] = None
    risk_acceptance: Optional[str] = None
    owner: Optional[str] = None
    approved_by: Optional[str] = None
    expiry_date: Optional[str] = None
    expiry_days: Optional[int] = None
    model_id: Optional[str] = None
    notes: Optional[str] = None
    changed_by: str = ""


class CommentBody(BaseModel):
    author: str
    body: str = ""
    text: str = ""


class ExtendBody(BaseModel):
    expiry_days: int = 30
    approval_notes: str = ""
    changed_by: str = ""
    days: int = 0


class ReviewBody(BaseModel):
    outcome: str = "close"
    notes: str = ""
    changed_by: str = ""


# ─── Collection routes (must be before {eid}) ──────────


@router.get("/api/exceptions")
def get_exceptions(
    org_id: Optional[str] = Query(None),
    workspace_id: Optional[str] = Query(None),
    framework: Optional[str] = Query(None),
    control_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
):
    from .store import list_exceptions
    items = list_exceptions(
        org_id=org_id,
        workspace_id=workspace_id,
        framework=framework,
        control_id=control_id,
        status=status,
        owner=owner,
    )
    from .models import build_enriched
    return {"exceptions": [build_enriched(e) for e in items]}


@router.post("/api/exceptions")
def create_exception(body: ExceptionCreateBody):
    from .store import create_exception
    desc = body.description or body.justification
    title = body.title or desc or "Untitled"
    exc = create_exception(
        title=title,
        description=desc,
        org_id=body.org_id,
        workspace_id=body.workspace_id,
        framework=body.framework,
        control_id=body.control_id,
        control_reference=body.control_reference,
        risk_level=body.risk_level,
        likelihood=body.likelihood,
        impact=body.impact,
        compensating_controls=body.compensating_controls,
        risk_acceptance=body.risk_acceptance,
        owner=body.owner,
        created_by=body.created_by,
        expiry_date=body.expiry_date,
        expiry_days=body.expiry_days,
        notes=body.notes,
        model_id=body.model_id,
    )
    from .models import build_enriched
    return {"exception": build_enriched(exc)}


@router.get("/api/exceptions/stats")
def get_stats(org_id: Optional[str] = Query(None)):
    from .store import get_stats
    return get_stats(org_id=org_id)


@router.get("/api/exceptions/reminders")
def get_reminders():
    from .store import get_reminders
    return get_reminders()


@router.get("/api/exceptions/export.csv")
def export_csv():
    from .store import export_csv
    csv_data = export_csv()
    return Response(csv_data, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=exceptions-export.csv"})


@router.get("/api/exceptions/export/csv")
def export_csv_alt():
    return export_csv()


@router.post("/api/exceptions/seed")
def seed_data():
    from .store import seed_data
    count = seed_data()
    if count == 0:
        return {"message": "Data already seeded"}
    return {"ok": True, "count": count}


# ─── Frameworks ──────────────────────────────


class RiskAssessmentBody(BaseModel):
    method: str = "likelihood_impact"
    likelihood: int = 1
    impact: int = 1
    score: int = 0
    residual: str = ""
    rationale: str = ""
    changed_by: str = ""


@router.get("/api/frameworks")
def list_frameworks():
    from .framework_registry import list_frameworks as _list
    return {"frameworks": _list()}


# ─── Lifecycle / Risk / Transitions ───────────────


@router.get("/api/exceptions/{eid}/transitions")
def get_transitions(eid: str):
    from .store import get_exception, get_allowed_transitions
    exc = get_exception(eid)
    if not exc:
        raise HTTPException(404, "Exception not found")
    return {"transitions": get_allowed_transitions(exc)}


@router.post("/api/exceptions/{eid}/risk")
def set_risk(eid: str, body: RiskAssessmentBody):
    from .store import update_risk
    ra = body.model_dump()
    changed_by = ra.pop("changed_by", "")
    exc = update_risk(eid, ra, changed_by=changed_by)
    if not exc:
        raise HTTPException(404, "Exception not found")
    from .models import build_enriched
    return {"exception": build_enriched(exc)}


@router.get("/api/exceptions/{eid}/lifecycle")
def get_lifecycle(eid: str):
    from .store import get_exception
    exc = get_exception(eid)
    if not exc:
        raise HTTPException(404, "Exception not found")
    return {
        "extension_log": exc.get("extension_log", []),
        "history": exc.get("history", []),
    }


# ─── Item routes (after all literal routes) ──────────


@router.get("/api/exceptions/{eid}")
def get_exception(eid: str):
    from .store import get_exception
    exc = get_exception(eid)
    if not exc:
        raise HTTPException(404, "Exception not found")
    from .models import build_enriched
    return {"exception": build_enriched(exc)}


@router.patch("/api/exceptions/{eid}")
def update_exception(eid: str, body: ExceptionUpdateBody):
    from .store import update_exception
    exc = update_exception(
        eid,
        title=body.title,
        description=body.description,
        framework=body.framework,
        control_id=body.control_id,
        control_reference=body.control_reference,
        status=body.status,
        risk_level=body.risk_level,
        likelihood=body.likelihood,
        impact=body.impact,
        compensating_controls=body.compensating_controls,
        risk_acceptance=body.risk_acceptance,
        owner=body.owner,
        approved_by=body.approved_by,
        expiry_date=body.expiry_date,
        expiry_days=body.expiry_days,
        model_id=body.model_id,
        notes=body.notes,
        changed_by=body.changed_by,
    )
    if not exc:
        raise HTTPException(404, "Exception not found")
    from .models import build_enriched
    return {"exception": build_enriched(exc)}


@router.delete("/api/exceptions/{eid}")
def delete_exception(eid: str):
    from .store import delete_exception
    if not delete_exception(eid):
        raise HTTPException(404, "Exception not found")
    return {"status": "deleted"}


# ─── Milestones / POA&M ──────────────────────


class MilestoneBody(BaseModel):
    description: str
    target_date: str = ""
    owner: str = ""
    changed_by: str = ""


class MilestoneUpdateBody(BaseModel):
    description: str | None = None
    target_date: str | None = None
    status: str | None = None
    owner: str | None = None
    evidence: str | None = None
    completion_date: str | None = None
    changed_by: str = ""


@router.post("/api/exceptions/{eid}/milestones")
def add_milestone(eid: str, body: MilestoneBody):
    from .store import add_milestone
    m = add_milestone(eid, description=body.description, target_date=body.target_date,
                      owner=body.owner, changed_by=body.changed_by)
    if not m:
        raise HTTPException(404, "Exception not found")
    return {"milestone": m}


@router.patch("/api/exceptions/{eid}/milestones/{mid}")
def update_milestone(eid: str, mid: str, body: MilestoneUpdateBody):
    from .store import update_milestone
    m = update_milestone(
        eid, mid,
        description=body.description,
        target_date=body.target_date,
        status=body.status,
        owner=body.owner,
        evidence=body.evidence,
        completion_date=body.completion_date,
        changed_by=body.changed_by,
    )
    if not m:
        raise HTTPException(404, "Milestone not found")
    return {"milestone": m}


@router.delete("/api/exceptions/{eid}/milestones/{mid}")
def delete_milestone(eid: str, mid: str, changed_by: str = ""):
    from .store import delete_milestone
    if not delete_milestone(eid, mid, changed_by=changed_by):
        raise HTTPException(404, "Milestone not found")
    return {"status": "deleted"}


# ─── Comments ────────────────────────────────


@router.post("/api/exceptions/{eid}/comments")
def add_comment(eid: str, body: CommentBody):
    from .store import add_comment
    text = body.body or body.text
    c = add_comment(eid, author=body.author, body=text)
    if not c:
        raise HTTPException(404, "Exception not found")
    return {"comment": c}


# ─── Extend / Review (AI Gov lifecycle) ──────────


@router.post("/api/exceptions/{eid}/extend")
def extend_exception(eid: str, body: ExtendBody):
    from .store import extend_exception
    days = body.expiry_days if body.expiry_days else (body.days or 30)
    exc = extend_exception(eid, expiry_days=days, approval_notes=body.approval_notes, changed_by=body.changed_by)
    if not exc:
        raise HTTPException(404, "Exception not found")
    from .models import build_enriched
    return build_enriched(exc)


@router.post("/api/exceptions/{eid}/review")
def review_exception(eid: str, body: ReviewBody):
    from .store import review_exception as store_review
    exc = store_review(eid, outcome=body.outcome, notes=body.notes, changed_by=body.changed_by)
    if not exc:
        raise HTTPException(404, "Exception not found")
    from .models import build_enriched
    return {"exception": build_enriched(exc), "outcome": body.outcome}


@router.post("/api/exceptions/{eid}/approve")
def approve_exception(eid: str, body: ReviewBody):
    from .store import review_exception as store_review
    exc = store_review(eid, outcome="close", notes=body.notes, changed_by=body.changed_by)
    if not exc:
        raise HTTPException(404, "Exception not found")
    from .models import build_enriched
    return {"exception": build_enriched(exc), "outcome": "close"}


@router.post("/api/exceptions/{eid}/reject")
def reject_exception(eid: str, body: ReviewBody):
    from .store import review_exception as store_review
    exc = store_review(eid, outcome="reject", notes=body.notes, changed_by=body.changed_by)
    if not exc:
        raise HTTPException(404, "Exception not found")
    from .models import build_enriched
    return {"exception": build_enriched(exc), "outcome": "reject"}


@router.post("/api/exceptions/{eid}/escalate")
def escalate_exception(eid: str, body: ReviewBody):
    from .store import review_exception as store_review
    exc = store_review(eid, outcome="escalate", notes=body.notes, changed_by=body.changed_by)
    if not exc:
        raise HTTPException(404, "Exception not found")
    from .models import build_enriched
    return {"exception": build_enriched(exc), "outcome": "escalate"}


# ─── Reminders ─────────────────────────────────


@router.get("/api/exceptions/{eid}/reminder")
def get_reminder(eid: str):
    from .store import get_reminder
    r = get_reminder(eid)
    if not r:
        raise HTTPException(404, "Exception not found")
    return r


# ─── Attachments ─────────────────────────────


@router.post("/api/exceptions/{eid}/attachments")
def upload_attachment(eid: str, file: UploadFile = File(...)):
    from .store import upload_attachment
    data = file.file.read()
    att = upload_attachment(eid, filename=file.filename or "file", data=data)
    if att is None:
        from .store import get_exception
        if not get_exception(eid):
            raise HTTPException(404, "Exception not found")
        raise HTTPException(400, "File exceeds 10MB limit")
    return {"attachment": att}


@router.get("/api/exceptions/{eid}/attachments/{fid}")
def get_attachment(eid: str, fid: str):
    from .store import get_attachment
    data, filename = get_attachment(eid, fid)
    if data is None:
        raise HTTPException(404, "Attachment not found")
    return Response(data, media_type="application/octet-stream",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.delete("/api/exceptions/{eid}/attachments/{fid}")
def delete_attachment(eid: str, fid: str):
    from .store import get_exception, _get_db, _write_exc, UPLOADS_DIR
    import os
    exc = get_exception(eid)
    if not exc:
        raise HTTPException(404, "Exception not found")
    atts = exc.get("attachments", [])
    for i, att in enumerate(atts):
        if att["id"] == fid:
            stored = att.get("stored_as", "")
            if stored:
                path = os.path.join(UPLOADS_DIR, stored)
                if os.path.exists(path):
                    os.remove(path)
            atts.pop(i)
            db = _get_db()
            try:
                _write_exc(db, exc)
                db.commit()
            finally:
                db.close()
            return {"status": "deleted"}
    raise HTTPException(404, "Attachment not found")
