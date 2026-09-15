from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import Response
from typing import Optional
import csv
import io
import json
import hashlib
import zipfile
from pathlib import Path

router = APIRouter()

PLAYBOOKS = {
    "prompt_injection": {
        "title": "Prompt Injection / Jailbreaking Response",
        "sections": {
            "Immediate (0-1h)": ["Isolate the affected model endpoint", "Revoke exposed API keys", "Audit conversation logs for scope"],
            "Containment": ["Apply updated prompt guardrails", "Deploy input sanitization filters", "Rate-limit affected endpoint"],
            "Regulatory/Compliance": ["Assess data exposure scope", "Notify security team", "File incident report per EU AI Act Art. 73"],
        },
    },
    "model_poisoning": {
        "title": "Model Poisoning / Training Data Corruption Response",
        "sections": {
            "Immediate (0-1h)": ["Suspend model inference", "Quarantine affected model version", "Alert data pipeline team"],
            "Containment": ["Roll back to last validated checkpoint", "Audit training data provenance", "Review access logs on training pipeline"],
            "Regulatory/Compliance": ["Assess downstream impact", "Notify affected customers", "Prepare regulator notification if critical"],
        },
    },
    "model_drift": {
        "title": "Severe Model Drift / Hallucination Response",
        "sections": {
            "Immediate (0-1h)": ["Compare current metrics to baseline", "Check training data pipeline for changes", "Flag anomalous outputs"],
            "Containment": ["Roll back to last validated model version", "Investigate root cause of data drift", "Update monitoring thresholds"],
            "Regulatory/Compliance": ["Document accuracy impact", "Assess user-facing effects", "File incident report if systemic"],
        },
    },
    "data_exfiltration": {
        "title": "Unintended PII / Sensitive Data Exfiltration Response",
        "sections": {
            "Immediate (0-1h)": ["Immediately block the affected model", "Trace all outputs from the incident window", "Identify exposed data types"],
            "Containment": ["Deploy PII scrubbing filters", "Audit training and inference data", "Engage legal/compliance team"],
            "Regulatory/Compliance": ["Notify affected users/data subjects", "Notify regulator if required (GDPR Art. 33)", "Conduct post-mortem"],
        },
    },
    "systemic_bias": {
        "title": "Systemic Bias / Discriminatory Output Response",
        "sections": {
            "Immediate (0-1h)": ["Suspend model for affected demographic", "Flag all outputs from incident window", "Alert ethics committee"],
            "Containment": ["Audit training data for representation gaps", "Run fairness evaluation on revised model", "Document bias mitigation steps"],
            "Regulatory/Compliance": ["Review with ethics committee", "Prepare bias impact assessment", "Obtain sign-off before redeployment"],
        },
    },
    "security_breach": {
        "title": "Security Breach / Unauthorized Access Response",
        "sections": {
            "Immediate (0-1h)": ["Revoke compromised credentials", "Isolate affected systems", "Activate incident response team"],
            "Containment": ["Rotate all API keys and secrets", "Audit access logs for scope", "Patch vulnerability vector"],
            "Regulatory/Compliance": ["Assess data breach notification requirements", "Notify regulator within 72h if personal data involved", "File breach report"],
        },
    },
    "agent_failure": {
        "title": "Autonomous Agent Failure Response",
        "sections": {
            "Immediate (0-1h)": ["Kill all agent processes", "Revoke tool access for affected agent", "Review agent action log"],
            "Containment": ["Audit agent decision trace", "Update tool-use guardrails", "Implement human-in-the-loop checkpoints"],
            "Regulatory/Compliance": ["Assess real-world impact of agent actions", "Notify affected parties", "Update risk assessment documentation"],
        },
    },
    "other": {
        "title": "Other AI-Specific Failure Response",
        "sections": {
            "Immediate (0-1h)": ["Document observed behavior", "Isolate affected system components", "Engage relevant technical team"],
            "Containment": ["Implement temporary mitigation", "Gather forensic data", "Escalate to security/compliance"],
            "Regulatory/Compliance": ["Assess EU AI Act applicability", "Determine notification requirements", "File incident report"],
        },
    },
}


@router.get("/api/incidents")
def list_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    failure_mode: Optional[str] = Query(None),
    control_id: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    overdue: bool = Query(False),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
):
    from .store import list_incidents
    items, total = list_incidents(status=status, severity=severity, failure_mode=failure_mode, control_id=control_id, q=q, limit=limit, offset=offset, overdue=overdue, sort_by=sort_by, sort_order=sort_order)
    return {"incidents": items, "total": total}


@router.post("/api/incidents")
def create_incident(data: dict):
    from .store import create_incident
    inc = create_incident(
        title=data.get("title", ""),
        description=data.get("description", ""),
        failure_mode=data.get("failure_mode", ""),
        severity=data.get("severity", "medium"),
        model_id=data.get("model_id", ""),
        model_name=data.get("model_name", ""),
        system_id=data.get("system_id", ""),
        reporter_name=data.get("reporter_name", ""),
        impact_description=data.get("impact_description", ""),
        affected_inference_pct=data.get("affected_inference_pct", 0),
        total_users_exposed=data.get("total_users_exposed", 0),
        downstream_applications=data.get("downstream_applications", ""),
        source=data.get("source", ""),
        external_id=data.get("external_id", ""),
        control_id=data.get("control_id", ""),
    )
    return {"incident": inc}


@router.get("/api/incidents/stats")
def incident_stats():
    from .store import get_stats
    return get_stats()


@router.post("/api/incidents/seed")
def seed_incidents():
    from .store import seed_incidents
    results = seed_incidents()
    return {"incidents": results, "count": len(results)}


@router.get("/api/incidents/{iid}")
def get_incident(iid: str):
    from .store import get_incident
    inc = get_incident(iid)
    if not inc:
        raise HTTPException(404, "Incident not found")
    return {"incident": inc}


@router.patch("/api/incidents/{iid}")
def update_incident(iid: str, data: dict):
    from .store import update_incident
    inc = update_incident(iid, data)
    if not inc:
        raise HTTPException(404, "Incident not found")
    return {"incident": inc}


@router.delete("/api/incidents/{iid}")
def delete_incident(iid: str):
    from .store import delete_incident
    if not delete_incident(iid):
        raise HTTPException(404, "Incident not found")
    return {"ok": True}


@router.post("/api/incidents/bulk")
def bulk_incident_ops(data: dict):
    from .store import bulk_incident_ops
    results = bulk_incident_ops(data.get("ids", []), data.get("action", ""), value=data.get("value", ""))
    return {"incidents": results, "count": len(results)}


@router.post("/api/incidents/{iid}/transition")
def transition_incident(iid: str, data: dict):
    from .store import transition_incident
    inc = transition_incident(iid, data.get("status", ""), detail=data.get("detail", ""), rca_data=data.get("rca"))
    if not inc:
        raise HTTPException(404, "Incident not found")
    return {"incident": inc}


@router.post("/api/incidents/{iid}/notify-regulator")
def notify_regulator(iid: str):
    from .store import notify_regulator
    inc = notify_regulator(iid)
    if not inc:
        raise HTTPException(404, "Incident not found")
    return {"incident": inc}


@router.post("/api/incidents/{iid}/auto-classify")
def auto_classify(iid: str):
    from .store import auto_classify
    inc = auto_classify(iid)
    if not inc:
        raise HTTPException(404, "Incident not found")
    return {"incident": inc}


@router.post("/api/incidents/{iid}/evidence")
async def upload_evidence(iid: str, file: UploadFile = File(...), label: str = Form("")):
    from .store import add_evidence
    try:
        data = await file.read()
        entry = add_evidence(iid, file.filename or "evidence.bin", data, label=label)
        if not entry:
            raise HTTPException(404, "Incident not found")
        return {"evidence": entry}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/api/incidents/{iid}/evidence/{eid}")
def download_evidence(iid: str, eid: str):
    from .store import get_evidence_file
    result = get_evidence_file(iid, eid)
    if not result:
        raise HTTPException(404, "Evidence not found")
    ev, data = result
    if data is None:
        raise HTTPException(404, "File not found on disk")
    return Response(content=data, media_type="application/octet-stream", headers={"Content-Disposition": f'attachment; filename="{ev["filename"]}"'})


@router.delete("/api/incidents/{iid}/evidence/{eid}")
def delete_evidence(iid: str, eid: str):
    from .store import delete_evidence
    if not delete_evidence(iid, eid):
        raise HTTPException(404, "Evidence not found")
    return {"ok": True}


@router.post("/api/incidents/{iid}/corrective-actions")
def add_corrective_action(iid: str, data: dict):
    from .store import add_corrective_action
    action = add_corrective_action(iid, data.get("description", ""), assigned_to=data.get("assigned_to", ""), due_date=data.get("due_date", ""))
    if not action:
        raise HTTPException(404, "Incident not found")
    return {"corrective_action": action}


@router.patch("/api/incidents/{iid}/corrective-actions/{caid}")
def update_corrective_action(iid: str, caid: str, data: dict):
    from .store import update_corrective_action
    action = update_corrective_action(iid, caid, data)
    if not action:
        raise HTTPException(404, "Corrective action not found")
    return {"corrective_action": action}


@router.post("/api/incidents/{iid}/telemetry")
def save_telemetry(iid: str, data: dict):
    from .store import save_telemetry
    inc = save_telemetry(iid, data)
    if not inc:
        raise HTTPException(404, "Incident not found")
    return {"incident": inc}


@router.post("/api/incidents/{iid}/regulatory-reports")
def create_regulatory_report(iid: str, data: dict):
    from .store import create_regulatory_report
    report = create_regulatory_report(iid, data.get("report_type", "initial"), submitted_to=data.get("submitted_to", ""), content=data.get("content", ""))
    if not report:
        raise HTTPException(404, "Incident not found")
    return {"report": report}


@router.get("/api/incidents/{iid}/export")
def export_incident(iid: str):
    from .store import get_incident
    i = get_incident(iid)
    if not i:
        raise HTTPException(404, "Incident not found")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["field", "value"])
    for k, v in i.items():
        if k in ("id", "title", "description", "failure_mode", "severity", "status", "model_name", "reporter_name", "created_at"):
            w.writerow([k, str(v)])
    w.writerow([])
    w.writerow(["history"])
    for h in i.get("history", []):
        w.writerow([h.get("timestamp", ""), h.get("action", ""), h.get("detail", "")])
    return Response(buf.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=incident-{iid}.csv"})


@router.get("/api/incidents/export/csv")
def export_incidents_csv():
    from .store import list_incidents
    items, _ = list_incidents(limit=9999)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "title", "failure_mode", "severity", "status", "created_at", "regulatory_deadline", "notified"])
    for i in items:
        clock = i.get("regulatory_clock", {})
        w.writerow([i.get("id"), i.get("title"), i.get("failure_mode"), i.get("severity"), i.get("status"), i.get("created_at"), clock.get("deadline", ""), clock.get("notified", False)])
    return Response(buf.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=incidents-export.csv"})


@router.get("/api/incidents/{iid}/export/regulator-pack")
def export_regulator_pack(iid: str):
    from .store import get_incident, get_evidence_file
    i = get_incident(iid)
    if not i:
        raise HTTPException(404, "Incident not found")
    buf = io.BytesIO()
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        summary = (
            f"Regulator Pack — {i['title']}\n"
            f"Incident ID: {iid}\n"
            f"Generated: {now}\n"
            f"Severity: {i.get('severity')}\n"
            f"Status: {i.get('status')}\n"
            f"Failure Mode: {i.get('failure_mode')}\n"
            f"Reported: {i.get('created_at')}\n"
            f"Regulatory Deadline: {i.get('regulatory_clock', {}).get('deadline', 'N/A')}\n"
            f"Notified: {i.get('regulatory_clock', {}).get('notified', False)}\n"
        )
        zf.writestr("summary.txt", summary)

        csv_buf = io.StringIO()
        w = csv.writer(csv_buf)
        w.writerow(["timestamp", "action", "detail"])
        for h in i.get("history", []):
            w.writerow([h.get("timestamp", ""), h.get("action", ""), h.get("detail", "")])
        zf.writestr("audit_trail.csv", csv_buf.getvalue())

        timeline = i.get("timeline", {})
        tl_lines = ["Timeline", "--------"]
        for k, v in timeline.items():
            tl_lines.append(f"{k}: {v or 'N/A'}")
        zf.writestr("timeline.txt", "\n".join(tl_lines))

        files_dir = Path("/tmp/khestra-evidence-files")
        for ev in i.get("evidence", []):
            ext = Path(ev["filename"]).suffix
            src = files_dir / f"{ev['id']}{ext}"
            if src.exists():
                zf.write(str(src), f"evidence/{ev['id']}{ext}")

        zf.writestr(
            "readme.txt",
            "Khestra Incident Regulator Pack\n"
            f"Generated: {now}\n"
            f"Incident: {i['title']} ({iid})\n"
            f"Evidence files: {len(i.get('evidence', []))}\n"
            f"Contains: summary.txt, audit_trail.csv, timeline.txt, evidence/*\n",
        )
    return Response(buf.getvalue(), media_type="application/zip", headers={"Content-Disposition": f"attachment; filename=regulator-pack-{iid}.zip"})


@router.get("/api/playbooks")
def list_playbooks():
    return {"playbooks": PLAYBOOKS}


@router.get("/api/playbooks/{mode}")
def get_playbook(mode: str):
    if mode not in PLAYBOOKS:
        raise HTTPException(404, "Playbook not found")
    return {"playbook": PLAYBOOKS[mode]}


@router.get("/api/notifications")
def get_notifications():
    from .store import list_incidents
    items, _ = list_incidents(limit=9999)
    notes = []
    for i in items:
        for h in i.get("history", []):
            notes.append({"source": "incident", "source_id": i.get("id"), "source_title": i.get("title"), "timestamp": h.get("timestamp"), "action": h.get("action"), "detail": h.get("detail")})
    notes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"notifications": notes[:100], "unread": len(notes[:100])}
