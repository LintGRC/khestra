"""SOC 2 Khestra API."""

from __future__ import annotations

import io
import json
import sys
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from security_headers.ratelimit import add_rate_limiting
from security_headers.security import add_security_headers
from dotenv import load_dotenv
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

PLATFORM = Path(__file__).resolve().parents[1]
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
CORE = PLATFORM / "core"
PACKAGES = PLATFORM / "packages"
if not PACKAGES.is_dir():
    PACKAGES = PLATFORM.parents[1] / "packages"  # local dev: khestra/
EVIDENCE = PACKAGES / "evidence"
CMMC_CORE = (PLATFORM.parent / "cmmc" / "core")  # Docker: sibling app
if not CMMC_CORE.is_dir():
    CMMC_CORE = PLATFORM.parents[1] / "apps" / "cmmc" / "core"  # local dev: khestra/
# SOC 2 core must win over CMMC core (both have readiness.py, app_config.py, etc.).
# CMMC core is appended so entra_auth resolves without shadowing SOC 2 modules.
for path in (PACKAGES, EVIDENCE, CORE, PLATFORM / "server"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
# Re-insert PACKAGES at front so shared packages win over per-app modules
if str(PACKAGES) in sys.path:
    sys.path.remove(str(PACKAGES))
    sys.path.insert(0, str(PACKAGES))
if str(CMMC_CORE) not in sys.path:
    sys.path.append(str(CMMC_CORE))

from auth_middleware import entra_auth_middleware  # noqa: E402
from entra_auth import auth_enabled, get_auth_user, public_auth_config  # noqa: E402
from auth.jwt import init_secret as init_auth_secret  # noqa: E402
from auth.routes import router as auth_router  # noqa: E402
from auth.store import init_store as init_auth_store  # noqa: E402
from entra_auth.config import auth_mode  # noqa: E402
from production_config import allowed_cors_origins, demo_api_enabled  # noqa: E402

from config import DATA_DIR as SOC2_DATA_DIR  # noqa: E402
from kevidence.config import configure as configure_evidence  # noqa: E402
configure_evidence(data_dir=SOC2_DATA_DIR, platform_root=PLATFORM)
from kevidence.availability import collectors_available

if collectors_available():
    import soc2_collectors  # noqa: F401,E402 — register evidence mapping

from ccf.routes import router as ccf_router  # noqa: E402
from remediation.routes import router as remediation_router  # noqa: E402
from remediation.routes import init_store as init_remediation_store  # noqa: E402
from policies.routes import router as policy_router  # noqa: E402
from policies.store import init_store as init_policy_store  # noqa: E402
from policies.store import add_builtin_templates  # noqa: E402
from orgs.routes import router as orgs_router  # noqa: E402
from orgs.store import init_store as init_orgs_store  # noqa: E402
from raci.routes import router as raci_router  # noqa: E402
from raci.store import init_store as init_raci_store  # noqa: E402
from exceptions.store import init_store as init_exception_store  # noqa: E402
from exceptions.routes import router as exception_router  # noqa: E402
from vendors.routes import router as vendor_router  # noqa: E402
from vendors.store import init_store as init_vendor_store  # noqa: E402
from audit.routes import router as audit_router  # noqa: E402
from audit.store import init_store as init_audit_store  # noqa: E402
from risks.routes import router as risks_router  # noqa: E402
from risks.store import init_store as init_risks_store, seed_risks  # noqa: E402
from testing.routes import router as testing_router  # noqa: E402
from testing.store import init_store as init_testing_store, get_stats, overdue_test_count  # noqa: E402
from findings.routes import router as findings_router  # noqa: E402
from findings.store import init_store as init_findings_store  # noqa: E402
from audit_center.routes import router as audit_center_router  # noqa: E402
from audit_center.store import init_store as init_audit_center_store  # noqa: E402
from training.routes import router as training_router  # noqa: E402
from training.store import init_store as init_training_store  # noqa: E402
from training.soc2_modules import seed_soc2_modules  # noqa: E402
from personnel.routes import router as personnel_router  # noqa: E402
from compliance_calendar.routes import router as compliance_calendar_router  # noqa: E402
from effectiveness.routes import router as effectiveness_router  # noqa: E402
from control_tests.routes import router as control_tests_router  # noqa: E402
from control_tests.store import init_store as init_control_tests_store  # noqa: E402
from personnel.store import init_store as init_personnel_store  # noqa: E402
from assets.routes import router as assets_router  # noqa: E402
from assets.store import init_store as init_assets_store  # noqa: E402
from audit_log.store import init_store as init_audit_log_store, list_events, log_event, export_events_csv  # noqa: E402
from evidence_hub.routes import router as evidence_hub_router  # noqa: E402
from evidence_hub.store import init_store as init_evidence_hub_store  # noqa: E402
from reviews.store import init_store as init_reviews_store  # noqa: E402
from notifications.routes import router as notifications_router  # noqa: E402
from notifications.store import init_store as init_notification_store, check_all_triggers  # noqa: E402
from compliance_calendar.store import init_store as init_compliance_calendar_store  # noqa: E402

from incidents.routes import router as incidents_router  # noqa: E402
from incidents.store import init_store as init_incidents_store  # noqa: E402

from app_config import APP_VERSION, FREQUENCY_OPTIONS, OPERATING_STATUS_OPTIONS, STATUS_OPTIONS, USER_ROLES  # noqa: E402
from permissions_api import can_edit_controls, can_edit_org, can_export, role_capabilities  # noqa: E402
from demo_loader import load_demo  # noqa: E402
from readiness import compute_dashboard  # noqa: E402
from soc2_catalog import SOC2_CONTROLS  # noqa: E402
from tsc_scoping import (  # noqa: E402
    DEFAULT_SCOPE,
    TSC_CATEGORIES,
    get_in_scope_controls,
    get_in_scope_criteria_ids,
    is_in_scope,
    normalize_scope,
    scope_summary,
    validate_scope,
)
from documents_registry import build_documents_list  # noqa: E402
from reviews.routes import router as reviews_router  # noqa: E402
def get_guidance(control_id: str) -> dict:
    """Check-keyed evidence guidance is part of the collectors edition."""
    return {}  # noqa: E402
from org_profile import (  # noqa: E402
    FIELD_LABELS,
    FIELD_PLACEHOLDERS,
    WIZARD_STEPS,
    merge_org_profile,
    profile_needs_wizard,
)
from env_scope import (  # noqa: E402
    CLOUD_LABELS,
    YES_NO_LABELS,
    env_scope_complete,
    format_env_scope_summary,
    merge_env_scope,
    scoping_suggestions,
)
from org_inventory import (  # noqa: E402
    INVENTORY_COLUMNS,
    merge_org_inventory,
    set_inventory_assets,
)
from readiness_assessment import run_readiness_assessment  # noqa: E402
from ssp_export import generate_system_description_docx  # noqa: E402
from poam_export import export_poam_csv, export_poam_docx  # noqa: E402
from my_work import get_my_work  # noqa: E402
from priority_queue import get_priority_queue  # noqa: E402
from workspace_service import (  # noqa: E402
    WorkspaceLockedError,
    attach_evidence,
    attach_evidence_multi,
    create_audit_period,
    create_evidence_request,
    default_control_answer,
    detach_evidence,
    evidence_coverage_for_period,
    freeze_audit_period,
    generate_manifest,
    get_recent_activity,
    list_all_evidence,
    list_audit_periods,
    list_control_summaries,
    list_evidence_requests,
    load_workspace,
    patch_control,
    patch_evidence_request,
    patch_pof,
    bulk_patch_pofs,
    pof_coverage_stats,
    require_workspace_editable,
    review_evidence,
    save_workspace,
    workspace_is_locked,
)
if collectors_available():
    from collectors.credentials_store import (  # noqa: E402
        credentials_status,
        delete_credentials,
        save_credentials,
    )
    from collectors.engine import recent_runs, run_collector  # noqa: E402
    from collectors.monitor_store import get_events, patch_monitor_schedule  # noqa: E402
    from collectors.registry import CONNECTOR_CATALOG, list_connectors  # noqa: E402
    from collectors.routes import router as collectors_router  # noqa: E402
    from collectors.dev_scheduler import lifespan_scheduler  # noqa: E402
    from soc2_collectors.attach import run_and_attach  # noqa: E402
    from soc2_collectors.freshness import freshness_for_workspace  # noqa: E402
    from soc2_collectors.scheduler import monitoring_summary, run_due_connectors  # noqa: E402
    from soc2_collectors.webhook_ingest import ingest_webhook_payload  # noqa: E402
    from collectors.webhook_store import (  # noqa: E402
        create_webhook_collector,
        delete_webhook_collector,
        env_webhook_token,
        list_webhook_collectors,
    )
else:
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _noop_lifespan():
        yield

    class _MockRun:
        def to_dict(self):
            return {"status": "unavailable"}
        status = "unavailable"

    CONNECTOR_CATALOG = {}
    list_connectors = lambda: []
    recent_runs = lambda: []
    run_collector = lambda *a, **k: _MockRun()
    get_events = lambda limit=0: []
    patch_monitor_schedule = lambda connector_id, **k: {"connector_id": connector_id}
    credentials_status = lambda connector_id, fields: {"connector_id": connector_id, "configured": False}
    save_credentials = lambda *a, **k: None
    delete_credentials = lambda *a, **k: None
    lifespan_scheduler = _noop_lifespan
    run_and_attach = lambda connector_id, **kw: (_MockRun(), [], [])
    freshness_for_workspace = lambda ws: {}
    monitoring_summary = lambda: {}
    run_due_connectors = lambda **kw: {"ran_count": 0, "due_count": 0}
    ingest_webhook_payload = lambda *a, **k: {}
    create_webhook_collector = lambda *a, **k: {}
    delete_webhook_collector = lambda *a, **k: None
    env_webhook_token = lambda: ""
    list_webhook_collectors = lambda: []
from client_workspaces import (  # noqa: E402
    active_client_id,
    client_evidence_dir,
    create_client,
    delete_client,
    ensure_default_client,
    list_clients,
    rename_client,
    set_active_client_id,
)
from system_description import generate_system_description  # noqa: E402
from cuec import create_cuec, delete_cuec, get_cuecs_for_control, list_cuecs, update_cuec  # noqa: E402
from executive_report import generate_executive_summary  # noqa: E402
from pdf_export.engine import generate_pdf  # noqa: E402
from control_matrix import generate_control_matrix  # noqa: E402
from evidence_hints import get_pof_hints  # noqa: E402
from gap_analysis import generate_gap_analysis  # noqa: E402
from readiness_trends import get_readiness_trends, snapshot_readiness  # noqa: E402
from filestore import get_evidence_bytes, safe_evidence_filename, within_size_limit  # noqa: E402


class ControlPatchBody(BaseModel):
    status: Optional[str] = None
    implementation_narrative: Optional[str] = None
    assessor_notes: Optional[str] = None
    owner: Optional[str] = None
    target_date: Optional[str] = None
    remediation_plan: Optional[str] = None
    operating_status: Optional[str] = None
    frequency: Optional[str] = None
    last_review_date: Optional[str] = None
    next_review_date: Optional[str] = None
    linked_policies: Optional[List[Dict[str, Any]]] = None
    linked_assets: Optional[List[Dict[str, Any]]] = None
    linked_team: Optional[List[str]] = None
    points_of_focus: Optional[Dict[str, Dict[str, str]]] = None


class BulkPofBody(BaseModel):
    updates: Dict[str, Dict[str, str]]


class PatchPofBody(BaseModel):
    status: str = "not_applicable"
    justification: str = ""


class CollectorCredentialsBody(BaseModel):
    credentials: Dict[str, str] = Field(default_factory=dict)


class CollectorRunBody(BaseModel):
    use_fixture: bool = False
    attach: bool = True
    control_ids: Optional[List[str]] = None


class CollectorScheduleBody(BaseModel):
    enabled: Optional[bool] = None
    interval: Optional[str] = None
    attach_on_run: Optional[bool] = None


class RunDueBody(BaseModel):
    use_fixture_if_unconfigured: bool = False


class CreateAuditPeriodBody(BaseModel):
    name: str
    start_date: str
    end_date: str


class UploadEvidenceMultiBody(BaseModel):
    file: Optional[str] = None
    control_ids: List[str] = Field(default_factory=list)
    source: str = "manual"


class ReviewEvidenceBody(BaseModel):
    reviewer: str
    status: str
    comment: str = ""


class CreateEvidenceRequestBody(BaseModel):
    control_id: str
    title: str
    description: str = ""
    assigned_to: str = ""
    due_date: str = ""


class PatchEvidenceRequestBody(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None


class WebhookCreateBody(BaseModel):
    name: str
    source_system: str = ""


class OrgProfileBody(BaseModel):
    org_name: Optional[str] = None
    system_name: Optional[str] = None
    system_description: Optional[str] = None
    architecture_summary: Optional[str] = None
    boundary_description: Optional[str] = None
    system_owner: Optional[str] = None
    compliance_officer: Optional[str] = None
    it_admin: Optional[str] = None
    auditor_name: Optional[str] = None
    system_unique_id: Optional[str] = None
    org_address: Optional[str] = None
    org_phone: Optional[str] = None
    header_short_name: Optional[str] = None
    hardware_inventory: Optional[str] = None
    software_inventory: Optional[str] = None
    team_roster: Optional[str] = None


class EnvScopeBody(BaseModel):
    uses_cloud: Optional[str] = None
    cloud_provider: Optional[str] = None
    uses_saas: Optional[str] = None
    remote_workforce: Optional[str] = None
    uses_wireless: Optional[str] = None
    processes_pii: Optional[str] = None


class InventoryUpdateBody(BaseModel):
    assets: List[Dict[str, str]] = Field(default_factory=list)


class RolePatch(BaseModel):
    role: str


class UserNamePatch(BaseModel):
    name: str


class ClientCreateBody(BaseModel):
    name: str


class ClientRenameBody(BaseModel):
    name: str


def _workspace_locked_detail() -> str:
    return "Workspace is locked while an audit period is frozen"


def _guard_editable(ws: Dict[str, Any]) -> None:
    try:
        require_workspace_editable(ws)
    except WorkspaceLockedError as exc:
        raise HTTPException(409, str(exc)) from exc


def _ws_role(ws: Dict[str, Any]) -> str:
    user = get_auth_user()
    if user and auth_enabled():
        return user.role
    return ws.get("current_role", "Assessor")


def _require_edit_controls(ws: Dict[str, Any]) -> None:
    role = _ws_role(ws)
    if not can_edit_controls(role):
        raise HTTPException(403, "Your role does not have permission to edit controls")


def _require_edit_org(ws: Dict[str, Any]) -> None:
    role = _ws_role(ws)
    if not can_edit_org(role):
        raise HTTPException(403, "Your role does not have permission to edit organization data")


def _require_export(ws: Dict[str, Any]) -> None:
    role = _ws_role(ws)
    if not can_export(role):
        raise HTTPException(403, "Your role does not have permission to export data")


def _current_user_name(ws: Dict[str, Any]) -> str:
    user = get_auth_user()
    if user:
        return user.name or user.email or ""
    return ws.get("current_user_name", "")


def _resolve_evidence_file(
    ws: Dict[str, Any], control_id: str, filename: str
) -> tuple[Dict[str, Any], bytes]:
    if control_id not in SOC2_CONTROLS:
        raise HTTPException(404, "Control not found")
    scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
    if not is_in_scope(control_id, scope):
        raise HTTPException(404, "Control is out of scope")
    safe = safe_evidence_filename(filename)
    evidence_dir = client_evidence_dir(ws.get("client_id") or active_client_id())
    ans = ws["answers"].get(control_id, default_control_answer())
    for ev in ans.get("evidence") or []:
        if ev.get("filename") == safe:
            data = get_evidence_bytes(
                control_id,
                ev,
                ws.get("restored_evidence"),
                evidence_dir=evidence_dir,
            )
            if data is None:
                raise HTTPException(404, "Evidence file not found on disk")
            return ev, data
    raise HTTPException(404, "Evidence not found")


def _audit_log(
    ws: Dict[str, Any],
    action: str,
    resource_type: str,
    resource_id: str = "",
    details: Optional[Dict[str, Any]] = None,
    outcome: str = "success",
) -> None:
    try:
        log_event(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            framework_id="SOC2",
            user_email=_current_user_name(ws),
            details=details,
            outcome=outcome,
        )
    except Exception:
        pass


@asynccontextmanager
async def _lifespan(_app: FastAPI):

    try:
        from auth.deploy_guard import assert_safe_auth_posture
        assert_safe_auth_posture()
    except RuntimeError as e:
        print(f"[startup] AUTH POSTURE REFUSAL: {e}", file=sys.stderr)
        raise
    for _init_fn, _path in [
        (init_remediation_store, str(SOC2_DATA_DIR)),
        (init_policy_store, str(SOC2_DATA_DIR)),
        (init_orgs_store, str(SOC2_DATA_DIR)),
        (init_raci_store, str(SOC2_DATA_DIR)),
        (init_exception_store, str(SOC2_DATA_DIR)),
        (init_vendor_store, str(SOC2_DATA_DIR)),
        (init_audit_store, str(SOC2_DATA_DIR)),
        (init_risks_store, str(SOC2_DATA_DIR)),
        (init_control_tests_store, str(SOC2_DATA_DIR)),
        (init_testing_store, str(SOC2_DATA_DIR)),
        (init_findings_store, str(SOC2_DATA_DIR)),
        (init_audit_center_store, str(SOC2_DATA_DIR)),
        (init_training_store, str(SOC2_DATA_DIR)),
        (init_personnel_store, str(SOC2_DATA_DIR)),
        (init_assets_store, str(SOC2_DATA_DIR)),
        (init_audit_log_store, str(SOC2_DATA_DIR)),
        (init_compliance_calendar_store, str(SOC2_DATA_DIR)),
        (init_evidence_hub_store, str(SOC2_DATA_DIR)),
        (init_incidents_store, str(SOC2_DATA_DIR)),
        (init_reviews_store, str(SOC2_DATA_DIR)),
        (init_notification_store, str(SOC2_DATA_DIR)),
        (init_auth_secret, str(SOC2_DATA_DIR)),
    ]:
        try:
            _init_fn(_path)
        except Exception as e:
            print(f"[lifespan] {_init_fn.__name__} failed: {e}", file=sys.stderr)
    try:
        add_builtin_templates()
    except Exception as e:
        print(f"[lifespan] add_builtin_templates failed: {e}", file=sys.stderr)
    try:
        seed_risks()
    except Exception as e:
        print(f"[lifespan] seed_risks failed: {e}", file=sys.stderr)
    try:
        seed_soc2_modules()
    except Exception as e:
        print(f"[lifespan] seed_soc2_modules failed: {e}", file=sys.stderr)
    if auth_mode() == "local":
        try:
            init_auth_store(str(SOC2_DATA_DIR))
        except Exception as e:
            print(f"[lifespan] init_auth_store failed: {e}", file=sys.stderr)

    try:
        from compliance_calendar.sweep import run_reminder_sweep
        outcome = run_reminder_sweep(window_days=7)
        if outcome.get("created"):
            print(f"[startup] compliance reminders: {outcome['created']} new", file=sys.stderr)
    except Exception as e:
        print(f"[startup] compliance reminder sweep failed: {e}", file=sys.stderr)

    try:
        from compliance_calendar.framework_milestones import sync_soc2_milestones
        sync_soc2_milestones(load_workspace())
    except Exception as e:
        print(f"[startup] SOC2 milestone sync failed: {e}", file=sys.stderr)

    async with lifespan_scheduler():
        yield


app = FastAPI(title="Khestra SOC 2", version=APP_VERSION, lifespan=_lifespan, docs_url=None, redoc_url=None, openapi_url=None)


class StripFrameworkPrefixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/api/soc2/"):
                scope["path"] = path.replace("/api/soc2/", "/api/", 1)
        await self.app(scope, receive, send)


app.add_middleware(StripFrameworkPrefixMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_security_headers(app)
add_rate_limiting(app)


app.middleware("http")(entra_auth_middleware)

_EXCLUDED_MUTATION_PREFIXES = (
    "/api/controls/",
    "/api/org-profile",
    "/api/settings/",
    "/api/clients/",
    "/api/inventory",
    "/api/env-scope",
    "/api/webhooks",
    "/api/webhook/",
    "/api/collectors/",
    "/api/demo/",
    "/api/audit-log",
    "/api/evidence",
    "/api/audit/periods",
    "/api/evidence/requests",
)


@app.middleware("http")
async def _audit_mutation_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return response
    path = request.url.path
    if not path.startswith("/api/"):
        return response
    if any(path.startswith(p) for p in _EXCLUDED_MUTATION_PREFIXES):
        return response
    if response.status_code in (200, 201):
        outcome = "success"
    elif response.status_code in (401, 403):
        outcome = "failure"
    else:
        return response
    try:
        user = get_auth_user()
        details = {}
        if outcome == "failure":
            details = {"denied_path": path, "method": request.method, "security": True}
        log_event(
            action=request.method.lower(),
            resource_type=path.split("/")[2] if len(path.split("/")) > 2 else "unknown",
            framework_id="SOC2",
            user_id=user.oid if user else "",
            user_email=user.email if user else "",
            ip_address=request.client.host if request.client else "",
            user_agent=request.headers.get("user-agent", ""),
            outcome=outcome,
            details=details,
        )
    except Exception:
        pass
    return response


@app.get("/api/auth/config")
def auth_config() -> Dict[str, Any]:
    return public_auth_config()


def _capabilities(role: str) -> Dict[str, bool]:
    return role_capabilities(role)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": "khestra-soc2",
        "version": APP_VERSION,
        "framework": "soc2-type2",
        "controls": len(SOC2_CONTROLS),
    }


@app.get("/api/dashboard")
def dashboard(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    dash = compute_dashboard(ws)
    periods = list_audit_periods(ws)
    active_period = next((p for p in periods if not p["frozen"]), None)
    frozen_period = next((p for p in periods if p["frozen"]), None)
    test_stats = get_stats(framework="SOC2")
    overdue = overdue_test_count(framework="SOC2")
    period_cov = evidence_coverage_for_period(ws, active_period) if active_period else None
    return {
        **dash,
        "active_audit_period": active_period,
        "frozen_audit_period": frozen_period,
        "evidence_total": len(list_all_evidence(ws)),
        "evidence_review_pending": sum(
            1 for e in list_all_evidence(ws) if e.get("review_status") == "pending"
        ),
        "open_requests": len([r for r in list_evidence_requests(ws) if r["status"] == "open"]),
        "recent_activity": get_recent_activity(ws, limit=8),
        "test_pass_rate": test_stats.get("pass_rate", 0.0),
        "test_total": test_stats.get("total", 0),
        "test_pass": test_stats.get("pass", 0),
        "test_fail": test_stats.get("fail", 0),
        "test_not_tested": test_stats.get("not_tested", 0),
        "test_needs_review": test_stats.get("needs_review", 0),
        "overdue_tests": overdue,
        "period_coverage": period_cov,
    }


@app.get("/api/readiness/trends")
def get_readiness_trends_endpoint(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return get_readiness_trends(ws)


@app.get("/api/scoping/tsc")
def get_tsc_scope(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
    return {
        "scope": scope,
        "categories": {k: {kk: vv for kk, vv in v.items() if kk != "criteria_prefixes"} for k, v in TSC_CATEGORIES.items()},
        "summary": scope_summary(scope),
        "scoping_completed": ws.get("scoping_completed", False),
    }

class TscScopeBody(BaseModel):
    scope: Dict[str, bool]
    scoping_completed: bool = True
@app.patch("/api/scoping/tsc")
def patch_tsc_scope(body: TscScopeBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    validation = validate_scope(body.scope)
    if not validation["valid"]:
        raise HTTPException(400, "; ".join(validation["errors"]))
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_org(ws)
    normalized = normalize_scope(body.scope)
    normalized["Security"] = True  # enforce mandatory
    ws["tsc_scope"] = normalized
    ws["scoping_completed"] = body.scoping_completed
    save_workspace(ws)
    _audit_log(ws, "updated", "scoping", "", {"categories": [k for k, v in normalized.items() if v]})
    return {
        "scope": ws["tsc_scope"],
        "summary": scope_summary(ws["tsc_scope"]),
        "scoping_completed": ws["scoping_completed"],
    }
@app.get("/api/evidence")
def get_evidence_all(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {"evidence": list_all_evidence(ws)}


@app.post("/api/evidence")
async def upload_evidence_multi(
    file: UploadFile = File(...),
    control_ids: str = Form(...),
    client_id: Optional[str] = Query(None),
    valid_from: Optional[str] = Query(None),
    valid_to: Optional[str] = Query(None),
) -> Dict[str, Any]:
    try:
        ids = json.loads(control_ids)
    except json.JSONDecodeError as exc:
        raise HTTPException(400, "control_ids must be a JSON array of criterion IDs") from exc
    if not isinstance(ids, list) or not ids:
        raise HTTPException(400, "control_ids must be a non-empty JSON array")
    unknown = [cid for cid in ids if cid not in SOC2_CONTROLS]
    if unknown:
        raise HTTPException(400, f"Unknown criteria: {', '.join(unknown)}")

    ws = load_workspace(client_id)
    scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
    out_of_scope = [cid for cid in ids if not is_in_scope(cid, scope)]
    if out_of_scope:
        raise HTTPException(400, f"Out of scope criteria: {', '.join(out_of_scope)}")
    _guard_editable(ws)
    _require_edit_controls(ws)
    data = await file.read()
    if not within_size_limit(data):
        raise HTTPException(413, "Evidence file exceeds size limit")
    import hashlib
    from datetime import datetime

    filename = safe_evidence_filename(file.filename or "evidence")
    sha = hashlib.sha256(data).hexdigest()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    vf = valid_from or stamp.split(" ")[0]
    ws = attach_evidence_multi(ws, ids, filename=filename, data=data, sha256=sha, upload_date=stamp, valid_from=vf, valid_to=valid_to)
    save_workspace(ws)
    _audit_log(ws, "created", "evidence", filename, {"control_ids": ids})
    return {"status": "ok", "filename": filename, "control_ids": ids}


@app.get("/api/evidence/coverage")
def get_evidence_coverage(
    period_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    periods = list_audit_periods(ws)
    if period_id:
        period = next((p for p in periods if p["id"] == period_id), None)
        if not period:
            raise HTTPException(404, "Period not found")
        return evidence_coverage_for_period(ws, period)
    # If no period_id, use the active (unfrozen) period, then the most recent
    target = next((p for p in periods if not p.get("frozen")), None) or (periods[-1] if periods else None)
    if not target:
        scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
        return {
            "period_id": None,
            "period_name": "No audit period defined",
            "start_date": None,
            "end_date": None,
            "total_controls": len(get_in_scope_controls(scope)),
            "controls_covered": 0,
            "coverage_pct": 0,
            "per_control": {},
        }
    return evidence_coverage_for_period(ws, target)


@app.get("/api/audit-log")
def get_audit_log(
    framework_id: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(200),
    offset: int = Query(0),
):
    entries = list_events(framework_id=framework_id, resource_type=resource_type, limit=limit, offset=offset)
    return {"entries": entries}


@app.get("/api/audit-log/export")
def export_audit_log_csv(
    framework_id: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
):
    csv_data = export_events_csv(framework_id=framework_id, resource_type=resource_type)
    return Response(
        csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-log-export.csv"},
    )


@app.get("/api/audit/periods")
def get_audit_periods(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {"periods": list_audit_periods(ws)}


@app.post("/api/audit/periods")
def post_audit_period(
    body: CreateAuditPeriodBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    period = create_audit_period(ws, name=body.name, start_date=body.start_date, end_date=body.end_date)
    _audit_log(ws, "created", "audit_period", period["id"], {"name": body.name, "start": body.start_date, "end": body.end_date})
    return {"period": period}


@app.post("/api/audit/periods/{period_id}/freeze")
def post_freeze_period(
    period_id: str,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    period = freeze_audit_period(ws, period_id)
    if not period:
        raise HTTPException(404, "Period not found")
    snapshot_readiness(ws, "period_freeze")
    save_workspace(ws)
    try:
        from compliance_calendar.framework_milestones import sync_soc2_milestones
        sync_soc2_milestones(ws)
    except Exception:
        pass
    _audit_log(ws, "froze", "audit_period", period_id, {"name": period.get("name", "")})
    return {"period": period}


class EngagementBody(BaseModel):
    type: str = ""
    firm: str = ""
    cpa_contact: str = ""
    engagement_start: str = ""
    engagement_end: str = ""
    status: str = ""


@app.get("/api/audit/engagement")
def get_engagement(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {"engagement": ws.get("soc2_engagement") or {}}


@app.put("/api/audit/engagement")
def put_engagement(body: EngagementBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    if body.type not in ("", "type1", "type2"):
        raise HTTPException(400, "Engagement type must be type1, type2, or empty")
    if body.status not in ("", "planning", "fieldwork", "report", "completed"):
        raise HTTPException(400, "Invalid engagement status")
    engagement = {
        "type": body.type,
        "firm": body.firm.strip(),
        "cpa_contact": body.cpa_contact.strip(),
        "engagement_start": body.engagement_start.strip(),
        "engagement_end": body.engagement_end.strip(),
        "status": body.status,
    }
    ws["soc2_engagement"] = engagement
    save_workspace(ws)
    try:
        from compliance_calendar.framework_milestones import sync_soc2_milestones
        sync_soc2_milestones(ws)
    except Exception:
        pass
    _audit_log(ws, "updated", "audit_engagement", "", {"type": body.type, "status": body.status})
    return {"engagement": engagement}


@app.get("/api/audit/manifest")
def get_manifest(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return generate_manifest(ws)


@app.get("/api/evidence/requests")
def get_evidence_requests(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {"requests": list_evidence_requests(ws)}


@app.post("/api/evidence/requests")
def post_evidence_request(
    body: CreateEvidenceRequestBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    if body.control_id not in SOC2_CONTROLS:
        raise HTTPException(400, f"Unknown criterion: {body.control_id}")
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    try:
        req = create_evidence_request(
        ws,
        control_id=body.control_id,
        title=body.title,
        description=body.description,
        assigned_to=body.assigned_to,
        due_date=body.due_date,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    _audit_log(ws, "created", "evidence_request", req["id"], {"control_id": body.control_id, "title": body.title})
    return {"request": req}


@app.patch("/api/evidence/requests/{request_id}")
def patch_evidence_request_endpoint(
    request_id: str,
    body: PatchEvidenceRequestBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    req = patch_evidence_request(
        ws, request_id,
        status=body.status,
        assigned_to=body.assigned_to,
        due_date=body.due_date,
    )
    if not req:
        raise HTTPException(404, "Request not found")
    _audit_log(ws, "updated", "evidence_request", request_id, {k: v for k, v in {"status": body.status, "assigned_to": body.assigned_to, "due_date": body.due_date}.items() if v is not None})
    return {"request": req}


@app.get("/api/evidence/activity")
def get_activity(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {"activity": get_recent_activity(ws, limit=25)}


@app.get("/api/reports/evidence-index")
def get_evidence_index(client_id: Optional[str] = Query(None)) -> StreamingResponse:
    ws = load_workspace(client_id)
    _require_export(ws)
    manifest = generate_manifest(ws)
    lines = ["control_id,filename,sha256,upload_date,review_status"]
    for item in manifest["items"]:
        lines.append(f"{item['control_id']},{item['filename']},{item['sha256']},{item['upload_date']},{item['review_status']}")
    return StreamingResponse(
        io.StringIO("\n".join(lines)),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=evidence_index.csv"},
    )


@app.get("/api/reports/audit-package")
def get_audit_package(client_id: Optional[str] = Query(None)) -> StreamingResponse:
    ws = load_workspace(client_id)
    _require_export(ws)
    cid = ws.get("client_id") or active_client_id()
    evidence_dir = client_evidence_dir(cid)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest = generate_manifest(ws)
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        lines = ["control_id,filename,sha256,upload_date,review_status"]
        for item in manifest["items"]:
            lines.append(f"{item['control_id']},{item['filename']},{item['sha256']},{item['upload_date']},{item['review_status']}")
        zf.writestr("evidence_index.csv", "\n".join(lines))
        files_included = 0
        for cid_key in get_in_scope_criteria_ids(ws.get("tsc_scope") or dict(DEFAULT_SCOPE)):
            ans = ws["answers"].get(cid_key, default_control_answer())
            for ev in ans.get("evidence") or []:
                fname = ev.get("filename") or ""
                if not fname:
                    continue
                payload = get_evidence_bytes(cid_key, ev, evidence_dir=evidence_dir)
                if payload:
                    zf.writestr(f"evidence/{cid_key}/{fname}", payload)
                    files_included += 1
        zf.writestr(
            "readme.txt",
            "SOC 2 Audit Package\n"
            f"Generated: {datetime.now().isoformat()}\n"
            f"Total evidence: {manifest['total_evidence']}\n"
            f"Evidence files included: {files_included}\n"
            f"Controls covered: {manifest['controls_covered']}\n"
            f"Manifest hash: {manifest['manifest_hash']}\n"
            f"Frozen period active: {workspace_is_locked(ws)}\n",
        )
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=audit_package.zip"},
    )


@app.get("/api/reports/readiness-summary")
def get_readiness_summary(client_id: Optional[str] = Query(None)) -> StreamingResponse:
    ws = load_workspace(client_id)
    dash = compute_dashboard(ws)
    lines = [
        "metric,value",
        f"org_name,{dash.get('org_name', '')}",
        f"readiness_pct,{dash.get('readiness_pct', 0)}",
        f"evidence_coverage_pct,{dash.get('evidence_coverage_pct', 0)}",
        f"auto_coverage_pct,{dash.get('auto_coverage_pct', 0)}",
        f"controls_met,{dash.get('controls_met', 0)}",
        f"controls_total,{dash.get('controls_total', 0)}",
        f"controls_assessed,{dash.get('controls_assessed', 0)}",
        f"open_gaps,{dash.get('open_gaps', 0)}",
        f"workspace_locked,{workspace_is_locked(ws)}",
    ]
    return StreamingResponse(
        io.StringIO("\n".join(lines)),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=readiness_summary.csv"},
    )


@app.get("/api/reports/system-description")
def get_system_description(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    md = generate_system_description(ws)
    slug = (ws.get("org_name") or "organization").replace(" ", "_")[:40]
    return Response(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="system_description_{slug}.md"'},
    )


@app.get("/api/reports/system-description-docx")
def get_system_description_docx(
    client_id: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
) -> StreamingResponse:
    ws = load_workspace(client_id)
    _require_export(ws)
    org_profile = ws.get("org_profile") or {}
    if not org_profile.get("org_name"):
        org_profile["org_name"] = ws.get("org_name", "Organization")
    slug = (ws.get("org_name") or "organization").replace(" ", "_")[:40]

    if format == "pdf":
        from readiness import compute_dashboard
        dash = compute_dashboard(ws)
        sections = [
            {"type": "heading", "content": "System Description", "level": 0},
            {"type": "kv", "key": "Organization", "value": org_profile.get("org_name", "")},
            {"type": "kv", "key": "System", "value": org_profile.get("system_name", "")},
            {"type": "kv", "key": "Readiness", "value": f"{dash.get('readiness_pct', 0):.0f}%"},
            {"type": "kv", "key": "Evidence coverage", "value": f"{dash.get('evidence_coverage_pct', 0):.0f}%"},
            {"type": "kv", "key": "Open gaps", "value": str(dash.get('open_gaps', 0))},
            {"type": "page_break"},
            {"type": "heading", "content": "System Overview", "level": 1},
            {"type": "text", "content": org_profile.get("system_description", "Not provided.")},
            {"type": "text", "content": f"Architecture: {org_profile.get('architecture_summary', 'Not provided.')}"},
            {"type": "text", "content": f"Boundary: {org_profile.get('boundary_description', 'Not provided.')}"},
            {"type": "heading", "content": "Control Environment", "level": 1},
        ]
        for c in dash.get("coverage", []):
            sections.append({"type": "kv", "key": c.get("id", ""), "value": f"{c.get('status', '')} | Evidence: {c.get('evidence_count', 0)}"})
        pdf_bytes = generate_pdf(f"System Description — {slug}", sections)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="System_Description_{slug}.pdf"'},
        )

    docx_bytes = generate_system_description_docx(ws)
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="System_Description_{slug}.docx"'},
    )


@app.get("/api/reports/control-matrix")
def get_control_matrix(client_id: Optional[str] = Query(None)) -> StreamingResponse:
    ws = load_workspace(client_id)
    _require_export(ws)
    xlsx_bytes = generate_control_matrix(ws)
    slug = (ws.get("org_name") or "organization").replace(" ", "_")[:40]
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="Control_Matrix_{slug}.xlsx"'},
    )


@app.get("/api/reports/gap-analysis")
def get_gap_analysis(
    client_id: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
) -> StreamingResponse:
    ws = load_workspace(client_id)
    _require_export(ws)
    slug = (ws.get("org_name") or "organization").replace(" ", "_")[:40]
    if format == "pdf":
        from readiness_assessment import run_readiness_assessment
        assessment = run_readiness_assessment(ws)
        sections = [
            {"type": "heading", "content": "Gap Analysis", "level": 0},
            {"type": "kv", "key": "Organization", "value": ws.get("org_name", "")},
            {"type": "kv", "key": "Readiness", "value": f"{assessment.get('readiness_pct', 0):.0f}%"},
            {"type": "kv", "key": "Open gaps", "value": str(assessment.get('gap_count', 0))},
            {"type": "page_break"},
        ]
        for gap in assessment.get("open_gaps", []):
            sections.append({"type": "heading", "content": f"{gap['control_id']}: {gap['name']}", "level": 2})
            sections.append({"type": "kv", "key": "Status", "value": gap.get("status", "")})
            sections.append({"type": "kv", "key": "Owner", "value": gap.get("owner", "Unassigned")})
            if not gap.get("has_evidence"):
                sections.append({"type": "bullet", "content": "Missing evidence — upload artifacts"})
            if not gap.get("has_narrative"):
                sections.append({"type": "bullet", "content": "Missing narrative — describe implementation"})
        if not assessment.get("open_gaps"):
            sections.append({"type": "text", "content": "No open gaps identified. All controls are complete."})
        pdf_bytes = generate_pdf(f"Gap Analysis — {slug}", sections)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="Gap_Analysis_{slug}.pdf"'},
        )

    docx_bytes = generate_gap_analysis(ws)
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="Gap_Analysis_{slug}.docx"'},
    )


@app.get("/api/reports/executive-summary")
def get_executive_summary(client_id: Optional[str] = Query(None)) -> StreamingResponse:
    ws = load_workspace(client_id)
    _require_export(ws)
    pdf_bytes = generate_executive_summary(ws)
    slug = (ws.get("org_name") or "organization").replace(" ", "_")[:40]
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Executive_Summary_{slug}.pdf"'},
    )


@app.get("/api/reports/exceptions")
def get_exceptions_csv(client_id: Optional[str] = Query(None)) -> StreamingResponse:
    ws = load_workspace(client_id)
    _require_export(ws)
    csv_bytes = export_poam_csv(
        answers=ws.get("answers") or {},
        exceptions=ws.get("exceptions") or [],
    )
    slug = (ws.get("org_name") or "organization").replace(" ", "_")[:40]
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="Exceptions_{slug}.csv"'},
    )


@app.get("/api/reports/exceptions-docx")
def get_exceptions_docx(client_id: Optional[str] = Query(None)) -> StreamingResponse:
    ws = load_workspace(client_id)
    _require_export(ws)
    org_name = ws.get("org_name") or "Organization"
    docx_bytes = export_poam_docx(
        org_name=org_name,
        answers=ws.get("answers") or {},
        exceptions=ws.get("exceptions") or [],
    )
    slug = org_name.replace(" ", "_")[:40]
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="Exceptions_{slug}.docx"'},
    )


@app.get("/api/reports/audit-package-enhanced")
def get_enhanced_audit_package(client_id: Optional[str] = Query(None)) -> StreamingResponse:
    ws = load_workspace(client_id)
    _require_export(ws)
    cid = ws.get("client_id") or active_client_id()
    evidence_dir = client_evidence_dir(cid)
    org_profile = ws.get("org_profile") or {}
    if not org_profile.get("org_name"):
        org_profile["org_name"] = ws.get("org_name", "Organization")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # System Description DOCX
        ssp_bytes = generate_system_description_docx(ws)
        zf.writestr("System_Description.docx", ssp_bytes)

        # Exceptions CSV
        poam_bytes = export_poam_csv(
            answers=ws.get("answers") or {},
            exceptions=ws.get("exceptions") or [],
        )
        zf.writestr("Exceptions.csv", poam_bytes)

        # Evidence index CSV
        manifest = generate_manifest(ws)
        lines = ["control_id,filename,sha256,upload_date,review_status"]
        for item in manifest["items"]:
            lines.append(f"{item['control_id']},{item['filename']},{item['sha256']},{item['upload_date']},{item['review_status']}")
        zf.writestr("evidence_index.csv", "\n".join(lines))

        # Readiness summary
        dash = compute_dashboard(ws)
        summary_lines = [
            "metric,value",
            f"org_name,{dash.get('org_name', '')}",
            f"readiness_pct,{dash.get('readiness_pct', 0)}",
            f"evidence_coverage_pct,{dash.get('evidence_coverage_pct', 0)}",
            f"controls_met,{dash.get('controls_met', 0)}",
            f"controls_total,{dash.get('controls_total', 0)}",
            f"open_gaps,{dash.get('open_gaps', 0)}",
        ]
        zf.writestr("readiness_summary.csv", "\n".join(summary_lines))

        # System description
        md = generate_system_description(ws)
        zf.writestr("system_description.md", md)

        # All evidence files
        files_included = 0
        for cid_key in get_in_scope_criteria_ids(ws.get("tsc_scope") or dict(DEFAULT_SCOPE)):
            ans = ws.get("answers", {}).get(cid_key, default_control_answer())
            for ev in ans.get("evidence") or []:
                fname = ev.get("filename") or ""
                if not fname:
                    continue
                payload = get_evidence_bytes(cid_key, ev, evidence_dir=evidence_dir)
                if payload:
                    zf.writestr(f"evidence/{cid_key}/{fname}", payload)
                    files_included += 1

        # README
        zf.writestr(
            "README.txt",
            f"SOC 2 Audit Package\n"
            f"Generated: {datetime.now().isoformat()}\n"
            f"Organization: {ws.get('org_name', '')}\n"
            f"Total evidence: {manifest['total_evidence']}\n"
            f"Evidence files included: {files_included}\n"
            f"Controls covered: {manifest['controls_covered']}\n"
            f"Readiness: {dash.get('readiness_pct', 0)}%\n"
            f"Manifest hash: {manifest['manifest_hash']}\n"
            f"\nContents:\n"
            f"  System_Description.docx - System Description document\n"
            f"  Exceptions.csv          - Control exceptions\n"
            f"  evidence_index.csv      - Evidence inventory\n"
            f"  readiness_summary.csv   - Readiness metrics\n"
            f"  system_description.md   - System description (Markdown)\n"
            f"  evidence/               - All evidence files\n",
        )

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="audit_package_{(ws.get("org_name") or "org").replace(" ","_")[:30]}.zip"'},
    )


@app.get("/api/clients")
def get_clients() -> List[Dict[str, str]]:
    ensure_default_client()
    return list_clients()


@app.post("/api/clients")
def post_create_client(body: ClientCreateBody) -> Dict[str, str]:
    name = (body.name or "").strip()
    if not name:
        raise HTTPException(400, "Client name is required")
    cid = create_client(name)
    ws = load_workspace(cid)
    _require_edit_org(ws)
    ws["org_name"] = name
    save_workspace(ws)
    _audit_log(ws, "created", "client", cid, {"name": name})
    return {"client_id": cid, "name": name, "active_client_id": cid}


@app.post("/api/clients/{client_id}/activate")
def post_activate_client(client_id: str) -> Dict[str, str]:
    ensure_default_client()
    if client_id not in {c["id"] for c in list_clients()}:
        raise HTTPException(404, "Client not found")
    set_active_client_id(client_id)
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    _audit_log(ws, "activated", "client", client_id)
    return {"active_client_id": client_id}


@app.patch("/api/clients/{client_id}")
def patch_client(client_id: str, body: ClientRenameBody) -> Dict[str, str]:
    name = (body.name or "").strip()
    if not name:
        raise HTTPException(400, "Client name is required")
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_org(ws)
    rename_client(client_id, name)
    _audit_log(ws, "renamed", "client", client_id, {"new_name": name})
    return {"client_id": client_id, "name": name}


@app.delete("/api/clients/{client_id}")
def delete_client_endpoint(client_id: str) -> Dict[str, str]:
    ensure_default_client()
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_org(ws)
    if not delete_client(client_id):
        raise HTTPException(400, "Cannot delete this client")
    _audit_log(load_workspace(active_client_id()), "deleted", "client", client_id)
    return {"active_client_id": active_client_id()}


@app.get("/api/settings")
def settings(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ensure_default_client()
    active = client_id or active_client_id()
    ws = load_workspace(active)
    auth_cfg = public_auth_config()
    auth_user = get_auth_user()
    role = _ws_role(ws)
    return {
        "org_name": ws.get("org_name", ""),
        "current_role": role,
        "current_user_name": _current_user_name(ws),
        "capabilities": _capabilities(role),
        "status_options": STATUS_OPTIONS,
        "operating_status_options": OPERATING_STATUS_OPTIONS,
        "user_roles": USER_ROLES,
        "is_demo": bool(ws.get("is_demo")),
        "demo_id": ws.get("demo_id"),
        "workspace_locked": workspace_is_locked(ws),
        "auth_enabled": auth_cfg["enabled"],
        "auth_role_locked": auth_cfg["role_locked"],
        "auth_user_email": auth_user.email if auth_user else "",
        "clients": list_clients(),
        "active_client_id": active,
    }


@app.patch("/api/settings/role")
def patch_role(body: RolePatch, client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    if auth_enabled():
        raise HTTPException(403, "Role is assigned by Microsoft Entra ID groups")
    if body.role not in USER_ROLES:
        raise HTTPException(400, f"Invalid role: {body.role}")
    ws = load_workspace(client_id)
    old_role = ws.get("current_role", "")
    ws["current_role"] = body.role
    save_workspace(ws)
    field_diffs = {}
    if old_role != body.role:
        field_diffs["role"] = {"old": old_role, "new": body.role}
    _audit_log(ws, "updated", "user_role", "", {"role": body.role, "field_diffs": field_diffs, "security": True})
    return {"current_role": body.role}


@app.patch("/api/settings/user-name")
def patch_user_name(body: UserNamePatch, client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    if auth_enabled():
        raise HTTPException(403, "User name comes from your Microsoft Entra ID profile")
    ws = load_workspace(client_id)
    ws["current_user_name"] = (body.name or "").strip()
    save_workspace(ws)
    _audit_log(ws, "updated", "user_name", "", {"name": ws["current_user_name"]})
    return {"current_user_name": ws["current_user_name"]}


@app.get("/api/settings/policy-variables")
def get_policy_variables(client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    ws = load_workspace(client_id)
    profile = merge_org_profile(ws.get("org_profile"), ws.get("org_name", ""))
    return {
        "company_name": profile.get("org_name") or ws.get("org_name", "Your Organization"),
        "system_name": profile.get("system_name") or "the system",
        "system_owner": profile.get("system_owner") or "",
        "compliance_officer": profile.get("compliance_officer") or "",
        "it_admin": profile.get("it_admin") or "",
        "auditor_name": profile.get("auditor_name") or "",
        "effective_date": datetime.now().strftime("%B %d, %Y"),
        "review_date": (datetime.now().replace(year=datetime.now().year + 1)).strftime("%B %d, %Y"),
        "org_address": profile.get("org_address") or "",
        "org_phone": profile.get("org_phone") or "",
    }


# ── Organization Profile routes ──────────────────────────────

@app.get("/api/organization")
def get_organization(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    org_profile = merge_org_profile(ws.get("org_profile"), ws.get("org_name", ""))
    env = merge_env_scope(ws.get("env_scope"))
    inventory = merge_org_inventory(ws.get("org_inventory"))
    answers = ws.get("answers") or {}

    return {
        "org_profile": org_profile,
        "env_scope": env,
        "env_scope_labels": {"yes_no": YES_NO_LABELS, "cloud": CLOUD_LABELS},
        "env_scope_complete": env_scope_complete(env),
        "env_scope_summary": format_env_scope_summary(env),
        "scoping_suggestions": scoping_suggestions(env, answers),
        "org_inventory": inventory,
        "inventory_columns": INVENTORY_COLUMNS,
        "audit_log": ws.get("audit_log") or [],
        "needs_wizard": profile_needs_wizard(org_profile),
        "wizard_steps": WIZARD_STEPS,
        "field_labels": FIELD_LABELS,
        "field_placeholders": FIELD_PLACEHOLDERS,
        "org_name": ws.get("org_name", ""),
        "scoping_completed": bool(ws.get("scoping_completed")),
    }


@app.get("/api/documents")
def get_documents(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
    scoped_controls = get_in_scope_criteria_ids(scope)
    docs = build_documents_list(ws.get("answers") or {}, scoped_controls)
    return {"documents": docs, "total": len(docs)}


@app.patch("/api/org-profile")
def update_org_profile(body: OrgProfileBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_org(ws)
    profile = merge_org_profile(ws.get("org_profile"), ws.get("org_name", ""))
    updates = body.model_dump(exclude_none=True)
    for field, val in updates.items():
        if field in profile:
            profile[field] = val
    ws["org_profile"] = profile
    if "org_name" in updates and updates["org_name"]:
        ws["org_name"] = updates["org_name"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.setdefault("audit_log", []).append({
        "timestamp": now,
        "event": "org_profile_updated",
        "fields": list(updates.keys()),
        "user": ws.get("current_user_name", ""),
    })
    _audit_log(ws, "updated", "org_profile", "", {"fields": list(updates.keys())})
    save_workspace(ws)
    return {"org_profile": profile, "org_name": ws.get("org_name", "")}


@app.patch("/api/env-scope")
def update_env_scope(body: EnvScopeBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_org(ws)
    env = merge_env_scope(ws.get("env_scope"))
    updates = body.model_dump(exclude_none=True)
    for field, val in updates.items():
        if field in env:
            env[field] = val
    ws["env_scope"] = env
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.setdefault("audit_log", []).append({
        "timestamp": now,
        "event": "env_scope_updated",
        "fields": list(updates.keys()),
        "user": ws.get("current_user_name", ""),
    })
    save_workspace(ws)
    _audit_log(ws, "updated", "env_scope", "", {"fields": list(updates.keys())})
    return {
        "env_scope": env,
        "env_scope_complete": env_scope_complete(env),
        "env_scope_summary": format_env_scope_summary(env),
    }


@app.patch("/api/inventory")
def update_inventory(body: InventoryUpdateBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_org(ws)
    inventory = set_inventory_assets(body.assets)
    ws["org_inventory"] = inventory
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.setdefault("audit_log", []).append({
        "timestamp": now,
        "event": "inventory_updated",
        "asset_count": len(body.assets),
        "user": ws.get("current_user_name", ""),
    })
    save_workspace(ws)
    _audit_log(ws, "updated", "inventory", "", {"asset_count": len(body.assets)})
    return {"org_inventory": inventory}


@app.get("/api/readiness/assessment")
def get_readiness_assessment(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    test_stats = get_stats(framework="SOC2")
    test_pass_rate = test_stats.get("pass_rate", 0.0)
    test_total = test_stats.get("total", 0)
    return run_readiness_assessment(ws, test_pass_rate=test_pass_rate, test_total=test_total)


@app.get("/api/my-work")
def get_my_work_items(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    user = _current_user_name(ws) or ws.get("current_user_name", "")
    return get_my_work(ws, user)


class CommentBody(BaseModel):
    text: str
    parent_id: Optional[str] = None


@app.post("/api/controls/{control_id}/comments")
def add_comment(control_id: str, body: CommentBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
    if not is_in_scope(control_id, scope):
        raise HTTPException(404, "Control is out of scope")
    _guard_editable(ws)
    _require_edit_controls(ws)
    ans = ws["answers"].setdefault(control_id, default_control_answer())
    comments = list(ans.get("comments") or [])
    import re
    mentions = list(set(re.findall(r"@(\w[\w\s]*\w|\w)", body.text)))
    comment = {
        "id": str(uuid.uuid4())[:8],
        "text": body.text,
        "author": ws.get("current_user_name", ""),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "parent_id": body.parent_id,
        "mentions": mentions,
    }
    comments.append(comment)
    ans["comments"] = comments
    save_workspace(ws)
    _audit_log(ws, "created", "comment", comment["id"], {"control_id": control_id, "text": body.text[:100]})
    return {"comment": comment}


@app.delete("/api/controls/{control_id}/comments/{comment_id}")
def delete_comment(control_id: str, comment_id: str, client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    if control_id not in SOC2_CONTROLS:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
    if not is_in_scope(control_id, scope):
        raise HTTPException(404, "Control is out of scope")
    _guard_editable(ws)
    _require_edit_controls(ws)
    _guard_editable(ws)
    ans = ws["answers"].get(control_id, {})
    comments = list(ans.get("comments") or [])
    kept = [c for c in comments if c.get("id") != comment_id]
    if len(kept) == len(comments):
        raise HTTPException(404, "Comment not found")
    ans["comments"] = kept
    save_workspace(ws)
    _audit_log(ws, "deleted", "comment", comment_id, {"control_id": control_id})
    return {"status": "deleted"}


@app.get("/api/demo/status")
def demo_status(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {
        "is_demo": bool(ws.get("is_demo")),
        "demo_id": ws.get("demo_id"),
        "org_name": ws.get("org_name"),
        "label": ws.get("org_name") if ws.get("is_demo") else None,
    }


@app.post("/api/demo/load")
def post_load_demo(
    demo_id: str = Query("northwind"),
    client_id: Optional[str] = Query(None),
    org_name: Optional[str] = Query(None),
) -> Dict[str, Any]:
    if not demo_api_enabled():
        raise HTTPException(403, "Demo workspaces are disabled in this environment")
    ws = load_demo(demo_id=demo_id, client_id=client_id, org_name=org_name)
    _require_edit_org(ws)
    dash = compute_dashboard(ws)
    _audit_log(ws, "loaded", "demo", demo_id, {"org_name": ws.get("org_name")})
    return {
        "client_id": ws["client_id"],
        "org_name": ws["org_name"],
        "demo_id": demo_id,
        "readiness_pct": dash["readiness_pct"],
        "is_demo": True,
        "label": ws["org_name"],
    }


@app.post("/api/demo/clear")
def post_clear_demo(client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    if not demo_api_enabled():
        raise HTTPException(403, "Demo workspaces are disabled in this environment")
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    ws["org_name"] = "Your Organization"
    ws["answers"] = {cid: default_control_answer() for cid in SOC2_CONTROLS}
    ws["audit_periods"] = []
    ws["evidence_requests"] = []
    ws["is_demo"] = False
    ws["demo_id"] = None
    save_workspace(ws)
    _audit_log(ws, "cleared", "demo", "", {})
    return {"status": "cleared"}


@app.get("/api/controls")
def get_controls(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    rows = list_control_summaries(ws)
    if category:
        rows = [r for r in rows if r["category"].lower() == category.lower()]
    if q:
        needle = q.lower()
        rows = [
            r
            for r in rows
            if needle in r["id"].lower()
            or needle in r["name"].lower()
            or needle in (r.get("description") or "").lower()
        ]
    categories = sorted({r["category"] for r in list_control_summaries(ws)})
    return {
        "controls": rows,
        "status_options": STATUS_OPTIONS,
        "category_options": [{"id": c, "label": c} for c in categories],
    }


def _pof_stats(control_id: str, ans: Dict[str, Any]) -> Dict[str, Any]:
    return pof_coverage_stats(ans, control_id)


@app.get("/api/controls/{control_id}")
def get_control(control_id: str, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
    if not is_in_scope(control_id, scope):
        raise HTTPException(404, "Control is out of scope")
    meta = SOC2_CONTROLS[control_id]
    ans = ws["answers"].get(control_id, default_control_answer())
    workspace_evidence = [
        {k: v for k, v in ev.items() if k != "data_bytes"}
        for ev in (ans.get("evidence") or [])
    ]
    try:
        from evidence_hub.store import list_evidence
        hub_evidence = [
            {
                "filename": e.get("filename", ""),
                "upload_date": e.get("uploaded_at", ""),
                "sha256": e.get("sha256", ""),
                "review_status": e.get("review_status", "pending"),
                "is_hub_evidence": True,
                "hub_id": e.get("id", ""),
            }
            for e in list_evidence(framework_id="SOC2", control_id=control_id)
        ]
    except Exception:
        hub_evidence = []
    return {
        "id": control_id,
        "code": control_id,
        "category": meta["category"],
        "name": meta["title"],
        "description": meta["description"],
        "status": ans.get("status", "NOT STARTED"),
        "operating_status": ans.get("operating_status", "NOT TESTED"),
        "implementation_narrative": ans.get("implementation_narrative", ""),
        "assessor_notes": ans.get("assessor_notes", ""),
        "owner": ans.get("owner", ""),
        "target_date": ans.get("target_date", ""),
        "remediation_plan": ans.get("remediation_plan", ""),
        "frequency": ans.get("frequency", ""),
        "last_review_date": ans.get("last_review_date", ""),
        "next_review_date": ans.get("next_review_date", ""),
        "linked_policies": ans.get("linked_policies", []),
        "linked_assets": ans.get("linked_assets", []),
        "linked_team": ans.get("linked_team", []),
        "linking_profile": {"policies": [], "assets": [], "team": []},
        "evidence": workspace_evidence + hub_evidence,
        "status_options": STATUS_OPTIONS,
        "operating_status_options": OPERATING_STATUS_OPTIONS,
        "frequency_options": FREQUENCY_OPTIONS,
        "has_narrative": bool((ans.get("implementation_narrative") or "").strip()),
        "evidence_count": len(workspace_evidence) + len(hub_evidence),
        "evidence_guidance": get_guidance(control_id),
        "reviews": ans.get("reviews") or [],
        "points_of_focus": [{**pof, "evidence_hints": get_pof_hints(pof)} for pof in meta.get("points_of_focus", [])],
        "pof_statuses": ans.get("points_of_focus") or {},
        "cuecs": get_cuecs_for_control(ws, control_id),
        "comments": ans.get("comments") or [],
        **_pof_stats(control_id, ans),
    }


class CuecCreateBody(BaseModel):
    control_id: str
    description: str = ""
    assigned_to: str = ""


class CuecUpdateBody(BaseModel):
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


@app.get("/api/cuec")
def get_cuecs(client_id: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    ws = load_workspace(client_id)
    return list_cuecs(ws)


@app.post("/api/cuec")
def post_cuec(body: CuecCreateBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    cuec = create_cuec(ws, body.control_id, body.description, body.assigned_to)
    save_workspace(ws)
    return {"cuec": cuec}


@app.patch("/api/cuec/{cuec_id}")
def patch_cuec(cuec_id: str, body: CuecUpdateBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    cuec = update_cuec(ws, cuec_id, **body.model_dump(exclude_none=True))
    if not cuec:
        raise HTTPException(404, "CUEC not found")
    save_workspace(ws)
    return {"cuec": cuec}


@app.delete("/api/cuec/{cuec_id}")
def post_delete_cuec(cuec_id: str, client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    if not delete_cuec(ws, cuec_id):
        raise HTTPException(404, "CUEC not found")
    save_workspace(ws)
    return {"status": "deleted"}


@app.patch("/api/controls/{control_id}")
def patch_control_endpoint(
    control_id: str,
    body: ControlPatchBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    old_status = ws.get("answers", {}).get(control_id, {}).get("status")
    ws = patch_control(
        ws,
        control_id,
        status=body.status,
        implementation_narrative=body.implementation_narrative,
        assessor_notes=body.assessor_notes,
        owner=body.owner,
        target_date=body.target_date,
        remediation_plan=body.remediation_plan,
        operating_status=body.operating_status,
        frequency=body.frequency,
        last_review_date=body.last_review_date,
        next_review_date=body.next_review_date,
        linked_policies=body.linked_policies,
        linked_assets=body.linked_assets,
        linked_team=body.linked_team,
        points_of_focus=body.points_of_focus,
    )
    changed = body.model_dump(exclude_none=True)
    details = {"fields": list(changed.keys())}
    if "status" in changed:
        new_status = ws.get("answers", {}).get(control_id, {}).get("status")
        if old_status != new_status:
            details["field_diffs"] = {"status": {"old": old_status, "new": new_status}}
    _audit_log(ws, "updated", "control", control_id, details)
    return get_control(control_id, client_id=ws["client_id"])


@app.patch("/api/controls/{control_id}/pofs/{pof_id}")
def patch_pof_endpoint(
    control_id: str,
    pof_id: str,
    body: PatchPofBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    try:
        ws = patch_pof(ws, control_id, pof_id, status=body.status, justification=body.justification)
    except ValueError as e:
        raise HTTPException(400, str(e))
    _audit_log(ws, "updated", "pof", pof_id, {"control_id": control_id, "status": body.status})
    return get_control(control_id, client_id=ws["client_id"])


@app.patch("/api/controls/{control_id}/pofs")
def bulk_patch_pofs_endpoint(
    control_id: str,
    body: BulkPofBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    try:
        ws = bulk_patch_pofs(ws, control_id, body.updates)
    except ValueError as e:
        raise HTTPException(400, str(e))
    _audit_log(ws, "bulk_updated", "pofs", control_id, {"pof_count": len(body.updates)})
    return get_control(control_id, client_id=ws["client_id"])


@app.post("/api/controls/{control_id}/evidence/{filename}/review")
def post_review_evidence(
    control_id: str,
    filename: str,
    body: ReviewEvidenceBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
    if not is_in_scope(control_id, scope):
        raise HTTPException(404, "Control is out of scope")
    _guard_editable(ws)
    _require_edit_controls(ws)
    try:
        ws = review_evidence(ws, control_id, filename, reviewer=body.reviewer, status=body.status, comment=body.comment)
    except ValueError as e:
        raise HTTPException(400, str(e))
    save_workspace(ws)
    _audit_log(ws, "reviewed", "evidence", filename, {"control_id": control_id, "status": body.status, "reviewer": body.reviewer})
    return {"status": "ok", "review_status": body.status}


@app.post("/api/controls/{control_id}/evidence")
async def upload_evidence(
    control_id: str,
    file: UploadFile = File(...),
    client_id: Optional[str] = Query(None),
    valid_from: Optional[str] = Query(None),
    valid_to: Optional[str] = Query(None),
) -> Dict[str, Any]:
    if control_id not in SOC2_CONTROLS:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    scope = ws.get("tsc_scope") or dict(DEFAULT_SCOPE)
    if not is_in_scope(control_id, scope):
        raise HTTPException(404, "Control is out of scope")
    _guard_editable(ws)
    _require_edit_controls(ws)
    data = await file.read()
    if not within_size_limit(data):
        raise HTTPException(413, "Evidence file exceeds size limit")
    import hashlib
    from datetime import datetime

    filename = safe_evidence_filename(file.filename or "evidence")
    sha = hashlib.sha256(data).hexdigest()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    vf = valid_from or stamp.split(" ")[0]
    try:
        ws = attach_evidence(ws, control_id, filename=filename, data=data, sha256=sha, upload_date=stamp, valid_from=vf, valid_to=valid_to)
    except ValueError as e:
        raise HTTPException(400, str(e))
    save_workspace(ws)
    _audit_log(ws, "created", "evidence", filename, {"control_id": control_id})
    return get_control(control_id, client_id=ws["client_id"])


@app.get("/api/controls/{control_id}/evidence/{filename}")
def download_evidence(
    control_id: str,
    filename: str,
    client_id: Optional[str] = Query(None),
) -> Response:
    ws = load_workspace(client_id)
    ev, data = _resolve_evidence_file(ws, control_id, filename)
    safe = ev.get("filename") or safe_evidence_filename(filename)
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{safe}"'},
    )


@app.delete("/api/controls/{control_id}/evidence/{filename}")
def delete_evidence_file(
    control_id: str,
    filename: str,
    client_id: Optional[str] = Query(None),
) -> Dict[str, str]:
    ws = load_workspace(client_id)
    _guard_editable(ws)
    _require_edit_controls(ws)
    try:
        detach_evidence(ws, control_id, filename=filename)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    _audit_log(ws, "deleted", "evidence", filename, {"control_id": control_id})
    return {"status": "deleted", "filename": safe_evidence_filename(filename)}


# ── Policy & Attestation routes ───────────────────────────────
# Handled by shared packages/policies/routes.py via policy_router


# ── Audit Findings routes ─────────────────────────────────────



@app.get("/api/help")
def get_help():
    return {"views": {}, "faq": []}

@app.get("/api/collectors")
def get_collectors(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {
        "connectors": list_connectors(),
        "monitoring": monitoring_summary(),
        "drift_events": get_events(limit=25),
        "freshness": freshness_for_workspace(ws["answers"]),
        "recent_runs": recent_runs(),
    }


@app.patch("/api/collectors/{connector_id}/schedule")
def patch_collector_schedule(connector_id: str, body: CollectorScheduleBody) -> Dict[str, Any]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    state = patch_monitor_schedule(
        connector_id,
        enabled=body.enabled,
        interval=body.interval,  # type: ignore[arg-type]
        attach_on_run=body.attach_on_run,
    )
    ws = load_workspace(None)
    _require_edit_controls(ws)
    _audit_log(ws, "updated", "collector_schedule", connector_id, {"enabled": body.enabled, "interval": body.interval})
    return state.to_dict()


@app.put("/api/collectors/{connector_id}/credentials")
def put_collector_credentials(connector_id: str, body: CollectorCredentialsBody) -> Dict[str, Any]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    meta = CONNECTOR_CATALOG[connector_id]
    creds = body.credentials
    missing = [f for f in meta["required_fields"] if not creds.get(f)]
    if missing:
        raise HTTPException(400, f"Missing required fields: {', '.join(missing)}")
    ws = load_workspace(None)
    _require_edit_controls(ws)
    save_credentials(connector_id, creds)
    ws = load_workspace(None)
    _audit_log(ws, "updated", "collector_credentials", connector_id, {"fields": list(creds.keys()), "security": True})
    return credentials_status(connector_id, meta["required_fields"])


@app.delete("/api/collectors/{connector_id}/credentials")
def remove_collector_credentials(connector_id: str) -> Dict[str, str]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    delete_credentials(connector_id)
    ws = load_workspace(None)
    _require_edit_controls(ws)
    _audit_log(ws, "deleted", "collector_credentials", connector_id, {"security": True})
    return {"status": "deleted"}


@app.post("/api/collectors/{connector_id}/run")
def post_collector_run(
    connector_id: str,
    body: CollectorRunBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    ws = load_workspace(client_id)
    if body.attach:
        _guard_editable(ws)
        _require_edit_controls(ws)
    try:
        if body.attach:
            result = run_and_attach(
                connector_id,
                use_fixture=body.use_fixture,
                client_id=client_id,
                control_ids=body.control_ids,
            )
            _audit_log(ws, "ran", "collector", connector_id, {"fixture": body.use_fixture, "attached": True})
            return {
                "run": result.run.to_dict(),
                "attached": [a.to_dict() for a in result.attached],
                "drift_events": result.drift_events,
            }
        run = run_collector(connector_id, use_fixture=body.use_fixture, client_id=client_id)
        _audit_log(ws, "ran", "collector", connector_id, {"fixture": body.use_fixture, "attached": False})
        return {"run": run.to_dict(), "attached": [], "drift_events": run.drift_events}
    except Exception as exc:
        print(f"ERROR: Collector run failed: {exc}", flush=True)
        raise HTTPException(400, "Collector run failed") from exc


@app.post("/api/collectors/monitoring/run-due")
def post_run_due(body: RunDueBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    if workspace_is_locked(ws):
        raise HTTPException(409, _workspace_locked_detail())
    _require_edit_controls(ws)
    _audit_log(ws, "ran", "collector_monitoring", "due", {"use_fixture_if_unconfigured": body.use_fixture_if_unconfigured})
    try:
        return run_due_connectors(
            client_id=client_id,
            use_fixture_if_unconfigured=body.use_fixture_if_unconfigured,
        )
    except Exception as exc:
        print(f"ERROR: Monitoring run failed: {exc}", flush=True)
        raise HTTPException(500, "Monitoring run failed") from exc


@app.get("/api/webhooks")
def get_webhooks() -> Dict[str, Any]:
    return {
        "collectors": list_webhook_collectors(),
        "env_token_configured": bool(env_webhook_token()),
    }


@app.post("/api/webhooks")
def post_webhook(body: WebhookCreateBody) -> Dict[str, Any]:
    collector = create_webhook_collector(body.name, body.source_system)
    ws = load_workspace(None)
    _require_edit_controls(ws)
    _audit_log(ws, "created", "webhook_collector", collector.id, {"name": body.name, "security": True})
    return {
        "collector": collector.to_dict(include_token=False),
        "webhook_token": collector.webhook_token,
        "usage": f"POST /api/webhooks/ingest/{collector.id} with the token in the Authorization header",
    }


@app.delete("/api/webhooks/{collector_id}")
def delete_webhook(collector_id: str) -> Dict[str, str]:
    delete_webhook_collector(collector_id)
    ws = load_workspace(None)
    _require_edit_controls(ws)
    _audit_log(ws, "deleted", "webhook_collector", collector_id, {"security": True})
    return {"status": "deleted"}


@app.post("/api/webhook/external")
async def post_webhook_external(
    request: Request,
    body: Dict[str, Any],
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    auth = request.headers.get("authorization") or ""
    token = auth[7:] if auth.lower().startswith("bearer ") else auth
    ws = load_workspace(client_id)
    _guard_editable(ws)
    try:
        result = ingest_webhook_payload(body, token=token or None, client_id=client_id, attach=True)
    except PermissionError as exc:
        raise HTTPException(401, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        print(f"ERROR: Webhook ingestion failed: {exc}", flush=True)
        raise HTTPException(500, "Webhook ingestion failed") from exc
    if result.status == "duplicate":
        raise HTTPException(409, detail=result.to_dict())
    _audit_log(ws, "ingested", "webhook_payload", "", {"source": body.get("source_system", "external"), "check_count": len(body.get("checks", []))})
    return result.to_dict()


@app.post("/api/webhooks/ingest/{collector_id}")
async def post_webhook_ingest_legacy(
    collector_id: str,
    request: Request,
    body: Dict[str, Any],
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    return await post_webhook_external(request, body, client_id)


@app.get("/api/priority-queue")
def api_priority_queue(
    request: Request,
    limit: int = Query(30, ge=1, le=100),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    answers = ws.get("answers", {})
    risks = ws.get("risks", [])
    exceptions = ws.get("exceptions", [])
    scope = ws.get("tsc_scope")
    return get_priority_queue(answers, risks, exceptions, scope=scope, limit=limit)


app.include_router(audit_router)
app.include_router(testing_router)
app.include_router(auth_router)
app.include_router(reviews_router)
