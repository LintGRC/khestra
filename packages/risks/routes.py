from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Union

from .store import list_risks, create_risk, get_stats, get_risk, update_risk, delete_risk, add_comment, get_risks_by_control
from control_catalog.catalog import list_controls, list_frameworks

router = APIRouter()

LEVEL_MAP = {"low": 1, "medium": 2, "high": 3, "critical": 4}


class RiskCreateBody(BaseModel):
    title: str
    description: str = ""
    category: str = ""
    framework: str = ""
    control_ids: list[str] = []
    system_id: str = ""
    owner: str = ""
    likelihood: int = 0
    impact: int = 0
    inherent_likelihood: str = ""
    inherent_impact: str = ""
    residual_likelihood: Union[int, str] = 0
    residual_impact: Union[int, str] = 0
    residual_score: int = 0
    treatment: str = ""
    treatment_plan: str = ""
    controls: str = ""
    control_id: str = ""
    mitigation_evidence: list[str] = []
    tags: list[str] = []
    framework_metadata: dict = {}
    created_by: str = ""
    status: str = "identified"
    review_date: str = ""
    acceptance_expires: str = ""
    control_owner: str = ""


class RiskUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    framework: Optional[str] = None
    control_ids: Optional[list[str]] = None
    system_id: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    likelihood: Optional[int] = None
    impact: Optional[int] = None
    inherent_likelihood: Optional[str] = None
    inherent_impact: Optional[str] = None
    residual_likelihood: Optional[Union[int, str]] = None
    residual_impact: Optional[Union[int, str]] = None
    residual_score: Optional[int] = None
    treatment: Optional[str] = None
    treatment_plan: Optional[str] = None
    controls: Optional[str] = None
    control_id: Optional[str] = None
    mitigation_evidence: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    framework_metadata: Optional[dict] = None
    changed_by: str = ""
    review_date: Optional[str] = None
    acceptance_expires: Optional[str] = None
    control_owner: Optional[str] = None


class CommentBody(BaseModel):
    author: str
    body: str


def _acceptance_flag(risk: dict) -> dict:
    """Annotate accepted risks with acceptance expiry state."""
    from datetime import date

    r = dict(risk)
    r["acceptance_overdue"] = False
    r["acceptance_days_left"] = None
    if r.get("status") == "accepted" and r.get("acceptance_expires"):
        try:
            d = date.fromisoformat((r["acceptance_expires"] or "")[:10])
            delta = (d - date.today()).days
            r["acceptance_overdue"] = delta < 0
            r["acceptance_days_left"] = delta
        except ValueError:
            pass
    return r


@router.get("/api/risks")
def get_risks(
    framework: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    control_id: Optional[str] = Query(None),
):
    return {"risks": [
        _acceptance_flag(r) for r in list_risks(
            framework=framework,
            category=category,
            status=status,
            owner=owner,
            control_id=control_id,
        )
    ]}


@router.post("/api/risks")
def create_risk_route(body: RiskCreateBody):
    likelihood = body.likelihood or LEVEL_MAP.get(body.inherent_likelihood, 0)
    impact = body.impact or LEVEL_MAP.get(body.inherent_impact, 0)
    treatment_plan = body.treatment_plan or body.controls or ""
    cids = body.control_ids
    if body.control_id and body.control_id not in cids:
        cids = [*cids, body.control_id]
    rl = body.residual_likelihood
    if isinstance(rl, str):
        rl = LEVEL_MAP.get(rl, 0)
    ri = body.residual_impact
    if isinstance(ri, str):
        ri = LEVEL_MAP.get(ri, 0)
    return {"risk": create_risk(
        title=body.title,
        description=body.description,
        category=body.category,
        framework=body.framework,
        control_ids=cids,
        system_id=body.system_id,
        owner=body.owner,
        likelihood=likelihood,
        impact=impact,
        residual_likelihood=rl,
        residual_impact=ri,
        residual_score=body.residual_score,
        treatment=body.treatment,
        treatment_plan=treatment_plan,
        mitigation_evidence=body.mitigation_evidence,
        tags=body.tags,
        framework_metadata=body.framework_metadata,
        created_by=body.created_by,
        status=body.status,
        review_date=body.review_date,
        acceptance_expires=body.acceptance_expires,
        control_owner=body.control_owner,
    )}


@router.get("/api/risks/stats")
def get_stats_route():
    return get_stats()


@router.get("/api/risks/by-control/{control_id}")
def get_risks_by_control_route(control_id: str):
    return {"risks": get_risks_by_control(control_id)}


@router.get("/api/risks/export/csv")
def export_risks_csv():
    import csv, io
    items = list_risks()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["ID", "Title", "Description", "Category", "Framework", "System ID", "Owner", "Status", "Likelihood", "Impact", "Inherent Score", "Residual Score", "Treatment", "Treatment Plan", "Created At"])
    for r in items:
        w.writerow([
            r.get("id"), r.get("title"), r.get("description"), r.get("category"),
            r.get("framework"), r.get("system_id", ""), r.get("owner"), r.get("status"),
            r.get("likelihood"), r.get("impact"), r.get("inherent_score"),
            r.get("residual_score"), r.get("treatment"), r.get("treatment_plan"),
            r.get("created_at"),
        ])
    from fastapi.responses import Response
    return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=risks.csv"})


@router.get("/api/risk-controls")
def list_risk_controls(framework: str | None = None):
    return {"controls": list_controls(framework)}


@router.get("/api/risk-controls/uncovered")
def list_uncovered_controls(framework: str | None = None):
    covered: set[str] = set()
    for r in list_risks():
        for cid in r.get("control_ids") or []:
            covered.add(cid)
        if r.get("control_id"):
            covered.add(r["control_id"])
    controls = list_controls(framework)
    return {"controls": [c for c in controls if c["id"] not in covered]}


@router.get("/api/risk-frameworks")
def list_risk_frameworks():
    return {"frameworks": list_frameworks()}


@router.get("/api/risks/{rid}")
def get_risk_route(rid: str):
    risk = get_risk(rid)
    if not risk:
        raise HTTPException(404, "Risk not found")
    return {"risk": _acceptance_flag(risk)}


@router.patch("/api/risks/{rid}")
def update_risk_route(rid: str, body: RiskUpdateBody):
    likelihood = body.likelihood
    if likelihood is None and body.inherent_likelihood:
        likelihood = LEVEL_MAP.get(body.inherent_likelihood, 0)
    impact = body.impact
    if impact is None and body.inherent_impact:
        impact = LEVEL_MAP.get(body.inherent_impact, 0)
    treatment_plan = body.treatment_plan
    if treatment_plan is None and body.controls is not None:
        treatment_plan = body.controls
    cids = body.control_ids
    if body.control_id and (not cids or body.control_id not in cids):
        cids = [*(cids or []), body.control_id]
    rl = body.residual_likelihood
    if isinstance(rl, str):
        rl = LEVEL_MAP.get(rl, 0)
    ri = body.residual_impact
    if isinstance(ri, str):
        ri = LEVEL_MAP.get(ri, 0)
    risk = update_risk(
        rid,
        title=body.title,
        description=body.description,
        category=body.category,
        framework=body.framework,
        control_ids=cids,
        system_id=body.system_id,
        owner=body.owner,
        status=body.status,
        likelihood=likelihood,
        impact=impact,
        residual_likelihood=rl,
        residual_impact=ri,
        residual_score=body.residual_score,
        treatment=body.treatment,
        treatment_plan=treatment_plan,
        mitigation_evidence=body.mitigation_evidence,
        tags=body.tags,
        framework_metadata=body.framework_metadata,
        changed_by=body.changed_by,
        review_date=body.review_date,
        acceptance_expires=body.acceptance_expires,
        control_owner=body.control_owner,
    )
    if not risk:
        raise HTTPException(404, "Risk not found")
    return {"risk": risk}


@router.post("/api/risks/{rid}/re-sign")
def re_sign_risk_route(rid: str, body: Optional[RiskUpdateBody] = None):
    """Re-sign an accepted risk: bump acceptance expiry (default +12 months),
    mark accepted, and append an audit comment for the re-decision."""
    from datetime import date, timedelta
    from .store import add_comment as store_add_comment

    risk = get_risk(rid)
    if not risk:
        raise HTTPException(404, "Risk not found")
    if risk.get("status") != "accepted":
        raise HTTPException(422, "Only accepted risks can be re-signed")
    months = 12
    base = risk.get("acceptance_expires") or date.today().isoformat()
    try:
        d = date.fromisoformat((base or "")[:10])
    except ValueError:
        d = date.today()
    new_expiry = (d + timedelta(days=months * 30)).isoformat()
    updated = update_risk(rid, status="accepted", acceptance_expires=new_expiry, changed_by=body.changed_by if body else "")
    by = (body.changed_by if body else "") or risk.get("owner") or "system"
    store_add_comment(rid, author=by, body=f"Acceptance re-signed; expires {new_expiry}.")
    return {"risk": _acceptance_flag(updated or risk)}


@router.delete("/api/risks/{rid}")
def delete_risk_route(rid: str):
    if not delete_risk(rid):
        raise HTTPException(404, "Risk not found")
    return {"status": "deleted"}


@router.post("/api/risks/{rid}/comments")
def add_comment_route(rid: str, body: CommentBody):
    c = add_comment(rid, author=body.author, body=body.body)
    if not c:
        raise HTTPException(404, "Risk not found")
    return {"comment": c}
