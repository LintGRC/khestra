"""Public Trust Center — compliance posture, security, and policy transparency."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/trust-center", tags=["trust-center"])

# ─── In-memory config (set by org admin, persisted to a small JSON file) ───

_CONF: dict | None = None


def _conf_path() -> Path:
    from config import DATA_DIR
    return DATA_DIR / "trust_center.json"


def _load_conf() -> dict:
    global _CONF
    if _CONF is not None:
        return _CONF
    try:
        _CONF = json.loads(_conf_path().read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        _CONF = {
            "org_name": "Organization",
            "certifications": [
                {"framework": "SOC 2 Type II", "status": "active", "last_audit": "2026-01-15", "scope": "Security, Availability, Confidentiality"},
                {"framework": "CMMC Level 2", "status": "in_progress", "last_audit": "", "scope": "CUI Enclave"},
                {"framework": "AI Governance", "status": "active", "last_audit": "2026-03-01", "scope": "AI Systems"},
            ],
            "security": {
                "encryption": "AES-256 at rest, TLS 1.3 in transit",
                "mfa": "Required for all users, including service accounts",
                "sso": "SAML 2.0 / OIDC (Azure Entra ID, Okta, Google Workspace)",
                "monitoring": "24/7 SIEM with automated alerting (Microsoft Sentinel)",
                "pentest": "Annual penetration test by accredited third party (last: 2026-02-28)",
                "vulnerability_scanning": "Weekly automated scans (Tenable.io)",
                "incident_response": "IR plan tested quarterly; < 1 hr mean detection time",
            },
            "subprocessors": [
                {"name": "Microsoft Azure", "service": "Cloud Infrastructure", "location": "US East, US West", "soc2": True},
                {"name": "AWS", "service": "Backup & Disaster Recovery", "location": "US East", "soc2": True},
                {"name": "Datadog", "service": "Monitoring & Observability", "location": "US", "soc2": True},
                {"name": "Twilio SendGrid", "service": "Email Notifications", "location": "US", "soc2": True},
            ],
        }
    return _CONF


import json
import os as _os
import threading

_TRUST_CENTER_ADMIN_KEY = _os.environ.get("TRUST_CENTER_ADMIN_KEY", "")
_conf_lock = threading.Lock()


def _require_admin(request: Request):
    if not _TRUST_CENTER_ADMIN_KEY:
        raise HTTPException(503, "Trust Center admin key not configured")
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth[7:] != _TRUST_CENTER_ADMIN_KEY:
        raise HTTPException(401, "Unauthorized")


def _save_conf(conf: dict):
    global _CONF
    with _conf_lock:
        _CONF = conf
        path = _conf_path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(conf, indent=2))
        tmp.replace(path)


# ─── Public endpoints ────────────────────────────────────


class SecurityUpdate(BaseModel):
    encryption: str = ""
    mfa: str = ""
    sso: str = ""
    monitoring: str = ""
    pentest: str = ""
    vulnerability_scanning: str = ""
    incident_response: str = ""


class SubprocessorEntry(BaseModel):
    name: str = ""
    service: str = ""
    location: str = ""
    soc2: bool = False


class CertificationEntry(BaseModel):
    framework: str = ""
    status: str = ""
    last_audit: str = ""
    scope: str = ""


@router.get("/summary")
def get_summary():
    conf = _load_conf()
    certs = conf.get("certifications", [])
    active_certs = [c for c in certs if c.get("status") == "active"]
    return {
        "org_name": conf.get("org_name", "Organization"),
        "certification_count": len(active_certs),
        "certifications": [{"framework": c["framework"], "status": c["status"]} for c in certs],
        "last_audit_date": max(
            (c.get("last_audit", "") for c in certs if c.get("last_audit")), default=""
        ),
        "security_count": len(conf.get("security", {})),
        "subprocessor_count": len(conf.get("subprocessors", [])),
    }


@router.get("/compliance")
def get_compliance():
    conf = _load_conf()
    return conf.get("certifications", [])


@router.get("/security")
def get_security():
    conf = _load_conf()
    return conf.get("security", {})


@router.get("/subprocessors")
def get_subprocessors():
    conf = _load_conf()
    return conf.get("subprocessors", [])


@router.get("/policies")
def get_published_policies():
    try:
        from policies.store import list_documents
        docs = list_documents()
        published = [d for d in docs if d.get("status") == "published"]
        return [
            {
                "id": d["id"],
                "title": d["title"],
                "description": d.get("description", ""),
                "version": d.get("version", 1),
                "updated_at": d.get("updated_at", ""),
            }
            for d in published
        ]
    except Exception:
        return []


@router.get("/evidence-summary")
def get_evidence_summary():
    try:
        from evidence_hub.store import get_stats
        stats = get_stats()
        return {
            "total_evidence": stats.get("total_evidence", 0),
            "total_mappings": stats.get("total_mappings", 0),
        }
    except Exception:
        return {"total_evidence": 0, "total_mappings": 0}


# ─── Admin config endpoints ───────────────────────────

import json
import os as _os
import threading
import tempfile

_TRUST_CENTER_ADMIN_KEY = _os.environ.get("TRUST_CENTER_ADMIN_KEY", "")
_conf_lock = threading.Lock()


def _save_conf(conf: dict):
    global _CONF
    with _conf_lock:
        _CONF = conf
        path = _conf_path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(conf, indent=2))
        tmp.replace(path)


@router.get("/config")
def get_config():
    return _load_conf()


@router.post("/config")
def update_config(
    request: Request,
    org_name: str = "",
    security: SecurityUpdate | None = None,
    subprocessors: list[SubprocessorEntry] | None = None,
    certifications: list[CertificationEntry] | None = None,
):
    _require_admin(request)
    conf = _load_conf()
    if org_name:
        conf["org_name"] = org_name
    if security is not None:
        conf["security"] = security.model_dump()
    if subprocessors is not None:
        conf["subprocessors"] = [s.model_dump() for s in subprocessors]
    if certifications is not None:
        conf["certifications"] = [c.model_dump() for c in certifications]
    _save_conf(conf)
    return {"status": "ok"}
