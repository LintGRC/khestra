import io, csv, json
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import re

router = APIRouter()


class VendorCreateBody(BaseModel):
    name: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    website: str = ""
    product_service: str = ""
    category: str = ""
    ai_service_type: str = ""
    tier: str = ""
    tags: list[str] = []
    org_id: str = ""
    workspace_id: str = ""
    frameworks: list[str] = []
    data_residency: list[str] = []
    transfer_mechanism: str = ""
    dpa_in_place: bool = False
    handles_cui: bool = False
    cmmc_level: str = ""
    sprs_score: Optional[int] = None
    flow_down_clause_signed: str = ""
    cui_categories: list[str] = []
    last_assessment_date: str = ""
    soc_report_type: str = ""
    soc_report_opinion: str = ""
    soc_report_coverage_start: str = ""
    soc_report_coverage_end: str = ""
    next_review_due: str = ""
    review_date: str = ""
    data_types: list[str] = []


class LinkFrameworkBody(BaseModel):
    framework_id: str = ""


class VendorUpdateBody(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    product_service: Optional[str] = None
    category: Optional[str] = None
    ai_service_type: Optional[str] = None
    tier: Optional[str] = None
    tags: Optional[list[str]] = None
    status: Optional[str] = None
    data_residency: Optional[list[str]] = None
    transfer_mechanism: Optional[str] = None
    dpa_in_place: Optional[bool] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    handles_cui: Optional[bool] = None
    cmmc_level: Optional[str] = None
    sprs_score: Optional[int] = None
    flow_down_clause_signed: Optional[str] = None
    cui_categories: Optional[list[str]] = None
    last_assessment_date: Optional[str] = None
    soc_report_type: Optional[str] = None
    soc_report_opinion: Optional[str] = None
    soc_report_coverage_start: Optional[str] = None
    soc_report_coverage_end: Optional[str] = None
    next_review_due: Optional[str] = None
    review_date: Optional[str] = None
    data_types: Optional[list[str]] = None


class AnalyzeBody(BaseModel):
    answers: list[dict] = []


class ClarifyBody(BaseModel):
    question: str = ""
    notes: str = ""


class ResponseBody(BaseModel):
    vendor_id: str = ""
    answers: list[dict] = []
    questionnaire_id: str = "default"


# ─── Questionnaire ─────────────────────────────


@router.get("/api/vendors/questionnaire/{qid}")
def get_questionnaire(qid: str = "default"):
    from .questionnaire import get_questionnaire
    return {"questionnaire": get_questionnaire(qid)}


# ─── Seed ────────────────────────────────────


@router.post("/api/vendors/seed")
def seed_vendors(force: bool = Query(False)):
    from .store import seed_data
    count = seed_data(force=force)
    return {"ok": True, "count": count}


# ─── CSV Export ────────────────────────────────


@router.get("/api/vendors/export/csv")
def export_vendors_csv():
    from .store import list_vendors, export_vendors_csv as _csv
    from fastapi.responses import Response
    vendors = list_vendors()
    csv_data = _csv(vendors)
    return Response(csv_data, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=vendors.csv"})


# ─── Vendors ───────────────────────────────────


@router.get("/api/vendors")
def list_vendors(org_id: Optional[str] = Query(None), framework_id: Optional[str] = Query(None)):
    from .store import list_vendors
    return {"vendors": list_vendors(org_id=org_id, framework_id=framework_id)}


@router.post("/api/vendors")
def create_vendor(body: VendorCreateBody):
    from .store import create_vendor
    return {"vendor": create_vendor(
        name=body.name,
        contact_name=body.contact_name,
        contact_email=body.contact_email,
        contact_phone=body.contact_phone,
        website=body.website,
        product_service=body.product_service,
        category=body.category,
        ai_service_type=body.ai_service_type,
        tier=body.tier,
        tags=body.tags,
        org_id=body.org_id,
        workspace_id=body.workspace_id,
        frameworks=body.frameworks,
        data_residency=body.data_residency,
        transfer_mechanism=body.transfer_mechanism,
        dpa_in_place=body.dpa_in_place,
        handles_cui=body.handles_cui,
        cmmc_level=body.cmmc_level,
        sprs_score=body.sprs_score,
        flow_down_clause_signed=body.flow_down_clause_signed,
        cui_categories=body.cui_categories,
        last_assessment_date=body.last_assessment_date,
        soc_report_type=body.soc_report_type,
        soc_report_opinion=body.soc_report_opinion,
        soc_report_coverage_start=body.soc_report_coverage_start,
        soc_report_coverage_end=body.soc_report_coverage_end,
        next_review_due=body.next_review_due,
        review_date=body.review_date,
    )}


@router.get("/api/vendors/{vid}")
def get_vendor(vid: str):
    from .store import get_vendor
    v = get_vendor(vid)
    if not v:
        raise HTTPException(404, "Vendor not found")
    return {"vendor": v}


@router.patch("/api/vendors/{vid}")
def update_vendor(vid: str, body: VendorUpdateBody):
    from .store import update_vendor
    v = update_vendor(vid, **body.model_dump(exclude_none=True))
    if not v:
        raise HTTPException(404, "Vendor not found")
    return {"vendor": v}


@router.delete("/api/vendors/{vid}")
def delete_vendor(vid: str):
    from .store import delete_vendor
    if not delete_vendor(vid):
        raise HTTPException(404, "Vendor not found")
    return {"status": "deleted"}


# ─── Framework Linking ────────────────────────────


@router.post("/api/vendors/{vid}/frameworks")
def link_framework(vid: str, body: LinkFrameworkBody):
    from .store import link_framework
    v = link_framework(vid, body.framework_id)
    if not v:
        raise HTTPException(404, "Vendor not found")
    return {"vendor": v}


@router.delete("/api/vendors/{vid}/frameworks/{framework_id}")
def unlink_framework(vid: str, framework_id: str):
    from .store import unlink_framework
    v = unlink_framework(vid, framework_id)
    if not v:
        raise HTTPException(404, "Vendor not found")
    return {"vendor": v}


# ─── Questionnaire Response ──────────────────────


def _verify_vendor_token(vendor_id: str, token: str | None) -> bool:
    if not token:
        return False
    from .store import get_vendor
    v = get_vendor(vendor_id)
    if not v:
        return False
    return v.get("access_token") == token


@router.get("/api/vendors/{vid}/response")
def get_vendor_response(vid: str, token: Optional[str] = Query(None)):
    from .store import get_response_by_vendor
    if token and not _verify_vendor_token(vid, token):
        raise HTTPException(403, "Invalid token")
    resp = get_response_by_vendor(vid)
    if not resp:
        return {"response": None}
    return {"response": resp}


@router.post("/api/vendors/response/draft")
def save_draft(body: ResponseBody, token: Optional[str] = Query(None)):
    from .store import save_draft_response, update_vendor
    if token and not _verify_vendor_token(body.vendor_id, token):
        raise HTTPException(403, "Invalid token")
    resp = save_draft_response(body.vendor_id, body.answers, body.questionnaire_id)
    update_vendor(body.vendor_id, status="in_progress")
    return {"response": resp}


@router.post("/api/vendors/response/submit")
def submit_response(body: ResponseBody, token: Optional[str] = Query(None)):
    from .store import submit_response, update_vendor, _log
    if token and not _verify_vendor_token(body.vendor_id, token):
        raise HTTPException(403, "Invalid token")
    resp = submit_response(body.vendor_id, body.answers, body.questionnaire_id)
    update_vendor(body.vendor_id, status="submitted")
    _log(body.vendor_id, "submitted", "Questionnaire submitted by vendor")
    return {"response": resp}


@router.post("/api/vendors/questionnaire/analyze")
def analyze_questionnaire_answers(body: AnalyzeBody):
    from .questionnaire import analyze_answers
    return analyze_answers(body.answers)


@router.post("/api/vendors/questionnaire/upload-soc2")
async def upload_soc2_prefill(vendor_id: str = Form(...), file: UploadFile = File(...)):
    from .store import get_vendor, update_vendor, _log
    from .questionnaire import prefill_from_soc2
    v = get_vendor(vendor_id)
    if not v:
        raise HTTPException(404, "Vendor not found")
    data = await file.read()
    text = data.decode("utf-8", errors="replace")
    prefilled = prefill_from_soc2(text)
    _log(vendor_id, "soc2_uploaded", f"SOC 2 uploaded: {file.filename}")
    return {"prefilled_answers": prefilled, "filename": file.filename}


# ─── Assessment ─────────────────────────────────


@router.post("/api/vendors/{vid}/assess")
def run_assessment(vid: str):
    from .store import get_vendor, list_responses, create_assessment, _log
    from .questionnaire import score_response
    from datetime import datetime, timezone

    v = get_vendor(vid)
    if not v:
        raise HTTPException(404, "Vendor not found")

    responses = list_responses(vendor_id=vid)
    submitted = [r for r in responses if r.get("status") == "submitted"]
    if not submitted:
        raise HTTPException(400, "No submitted questionnaire response found")

    response = submitted[0]
    result = score_response(response.get("answers", []))

    assessment = create_assessment(
        vendor_id=vid,
        response_id=response["id"],
        overall_score=result["overallScore"],
        overall_level=result["overallLevel"],
        category_scores=result["categoryScores"],
        findings=result["findings"],
    )

    try:
        from evidence_hub.store import upload_evidence_file, map_evidence
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        payload = {
            "vendor_id": vid,
            "vendor_name": v.get("name", ""),
            "overall_score": result["overallScore"],
            "overall_level": result["overallLevel"],
            "category_scores": result["categoryScores"],
            "findings": result["findings"],
            "assessed_at": now,
            "source": "vendor-intake",
        }
        payload_bytes = json.dumps(payload, indent=2).encode("utf-8")
        checksum = __import__("hashlib").sha256(payload_bytes).hexdigest()
        ev = upload_evidence_file(
            name=f"Vendor Assessment: {v.get('name', '')}",
            file_data=payload_bytes,
            filename=f"vendor_{vid}_assessment.json",
            description=f"Risk assessment for vendor {v.get('name', '')} — score {result['overallScore']}/100 ({result['overallLevel']})",
            tags=["vendor-assessment", v.get("name", ""), vid],
            uploaded_by=f"vendor-intake:{vid}",
            mime_type="application/json",
        )
        if ev.get("id"):
            for fw_id in (v.get("frameworks") or []):
                if fw_id in ("SOC2", "AIGov", "CMMC"):
                    map_evidence(ev["id"], fw_id, "vendor-intake", mapped_by=f"vendor-intake:{vid}")
    except Exception:
        pass

    _log(vid, "assessed", f"Assessment completed — score {result['overallScore']}/100 ({result['overallLevel']})")
    return {"assessment": assessment}


@router.get("/api/vendors/{vid}/assessment")
def get_assessment(vid: str):
    from .store import get_assessment_by_vendor
    a = get_assessment_by_vendor(vid)
    return {"assessment": a}


# ─── Remediations ────────────────────────────────


@router.get("/api/vendors/{vid}/remediations")
def list_remediations(vid: str):
    from .store import list_remediations
    return {"remediations": list_remediations(vendor_id=vid)}


class RemediationUpdateBody(BaseModel):
    status: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[str] = None


@router.patch("/api/vendors/{vid}/remediations/{rid}")
def update_remediation(vid: str, rid: str, body: RemediationUpdateBody):
    from .store import update_remediation
    r = update_remediation(rid, **body.model_dump(exclude_none=True))
    if not r:
        raise HTTPException(404, "Remediation not found")
    return {"remediation": r}


# ─── Communications ─────────────────────────────


@router.post("/api/vendors/{vid}/send-questionnaire")
def send_questionnaire(vid: str):
    from .store import get_vendor, update_vendor, _log
    v = get_vendor(vid)
    if not v:
        raise HTTPException(404, "Vendor not found")
    token = v.get("access_token", uuid4().hex)
    update_vendor(vid, status="sent")
    _log(vid, "questionnaire_sent", "Questionnaire sent with magic link")
    return {"status": "sent", "link": f"/questionnaire/{vid}?token={token}"}


@router.post("/api/vendors/{vid}/remind")
def remind_vendor(vid: str):
    from .store import get_vendor, update_vendor, _log
    v = get_vendor(vid)
    if not v:
        raise HTTPException(404, "Vendor not found")
    cnt = (v.get("reminder_count") or 0) + 1
    update_vendor(vid, reminder_count=cnt)
    level = "friendly" if cnt == 1 else "urgent" if cnt == 2 else "final"
    _log(vid, "reminded", f"{level} reminder sent")
    return {"ok": True, "level": level, "count": cnt}


# ─── Cert Upload ────────────────────────────────


@router.post("/api/vendors/{vid}/cert")
async def upload_cert(vid: str, file: UploadFile = File(...)):
    from uuid import uuid4
    from .store import get_vendor, update_vendor, _log
    from .models import VendorCertificate
    v = get_vendor(vid)
    if not v:
        raise HTTPException(404, "Vendor not found")

    data = await file.read()
    text = data.decode("utf-8", errors="replace")

    cert_type = None
    for cert in ["SOC 2", "SOC 3", "ISO 27001", "ISO 42001", "HIPAA", "PCI DSS", "FedRAMP"]:
        if cert.lower() in text.lower():
            cert_type = cert
            break

    cert = VendorCertificate(
        id=uuid4().hex[:12],
        type=cert_type or "Unknown",
        filename=file.filename or "uploaded",
        uploaded_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    )
    certs = v.get("certificates", [])
    certs.append(cert.to_dict())
    update_vendor(vid, certificates=certs)

    _log(vid, "cert_uploaded", f"Cert uploaded: {file.filename} ({cert_type or 'Unknown'})")
    v = get_vendor(vid)
    return {"vendor": v, "cert_type": cert_type}


# ─── Activities ───────────────────────────────


@router.get("/api/vendors/{vid}/activity")
def get_activities(vid: str):
    from .store import list_activities
    return {"activities": list_activities(vendor_id=vid)}


# ─── Cross-Border ─────────────────────────────


@router.get("/api/vendors/{vid}/cross-border")
def cross_border_check(vid: str):
    from .store import get_vendor, list_responses
    v = get_vendor(vid)
    if not v:
        raise HTTPException(404, "Vendor not found")
    responses = list_responses(vendor_id=vid)
    answer_map = {}
    for r in responses:
        for a in r.get("answers", []):
            answer_map[a.get("id", "")] = a.get("value", "")
    countries = answer_map.get("q4", "")
    eea_countries = [
        "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
        "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
        "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein",
        "Lithuania", "Luxembourg", "Malta", "Netherlands", "Norway", "Poland",
        "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
    ]
    cross_border = countries not in ("US Only", "EU/EEA") and countries != ""
    return {
        "hosting_countries": countries,
        "cross_border_required": cross_border,
        "suggested_destination": "EU Standard Contractual Clauses" if cross_border else None,
        "hosting_in_eea": countries in ("EU/EEA",) or countries in eea_countries,
    }


# ─── Clarify ────────────────────────────────────


@router.post("/api/vendors/{vid}/clarify")
def clarify_vendor(vid: str, body: ClarifyBody = ClarifyBody()):
    from .store import _log
    _log(vid, "clarified", f"Clarification: {body.question or body.notes}", detail=str(body.notes or body.question))
    return {"ok": True}


# ─── Create Remediation ─────────────────────────


class RemediationCreateBody(BaseModel):
    assessment_id: str = ""
    description: str = ""
    priority: str = "medium"
    status: str = "open"
    owner: str = ""
    due_date: str = ""


@router.post("/api/vendors/{vid}/remediations")
def create_remediation(vid: str, body: RemediationCreateBody):
    from .store import create_remediation, get_vendor
    v = get_vendor(vid)
    if not v:
        raise HTTPException(404, "Vendor not found")
    return {"remediation": create_remediation(
        vendor_id=vid,
        assessment_id=body.assessment_id,
        description=body.description,
        priority=body.priority,
        status=body.status,
        owner=body.owner,
        due_date=body.due_date,
    )}


@router.get("/api/vendors/due-review")
def get_due_for_review():
    from .review_reminders import get_vendors_due_review
    due = get_vendors_due_review()
    return {"vendors": due, "count": len(due)}
