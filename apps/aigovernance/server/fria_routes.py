"""FRIA (Fundamental Rights Impact Assessment) routes for AI Governance."""

import os, json, csv, io, sys
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVIDENCE_DIR = os.path.join(DATA_DIR, "fria_evidence")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".xlsx", ".csv", ".txt", ".md"}
MAX_EVIDENCE_MB = 25

# ─── Helpers ──────────────────────────────────────────

def _load() -> dict:
    p = os.path.join(DATA_DIR, "frias.json")
    if not os.path.exists(p):
        return {}
    try:
        with open(p) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"WARNING: Corrupt FRIA file {p}, returning empty", file=sys.stderr)
        return {}

def _save(data: dict):
    p = os.path.join(DATA_DIR, "frias.json")
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, p)

def _id() -> str:
    return uuid4().hex[:12]

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _log(fria: dict, action: str, detail: str = ""):
    fria.setdefault("activity_log", []).append({"action": action, "detail": detail, "timestamp": _now(), "actor": "system"})

# ─── Pydantic ─────────────────────────────────────────

class FRIACreate(BaseModel):
    system_name: str
    system_description: str = ""
    system_purpose: str = ""
    deployer_entity: str = ""
    developer_entity: str = ""
    risk_classification: str = "unclassified"
    affected_rights: list[str] = []
    impact_description: str = ""
    affected_groups: str = ""
    geography: list[str] = []
    technical_measures: str = ""
    organizational_measures: str = ""
    oversight_measures: str = ""
    model_id: str = ""
    use_frequency: str = ""
    risk_remediation: str = ""
    complaint_mechanism: str = ""

# ─── CRUD ─────────────────────────────────────────────

@router.post("/api/fria")
def create_fria(data: FRIACreate):
    db = _load()
    fid = _id()
    now = _now()
    record = data.model_dump()
    record["id"] = fid
    record["status"] = "draft"
    record["created_at"] = now
    record["updated_at"] = now
    record["activity_log"] = [{"action": "created", "detail": "FRIA created", "timestamp": now, "actor": "system"}]
    record["comments"] = []
    record["evidence"] = []
    record["risk_assessments"] = []
    db[fid] = record
    _save(db)
    return {"id": fid}

@router.get("/api/frias")
def list_frias(status: str = Query(None), q: str = Query(None), limit: int = Query(100), offset: int = Query(0)):
    items = list(_load().values())
    if status:
        items = [i for i in items if i.get("status") == status]
    if q:
        ql = q.lower()
        items = [i for i in items if ql in i.get("system_name", "").lower()]
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"frias": items[offset:offset + limit], "total": len(items)}

@router.get("/api/fria/{fid}")
def get_fria(fid: str):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    return {"fria": db[fid]}

@router.patch("/api/fria/{fid}")
def update_fria(fid: str, data: dict = {}):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    for k, v in data.items():
        if v is not None and k not in ("id", "created_at"):
            db[fid][k] = v
    db[fid]["updated_at"] = _now()
    _log(db[fid], "updated", "FRIA fields updated")
    _save(db)
    return {"fria": db[fid]}

@router.delete("/api/fria/{fid}")
def delete_fria(fid: str):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    del db[fid]
    _save(db)
    return {"ok": True}

@router.post("/api/fria/{fid}/copy")
def copy_fria(fid: str):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    src = db[fid]
    nid = _id()
    now = _now()
    copy = {k: v for k, v in src.items() if k not in ("id", "created_at", "updated_at", "activity_log", "comments", "evidence")}
    copy["id"] = nid
    copy["status"] = "draft"
    copy["system_name"] = f"{copy.get('system_name', '')} (Copy)"
    copy["created_at"] = now
    copy["updated_at"] = now
    copy["activity_log"] = [{"action": "copied", "detail": f"Copied from {fid}", "timestamp": now, "actor": "system"}]
    copy["comments"] = []
    copy["evidence"] = []
    db[nid] = copy
    _save(db)
    return {"id": nid}

# ─── Approval Workflow ────────────────────────────────

@router.post("/api/fria/{fid}/submit")
def submit_fria(fid: str):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    db[fid]["status"] = "submitted"
    _log(db[fid], "submitted", "Submitted for review")
    db[fid]["updated_at"] = _now()
    _save(db)
    return {"fria": db[fid]}

@router.post("/api/fria/{fid}/approve")
def approve_fria(fid: str, data: dict = {}):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    db[fid]["status"] = "approved"
    db[fid]["reviewed_by"] = data.get("reviewed_by", "")
    db[fid]["reviewed_at"] = _now()
    db[fid]["review_comment"] = data.get("comment", "")
    _log(db[fid], "approved", f"Approved by {data.get('reviewed_by', 'unknown')}")
    db[fid]["updated_at"] = _now()
    _save(db)
    return {"fria": db[fid]}

@router.post("/api/fria/{fid}/reject")
def reject_fria(fid: str, data: dict = {}):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    db[fid]["status"] = "rejected"
    db[fid]["reviewed_by"] = data.get("reviewed_by", "")
    db[fid]["reviewed_at"] = _now()
    db[fid]["review_comment"] = data.get("comment", "")
    _log(db[fid], "rejected", f"Rejected by {data.get('reviewed_by', 'unknown')}")
    db[fid]["updated_at"] = _now()
    _save(db)
    return {"fria": db[fid]}

# ─── Comments ────────────────────────────────────────

@router.post("/api/fria/{fid}/comments")
def add_comment(fid: str, data: dict = {}):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    comment = {
        "id": _id(),
        "author": data.get("author", ""),
        "text": data.get("text", ""),
        "created_at": _now(),
    }
    db[fid].setdefault("comments", []).append(comment)
    _log(db[fid], "comment_added", f"Comment by {data.get('author', 'unknown')}")
    db[fid]["updated_at"] = _now()
    _save(db)
    return {"comment": comment}

# ─── Evidence ─────────────────────────────────────────

@router.post("/api/fria/{fid}/evidence")
def upload_evidence(fid: str, file: UploadFile = File(...), label: str = Form("")):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    ext = os.path.splitext(file.filename or "file")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {ext} not allowed")
    data = file.file.read()
    if len(data) > MAX_EVIDENCE_MB * 1024 * 1024:
        raise HTTPException(400, f"File exceeds {MAX_EVIDENCE_MB}MB limit")
    evd = os.path.join(EVIDENCE_DIR, fid)
    os.makedirs(evd, exist_ok=True)
    eid = _id()
    fname = f"{eid}{ext}"
    with open(os.path.join(evd, fname), "wb") as f:
        f.write(data)
    entry = {"id": eid, "filename": file.filename or fname, "label": label or file.filename or fname, "size": len(data), "uploaded_at": _now()}
    db[fid].setdefault("evidence", []).append(entry)
    _log(db[fid], "evidence_uploaded", f"Uploaded: {file.filename}")
    db[fid]["updated_at"] = _now()
    _save(db)
    return {"evidence": entry}

@router.get("/api/fria/{fid}/evidence/{eid}")
def download_evidence(fid: str, eid: str):
    evd = os.path.join(EVIDENCE_DIR, fid)
    if not os.path.exists(evd):
        raise HTTPException(404, "Evidence not found")
    for fname in os.listdir(evd):
        if fname.startswith(eid):
            with open(os.path.join(evd, fname), "rb") as f:
                return Response(f.read(), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={fname}"})
    raise HTTPException(404, "Evidence not found")

@router.delete("/api/fria/{fid}/evidence/{eid}")
def delete_evidence(fid: str, eid: str):
    db = _load()
    if fid not in db:
        raise HTTPException(404, "FRIA not found")
    db[fid]["evidence"] = [e for e in db[fid].get("evidence", []) if e["id"] != eid]
    evd = os.path.join(EVIDENCE_DIR, fid)
    for fname in os.listdir(evd) if os.path.exists(evd) else []:
        if fname.startswith(eid):
            os.remove(os.path.join(evd, fname))
            break
    _log(db[fid], "evidence_deleted", f"Deleted: {eid}")
    db[fid]["updated_at"] = _now()
    _save(db)
    return {"ok": True}

# ─── Stats ────────────────────────────────────────────

@router.get("/api/frias/stats")
def get_stats():
    items = list(_load().values())
    return {
        "total": len(items),
        "by_status": {s: len([i for i in items if i.get("status") == s]) for s in set(i.get("status", "unknown") for i in items)},
        "approved": len([i for i in items if i.get("status") == "approved"]),
        "draft": len([i for i in items if i.get("status") == "draft"]),
        "submitted": len([i for i in items if i.get("status") == "submitted"]),
    }

@router.get("/api/frias/dashboard")
def get_dashboard():
    items = list(_load().values())
    return {
        "total": len(items),
        "by_status": {s: len([i for i in items if i.get("status") == s]) for s in set(i.get("status", "unknown") for i in items)},
        "pending_review": len([i for i in items if i.get("status") == "submitted"]),
    }

# ─── Notifications ────────────────────────────────────

@router.get("/api/frias/notifications")
def get_notifications():
    items = list(_load().values())
    notes = []
    for fr in items:
        for act in fr.get("activity_log", []):
            notes.append({"fria_id": fr["id"], "fria_name": fr.get("system_name", ""), "timestamp": act["timestamp"], "action": act["action"], "detail": act.get("detail", "")})
    notes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"notifications": notes[:50]}

# ─── Reminders ────────────────────────────────────────

@router.get("/api/frias/reminders")
def get_reminders():
    now = datetime.now(timezone.utc)
    items = list(_load().values())
    overdue, upcoming = [], []
    for fr in items:
        rd = fr.get("review_date")
        if not rd:
            continue
        try:
            rd_dt = datetime.fromisoformat(rd.replace("Z", "+00:00"))
            days = (rd_dt - now).days
            info = {"id": fr["id"], "name": fr.get("system_name", ""), "review_date": rd, "days_left": days}
            if days < 0:
                overdue.append(info)
            elif days <= 30:
                upcoming.append(info)
        except Exception:
            pass
    return {"overdue": overdue, "upcoming": upcoming}

# ─── Audit ────────────────────────────────────────────

@router.get("/api/frias/audit")
def get_audit():
    items = list(_load().values())
    entries = []
    for fr in items:
        for act in fr.get("activity_log", []):
            entries.append({"fria_id": fr["id"], "fria_name": fr.get("system_name", ""), **act})
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"entries": entries[:200]}

# ─── Export ───────────────────────────────────────────

@router.get("/api/frias/export/csv")
def export_csv():
    items = list(_load().values())
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "system_name", "status", "risk_classification", "deployer", "developer", "created_at", "reviewed_by"])
    for fr in items:
        w.writerow([fr.get("id"), fr.get("system_name"), fr.get("status"), fr.get("risk_classification"), fr.get("deployer_entity"), fr.get("developer_entity"), fr.get("created_at"), fr.get("reviewed_by")])
    return Response(buf.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=frias-export.csv"})

# ─── Seed ─────────────────────────────────────────────

@router.post("/api/frias/seed")
def seed_data():
    db = _load()
    if db:
        return {"message": "Data already seeded"}
    now = _now()
    samples = [
        {"system_name": "Trident Hiring Intelligence", "system_description": "AI-powered resume screening for cleared positions", "deployer_entity": "Trident Defense Systems", "developer_entity": "Trident Defense Systems", "risk_classification": "high", "status": "approved", "affected_rights": ["Right to fair treatment", "Right to privacy"], "impact_description": "Potential bias in candidate selection for cleared roles"},
        {"system_name": "Trident Mission Support Assistant", "system_description": "GPT-4o assistant for mission planning and threat analysis", "deployer_entity": "Trident Defense Systems", "developer_entity": "Trident Defense Systems", "risk_classification": "limited", "status": "draft", "affected_rights": ["Right to information"], "impact_description": "Transparency of AI-assisted mission planning"},
    ]
    for s in samples:
        sid = _id()
        s["id"] = sid
        s["created_at"] = now
        s["updated_at"] = now
        s["comments"] = []
        s["evidence"] = []
        s["activity_log"] = [{"action": "created", "detail": "Seeded", "timestamp": now, "actor": "system"}]
        s["risk_assessments"] = []
        db[sid] = s
    _save(db)
    return {"ok": True, "count": len(samples)}
