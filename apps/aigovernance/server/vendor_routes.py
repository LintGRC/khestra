"""Vendor Intake routes for AI Governance — assess third-party AI providers."""

import os, json, csv, io, re, sys
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ─── Helpers ──────────────────────────────────────────

def _load(name: str):
    p = os.path.join(DATA_DIR, f"vendors_{name}.json")
    if not os.path.exists(p):
        return [] if name in ("activities",) else {}
    try:
        with open(p) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"WARNING: Corrupt vendor state file {p}, returning empty", file=sys.stderr)
        return [] if name in ("activities",) else {}

def _save(name: str, data):
    p = os.path.join(DATA_DIR, f"vendors_{name}.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, p)

def _id() -> str:
    return uuid4().hex[:12]

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _log(vendor_id: str, action: str, detail: str, actor: str = "system"):
    activities = _load("activities")
    if not activities:
        activities = {"items": {}}
    activities.setdefault("items", {})
    aid = f"act_{_id()}"
    activities["items"][aid] = {"id": aid, "vendorId": vendor_id, "action": action, "detail": detail, "actor": actor, "createdAt": _now()}
    _save("activities", activities)

# ─── Questionnaire ───────────────────────────────────

BUILTIN_QUESTIONNAIRE = {
    "id": "default",
    "name": "AI Vendor Security Intake",
    "version": "1.0",
    "sections": [
        {"id": "vendor_overview", "title": "Vendor Overview", "questions": [
            {"id": "a1", "question": "Describe the AI product/service", "type": "text", "weight": 20},
            {"id": "a2", "question": "What AI model(s) underpin this product?", "type": "text", "weight": 20},
            {"id": "a3", "question": "Describe deployment architecture", "type": "text", "weight": 20},
        ]},
        {"id": "data_handling", "title": "Data Handling & Privacy", "questions": [
            {"id": "c2", "question": "Is customer data used to train AI models?", "type": "select", "options": ["Yes", "No", "Optional opt-in"], "weight": 13},
            {"id": "c6", "question": "Is a DPA available?", "type": "select", "options": ["Yes", "No", "Modified DPA available"], "weight": 12},
        ]},
        {"id": "security_controls", "title": "Security Controls", "questions": [
            {"id": "d1", "question": "How is access control performed?", "type": "text", "weight": 15},
        ]},
        {"id": "contractual", "title": "Contractual Requirements", "questions": [
            {"id": "g1", "question": "DPA signed", "type": "select", "options": ["Yes", "No", "Modified"], "weight": 10},
            {"id": "g2", "question": "No training on customer data", "type": "select", "options": ["Yes", "No", "Modified"], "weight": 10},
        ]},
    ],
}

# Scoring weights
WEIGHTS = {"vendor_overview": 20, "data_handling": 35, "security_controls": 15, "contractual": 15}

def _score_response(response: dict) -> dict:
    findings = []
    cat_data = {}
    answers = {a["questionId"]: a.get("value") for a in response.get("answers", [])}
    for section in BUILTIN_QUESTIONNAIRE["sections"]:
        for q in section.get("questions", []):
            val = answers.get(q["id"])
            cat = section["id"]
            cat_data.setdefault(cat, {"total": 0, "earned": 0})
            if q["type"] == "yes_no":
                cat_data[cat]["total"] += q["weight"]
                if val is True or str(val).lower() in ("yes", "true"):
                    cat_data[cat]["earned"] += q["weight"]
                else:
                    findings.append({"questionId": q["id"], "severity": "high" if q["weight"] >= 20 else "medium", "description": f"{q['question']}: No"})
            elif q["type"] in ("select", "multi_select"):
                sel = str(val) if val else ""
                if cat == "contractual" and sel == "No":
                    cat_data[cat]["total"] += q["weight"]
                    findings.append({"questionId": q["id"], "severity": "high", "description": f"{q['question']}: No — needs negotiation"})
                elif cat == "contractual" and sel == "Modified":
                    cat_data[cat]["total"] += q["weight"]
                    cat_data[cat]["earned"] += round(q["weight"] * 0.5)
                elif cat == "contractual" and sel == "Yes":
                    cat_data[cat]["total"] += q["weight"]
                    cat_data[cat]["earned"] += q["weight"]
                elif cat == "data_handling" and q["id"] == "c2" and sel == "Yes":
                    cat_data[cat]["total"] += q["weight"]
                    findings.append({"questionId": q["id"], "severity": "high", "description": "Customer data used for training"})
                elif cat == "data_handling" and q["id"] == "c2" and sel == "Optional opt-in":
                    cat_data[cat]["total"] += q["weight"]
                    cat_data[cat]["earned"] += round(q["weight"] * 0.5)
                else:
                    cat_data[cat]["total"] += q["weight"]
                    cat_data[cat]["earned"] += q["weight"]
            elif q["type"] == "text":
                if not val or (isinstance(val, str) and len(val.strip()) < 20):
                    findings.append({"questionId": q["id"], "severity": "low", "description": f"{q['question']}: Vague"})
    cat_scores = []
    for cat, data in cat_data.items():
        score = round((data["earned"] / max(data["total"], 1)) * 100)
        cat_scores.append({"category": cat, "score": score, "level": "low" if score >= 80 else "medium" if score >= 60 else "high" if score >= 40 else "critical"})
    total_w = sum(WEIGHTS.values())
    overall = round(sum(cs["score"] * WEIGHTS.get(cs["category"], 10) for cs in cat_scores) / total_w) if cat_scores else 50
    return {"overallScore": overall, "overallLevel": "low" if overall >= 80 else "medium" if overall >= 60 else "high" if overall >= 40 else "critical", "categoryScores": cat_scores, "findings": findings}

# ─── Vendors CRUD ────────────────────────────────────

@router.get("/api/vendor-intake/vendors")
def list_vendors(q: str | None = None, status: str | None = None, tier: str | None = None, tag: str | None = None):
    vendors = list(_load("vendors").values())
    if q:
        q = q.lower()
        vendors = [v for v in vendors if q in (v.get("name", "") + " " + v.get("contactName", "") + " " + v.get("productService", "") + " " + v.get("contactEmail", "") + " " + " ".join(v.get("tags", []))).lower()]
    if status:
        vendors = [v for v in vendors if v.get("status") == status]
    if tier:
        vendors = [v for v in vendors if str(v.get("tier")) == str(tier)]
    if tag:
        vendors = [v for v in vendors if tag in v.get("tags", [])]
    for v in vendors:
        if v.get("accessToken"):
            v["has_accessToken"] = True
        v.pop("accessToken", None)
    return {"vendors": vendors, "total": len(vendors)}

@router.post("/api/vendor-intake/vendors")
def create_vendor(data: dict = {}):
    db = _load("vendors")
    vid = _id()
    vendor = {
        "id": vid, "name": data.get("name", ""), "contactName": data.get("contactName", ""),
        "contactEmail": data.get("contactEmail", ""), "contactPhone": data.get("contactPhone", ""),
        "website": data.get("website", ""), "productService": data.get("productService", ""),
        "category": data.get("category", ""), "aiServiceType": data.get("aiServiceType", ""), "tier": data.get("tier", ""),
        "status": data.get("status", "pending"), "riskScore": data.get("riskScore"), "riskLevel": data.get("riskLevel"),
        "accessToken": uuid4().hex, "tags": data.get("tags", []),
        "certType": None, "certExpiry": None, "createdAt": _now(),
        "reminderCount": 0, "dataResidency": data.get("dataResidency", []), "transferMechanism": data.get("transferMechanism", ""),
        "dpaInPlace": data.get("dpaInPlace", False), "certificates": data.get("certificates", []),
        "reviewDate": data.get("reviewDate", ""), "reviewOwner": data.get("reviewOwner", ""), "approvalStatus": data.get("approvalStatus", "draft"),
    }
    db[vid] = vendor
    _save("vendors", db)
    _log(vid, "created", f"Vendor {data.get('name', '')} created")
    return {"vendor": vendor}

@router.get("/api/vendor-intake/vendors/{vid}")
def get_vendor(vid: str):
    db = _load("vendors")
    if vid not in db:
        raise HTTPException(404, "Vendor not found")
    return {"vendor": db[vid]}

@router.patch("/api/vendor-intake/vendors/{vid}")
def update_vendor(vid: str, data: dict = {}):
    db = _load("vendors")
    if vid not in db:
        raise HTTPException(404, "Vendor not found")
    for k, v in data.items():
        if v is not None and k != "id":
            db[vid][k] = v
    _save("vendors", db)
    _log(vid, "updated", "Vendor updated")
    return {"vendor": db[vid]}

@router.delete("/api/vendor-intake/vendors/{vid}")
def delete_vendor(vid: str):
    db = _load("vendors")
    if vid not in db:
        raise HTTPException(404, "Vendor not found")
    del db[vid]
    _save("vendors", db)
    for coll in ("responses", "assessments", "remediations", "activities"):
        items = _load(coll)
        if isinstance(items, dict):
            items = {k: v for k, v in items.items() if v.get("vendorId") != vid}
            _save(coll, items)
    return {"ok": True}

# ─── Activity ────────────────────────────────────────

@router.get("/api/vendor-intake/vendors/{vid}/activity")
def list_activity(vid: str):
    activities = _load("activities")
    items = list(activities.get("items", {}).values())
    filtered = [a for a in items if a.get("vendorId") == vid]
    filtered.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    return {"activities": filtered}

# ─── Questionnaire ───────────────────────────────────

@router.get("/api/vendor-intake/questionnaire/{qid}")
def get_questionnaire(qid: str):
    return {"questionnaire": BUILTIN_QUESTIONNAIRE}

@router.post("/api/vendor-intake/questionnaire/draft")
def save_draft(data: dict = {}):
    responses = _load("responses")
    existing = None
    for r in list(responses.values()):
        if r.get("vendorId") == data.get("vendorId") and r.get("status") == "draft":
            existing = r; break
    if existing:
        existing["answers"] = data.get("answers", [])
        existing["updatedAt"] = _now()
    else:
        rid = _id()
        responses[rid] = {"id": rid, "questionnaireId": data.get("questionnaireId", "default"), "vendorId": data.get("vendorId", ""), "status": "draft", "answers": data.get("answers", []), "createdAt": _now()}
    _save("responses", responses)
    return {"ok": True}

@router.post("/api/vendor-intake/questionnaire/respond")
def submit_response(data: dict = {}):
    responses = _load("responses")
    existing = None
    for r in list(responses.values()):
        if r.get("vendorId") == data.get("vendorId"):
            existing = r; break
    if existing:
        existing["answers"] = data.get("answers", [])
        existing["status"] = "submitted"
        existing["submittedAt"] = _now()
    else:
        rid = _id()
        responses[rid] = {"id": rid, "questionnaireId": data.get("questionnaireId", "default"), "vendorId": data.get("vendorId", ""), "status": "submitted", "answers": data.get("answers", []), "submittedAt": _now(), "createdAt": _now()}
    _save("responses", responses)
    return {"ok": True}

# ─── Assess ─────────────────────────────────────────

@router.post("/api/vendor-intake/vendors/{vid}/assess")
def run_assessment(vid: str):
    vendors = _load("vendors")
    if vid not in vendors:
        raise HTTPException(404, "Vendor not found")
    responses = list(_load("responses").values())
    response = next((r for r in responses if r.get("vendorId") == vid and r.get("status") == "submitted"), None)
    if not response:
        raise HTTPException(400, "No submitted questionnaire response found")
    result = _score_response(response)
    assessments = _load("assessments")
    aid = _id()
    assessments[aid] = {"id": aid, "vendorId": vid, "responseId": response["id"], "overallScore": result["overallScore"], "overallLevel": result["overallLevel"], "categoryScores": result["categoryScores"], "findings": result["findings"], "summary": f"Score: {result['overallScore']} ({result['overallLevel']})", "createdAt": _now()}
    _save("assessments", assessments)
    remediations = _load("remediations")
    for f in result["findings"]:
        if f.get("severity") in ("high", "critical"):
            remediations[_id()] = {"id": _id(), "vendorId": vid, "assessmentId": aid, "description": f.get("description", ""), "priority": f.get("severity"), "status": "open", "createdAt": _now()}
    _save("remediations", remediations)
    vendors[vid]["riskScore"] = result["overallScore"]
    vendors[vid]["riskLevel"] = result["overallLevel"]
    vendors[vid]["status"] = "assessed"
    _save("vendors", vendors)
    _log(vid, "assessed", f"Score: {result['overallScore']} ({result['overallLevel']})")
    return {"assessment": assessments[aid]}

@router.get("/api/vendor-intake/vendors/{vid}/assessment")
def get_assessment(vid: str):
    assessments = list(_load("assessments").values())
    vendor_assessments = [a for a in assessments if a.get("vendorId") == vid]
    if not vendor_assessments:
        return {"assessment": None}
    vendor_assessments.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    return {"assessment": vendor_assessments[0]}

# ─── Remediations ───────────────────────────────────

@router.get("/api/vendor-intake/vendors/{vid}/remediations")
def list_remediations(vid: str):
    all_r = list(_load("remediations").values())
    return {"remediations": [r for r in all_r if r.get("vendorId") == vid]}

@router.patch("/api/vendor-intake/vendors/{vid}/remediations/{rid}")
def update_remediation(vid: str, rid: str, data: dict = {}):
    remediations = _load("remediations")
    if rid not in remediations:
        raise HTTPException(404, "Remediation not found")
    for k, v in data.items():
        if v is not None:
            remediations[rid][k] = v
    _save("remediations", remediations)
    return {"remediation": remediations[rid]}

# ─── Send Questionnaire, Remind, Clarify ─────────────

@router.post("/api/vendor-intake/vendors/{vid}/send-questionnaire")
def send_questionnaire(vid: str):
    vendors = _load("vendors")
    if vid not in vendors:
        raise HTTPException(404, "Vendor not found")
    vendors[vid]["status"] = "sent"
    _save("vendors", vendors)
    _log(vid, "questionnaire_sent", "Questionnaire sent")
    return {"ok": True}

@router.post("/api/vendor-intake/vendors/{vid}/remind")
def remind_vendor(vid: str):
    vendors = _load("vendors")
    if vid not in vendors:
        raise HTTPException(404, "Vendor not found")
    cnt = (vendors[vid].get("reminderCount") or 0) + 1
    vendors[vid]["reminderCount"] = cnt
    vendors[vid]["lastReminderAt"] = _now()
    level = "friendly" if cnt == 1 else "urgent" if cnt == 2 else "final"
    _save("vendors", vendors)
    _log(vid, "reminded", f"{level} reminder sent")
    return {"ok": True, "level": level, "count": cnt}

@router.post("/api/vendor-intake/vendors/{vid}/clarify")
def clarify_vendor(vid: str, data: dict = {}):
    _log(vid, "clarified", f"Clarification: {str(data.get('question', ''))[:60]}")
    return {"ok": True}

# ─── Cert Upload ─────────────────────────────────────

@router.post("/api/vendor-intake/vendors/{vid}/cert")
def upload_cert(vid: str, file: UploadFile = File(...)):
    vendors = _load("vendors")
    if vid not in vendors:
        raise HTTPException(404, "Vendor not found")
    data = file.file.read()
    text = data.decode("utf-8", errors="replace")
    cert_type = None
    for cert in ["SOC 2", "SOC 3", "ISO 27001", "ISO 42001", "HIPAA", "PCI DSS", "FedRAMP"]:
        if cert.lower() in text.lower():
            cert_type = cert; break
    dates = re.findall(r"(\d{4}-\d{2}-\d{2})", text)
    vendors[vid]["certType"] = cert_type
    vendors[vid]["certExpiry"] = max(dates) if dates else None
    vendors[vid]["certUploadedAt"] = _now()
    vendors[vid]["certFileName"] = file.filename
    _save("vendors", vendors)
    _log(vid, "cert_uploaded", f"Cert uploaded: {file.filename} ({cert_type or 'Unknown'})")
    return {"vendor": vendors[vid], "certType": cert_type}

# ─── Cross-Border ────────────────────────────────────

@router.get("/api/vendor-intake/vendors/{vid}/cross-border")
def cross_border(vid: str):
    vendors = _load("vendors")
    if vid not in vendors:
        raise HTTPException(404, "Vendor not found")
    PHRASE_TO_CODE = {"united states": "US", "usa": "US", "uk": "GB", "united kingdom": "GB", "germany": "DE", "france": "FR", "canada": "CA", "australia": "AU"}
    EEA = {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE","IS","LI","NO"}
    answers = ""
    for r in list(_load("responses").values()):
        if r.get("vendorId") == vid:
            for a in r.get("answers", []):
                if a.get("questionId") == "c4":
                    answers = str(a.get("value", ""))
    codes = set()
    lower = answers.lower()
    for phrase, code in PHRASE_TO_CODE.items():
        if phrase in lower:
            codes.add(code)
    for m in re.findall(r"\b[A-Z]{2}\b", answers):
        codes.add(m)
    codes = list(codes)
    non_eea = next((c for c in codes if c not in EEA), None)
    return {"hostingCountries": codes, "crossBorderRequired": bool(non_eea), "suggestedDestination": non_eea}

# ─── Findings CSV ────────────────────────────────────

@router.get("/api/vendor-intake/vendors/{vid}/findings-csv")
def findings_csv(vid: str):
    assessments = list(_load("assessments").values())
    va = [a for a in assessments if a.get("vendorId") == vid]
    if not va:
        return Response("No findings", media_type="text/csv")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["questionId", "severity", "description"])
    for f in max(va, key=lambda x: x.get("createdAt", "")).get("findings", []):
        w.writerow([f.get("questionId"), f.get("severity"), f.get("description")])
    return Response(buf.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=findings-{vid}.csv"})

# ─── Reports ─────────────────────────────────────────

@router.get("/api/vendor-intake/reports/csv")
def reports_csv():
    vendors = list(_load("vendors").values())
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "name", "status", "riskLevel", "riskScore", "certType", "certExpiry", "reminderCount"])
    for v in vendors:
        w.writerow([v.get("id"), v.get("name"), v.get("status"), v.get("riskLevel"), v.get("riskScore"), v.get("certType"), v.get("certExpiry"), v.get("reminderCount")])
    return Response(buf.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=vendor-intake-export.csv"})

# ─── Seed ─────────────────────────────────────────────

@router.post("/api/vendor-intake/seed")
def seed_data():
    vendors = _load("vendors")
    if vendors:
        return {"message": "Already seeded"}
    samples = [
        {"name": "Trident AI Solutions", "contactName": "Jane", "contactEmail": "jane@trident-ai.com", "productService": "AI model development and ML ops"},
        {"name": "Trident DataWorks", "contactName": "Bob", "contactEmail": "bob@tridentdata.com", "productService": "Secure data labeling and annotation"},
    ]
    for s in samples:
        vid = _id()
        s["id"] = vid
        s["accessToken"] = uuid4().hex
        s["status"] = "pending"
        s["createdAt"] = _now()
        s["reminderCount"] = 0
        vendors[vid] = s
    _save("vendors", vendors)
    return {"ok": True, "count": len(samples)}
