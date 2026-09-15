"""FastAPI entry — run from platform/:

    uvicorn main:app --app-dir server --reload --port 8080
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

PLATFORM = Path(__file__).resolve().parents[1]
CORE = PLATFORM / "core"
PACKAGES = PLATFORM / "packages"
if not PACKAGES.is_dir():
    PACKAGES = PLATFORM.parents[1] / "packages"  # local dev: khestra/
EVIDENCE = PACKAGES / "evidence"
# PACKAGES must come before CORE so shared packages (controls, remediation) shadow per-app modules.
for path in (PACKAGES, EVIDENCE, CORE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
# Re-insert PACKAGES at front so it wins over CORE
if str(PACKAGES) in sys.path:
    sys.path.remove(str(PACKAGES))
    sys.path.insert(0, str(PACKAGES))

from config import DATA_DIR as CMMC_DATA_DIR  # noqa: E402
from kevidence.config import configure as configure_evidence  # noqa: E402
configure_evidence(data_dir=CMMC_DATA_DIR, platform_root=PLATFORM)
from kevidence.availability import collectors_available

if collectors_available():
    import cmmc_collectors  # noqa: F401,E402 — register CMMC control mapping

try:
    from dotenv import load_dotenv

    load_dotenv(PLATFORM / ".env", override=True)
except ImportError:
    pass

import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from security_headers.ratelimit import add_rate_limiting
from security_headers.security import add_security_headers
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app_config import (
    APP_VERSION,
    ASSET_TYPES,
    FAMILY_MAPPING,
    IMPACT_LEVELS,
    LIKELIHOOD_LEVELS,
    MATURITY_LEVELS,
    ROLE_PERMISSIONS,
    USER_ROLES,
    VALIDATION_RULES,
)
from evidence_coverage import FAMILY_CODE
from filestore import get_evidence_bytes, safe_evidence_filename, verify_evidence_hash
from assessment_helpers import validate_evidence_against_rules
from assessment_alerts_api import poam_overdue_alerts
from assessment_nav_api import find_next_incomplete, priority_controls
from assessment_status import apply_assessment_status, build_assessment_status, complete_closeout
from cmmc_scope import apply_scope, merge_scope
from contract_tracking import (
    add_contract,
    contracts_with_status,
    delete_contract,
    list_contracts,
    update_contract,
)
from level1 import (
    apply_l1_status,
    build_l1_entry_text,
    build_l1_status,
    save_l1_assessment,
)
from appendix_pack import get_appendix_pack_zip
from client_workspaces import active_client_id, create_client, delete_client, rename_client
from config import resolve_ssp_template
from controls import CMMC_FRAMEWORK
from demo_flow import demo_status, start_fresh_workspace_state
from demo_loader import load_demo
from ai_config import (
    AI_KEY_CONNECTOR_ID,
    api_key as ai_api_key,
    ai_key_source as ai_key_source_name,
    public_status as ai_public_status,
)
from env_scope import (
    CLOUD_LABELS,
    YES_NO_LABELS,
    control_scope_context,
    env_scope_complete,
    format_env_scope_summary,
    inheritance_hints,
    merge_env_scope,
    scoping_suggestions,
)
from inheritance_map import inheritance_map_rows
from evidence_coverage import compute_readiness_scores, format_evidence_coverage_report
from export_bundle import build_export_package
from guidance import family_prompts, get_control_guidance, objective_coverage, starter_narrative
from official_800_171 import build_control_objectives, get_effective_status
from help_data import FAQ, VIEW_HELP
from inventory_import import import_inventory_csv
from team_roster import (
    assignment_open,
    author_display_name,
    my_work_rows,
    names_match,
    parse_team_roster,
    target_date_overdue,
)
from narrative_prefill import (
    answers_with_export_starters,
    ssp_narrative_stats,
)
from org_assets import add_appendix_file, merge_org_assets, remove_appendix, remove_topology, set_topology_bytes
from org_inventory import INVENTORY_COLUMNS, merge_org_inventory, set_inventory_assets
from poam_export import build_poam_dataframe, export_poam_csv, export_poam_xlsx
from poam_import import import_poam_csv
from pdf_reports import (
    build_executive_report,
    build_poam_pdf,
    build_sprs_pdf,
    build_ssp_summary_pdf,
)
from permissions_api import (
    can_edit_controls,
    can_edit_org,
    can_export,
    can_validate_config,
    can_view_dashboard,
    role_capabilities,
)
from platform_analytics import build_analytics, build_remediation, control_meta
from poam_eligibility import poam_eligibility
from profile_wizard_data import WIZARD_STEPS, FIELD_LABELS, FIELD_PLACEHOLDERS, profile_needs_wizard
from readiness import evaluate_pre_c3pao_readiness
from readiness_review import format_readiness_review_report, run_readiness_review
from report_readiness import evaluate_report_readiness
from scope_ui import apply_scope_from_assets
from annex_weights import annex_weight
from sprs_engine import VARIABLE_WEIGHT_CONTROLS, calculate_detailed_sprs, sprs_weight_label
from sprs_entry import build_sprs_entry_summary
from sprs_one_pager import build_sprs_one_pager
from sprs_preview import format_sprs_delta, preview_sprs_score
from ssp_preview import control_ssp_preview, ssp_progress_detail
from sprs_validation import format_validation_report, run_validation
from ssp import assemble_ssp, assemble_ssp_family
from ssp.constants import FAMILY_ORDER
from user_journey import compute_user_journey
from workspace_io_platform import (
    build_workspace_zip,
    export_oscal_json,
    export_oscal_poam_json,
    load_workspace_zip_bytes,
    reset_controls_only,
    reset_workspace_state,
)
def compute_scope_coverage(ws: dict) -> dict:
    """Scope coverage is part of the collectors edition; empty in the free tier."""
    return {}
from workspace_service import (
    activate_client,
    add_control_comment,
    attach_evidence,
    detach_evidence,
    export_stamp,
    export_stale,
    list_workspace_clients,
    load_workspace,
    patch_control,
    persist_live_asset_snapshot,
    save_workspace,
)
if collectors_available():
    from collectors.credentials_store import (
        credentials_status,
        delete_credentials,
        save_credentials,
    )
    from collectors.engine import recent_runs, run_collector
    from cmmc_collectors.attach import run_and_attach
    from cmmc_collectors.control_requirements import linking_profile_for_control
    from cmmc_collectors.control_readiness import compute_control_readiness
    from cmmc_collectors.auto_linking import auto_link_assets
    from cmmc_collectors.collector_status import collector_status_for_control, collector_health_summary
    from cmmc_collectors.automation_coverage import automation_coverage_for_control
    from cmmc_collectors.evidence_provenance import enrich_evidence_list
    from cmmc_collectors.proof_package import build_proof_package
    from documents_registry import build_documents_list
    from cmmc_collectors.webhook_ingest import ingest_webhook_payload
    from collectors.webhook_store import (
        create_webhook_collector,
        delete_webhook_collector,
        env_webhook_token,
        list_webhook_collectors,
    )
    from cmmc_collectors.freshness import freshness_for_workspace
    from collectors.monitor_store import get_events, get_monitor_states, patch_monitor_schedule, read_scheduler_heartbeat, save_monitor_state
    from collectors.registry import CONNECTOR_CATALOG, list_connectors
    from collectors.routes import router as collectors_router
    from cmmc_collectors.scheduler import monitoring_summary, run_due_connectors
    from collectors.scheduler_config import scheduler_token_matches
    from collectors.dev_scheduler import lifespan_scheduler
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
    run_and_attach = lambda connector_id, **kw: (_MockRun(), [], [])
    linking_profile_for_control = lambda cid: {}
    compute_control_readiness = lambda *a, **k: {}
    auto_link_assets = lambda *a, **k: []
    collector_status_for_control = lambda cid: {}
    collector_health_summary = lambda: {}
    automation_coverage_for_control = lambda cid: {}
    enrich_evidence_list = lambda items: items
    build_proof_package = lambda cid, **kw: {}
    build_documents_list = lambda items: items
    ingest_webhook_payload = lambda *a, **k: {}
    credentials_status = lambda connector_id, fields: {"connector_id": connector_id, "configured": False}
    save_credentials = lambda *a, **k: None
    delete_credentials = lambda *a, **k: None
    get_events = lambda limit=0: []
    get_monitor_states = lambda: []
    patch_monitor_schedule = lambda connector_id, **k: {"connector_id": connector_id}
    read_scheduler_heartbeat = lambda: {}
    save_monitor_state = lambda *a, **k: None
    freshness_for_workspace = lambda ws: {}
    monitoring_summary = lambda: {}
    run_due_connectors = lambda **kw: {"ran_count": 0, "due_count": 0}
    create_webhook_collector = lambda *a, **k: {}
    delete_webhook_collector = lambda *a, **k: None
    env_webhook_token = lambda: ""
    list_webhook_collectors = lambda: []
    scheduler_token_matches = lambda token: False
    lifespan_scheduler = _noop_lifespan
from entra_auth import auth_enabled, get_auth_user, public_auth_config
from auth_middleware import entra_auth_middleware
from sandbox_access import (
    OrgAccessError,
    assert_may_create_org,
    filter_clients_for_user,
    require_org_access,
    require_sandbox_user,
    resolve_workspace_role,
    user_needs_organization,
)
from sandbox_config import sandbox_fixture_only, sandbox_mode
from production_config import allowed_cors_origins, demo_api_enabled
from org_membership import create_org_with_owner
from ccf.routes import router as ccf_router
from remediation.routes import router as remediation_router
from remediation.routes import init_store as init_remediation_store
from policies.routes import router as policy_router
from policies.store import init_store as init_policy_store
from policies.store import add_builtin_templates
from orgs.routes import router as orgs_router
from orgs.store import init_store as init_orgs_store
from raci.routes import router as raci_router
from raci.store import init_store as init_raci_store
from exceptions.routes import router as exception_router
from exceptions.store import init_store as init_exception_store
from vendors.routes import router as vendor_router
from vendors.store import init_store as init_vendor_store
from audit.routes import router as audit_router
from audit.store import init_store as init_audit_store
from risks.store import init_store as init_risks_store, list_risks as list_risk_items
from risks.routes import router as risks_router  # noqa: E402
from testing.routes import router as testing_router
from testing.store import init_store as init_testing_store
from findings.routes import router as findings_router
from findings.store import init_store as init_findings_store
from audit_center.routes import router as audit_center_router
from audit_center.store import init_store as init_audit_center_store
from training.routes import router as training_router
from training.store import init_store as init_training_store
from personnel.routes import router as personnel_router
from compliance_calendar.routes import router as compliance_calendar_router  # noqa: E402
from effectiveness.routes import router as effectiveness_router  # noqa: E402
from control_tests.routes import router as control_tests_router  # noqa: E402
from control_tests.store import init_store as init_control_tests_store  # noqa: E402
from personnel.store import init_store as init_personnel_store
from auth.routes import router as auth_router
from auth.jwt import init_secret as init_auth_secret
from auth.store import (
    init_store as init_auth_store,
    get_user_by_email,
    create_user,
    update_user_password,
)
from notifications.store import init_store as init_notification_store
from entra_auth.config import auth_mode
from assets.routes import router as assets_router
from assets.store import init_store as init_assets_store
from audit_log.store import init_store as init_audit_log_store, list_events, log_event, export_events_csv  # noqa: E402
from compliance_calendar.store import init_store as init_compliance_calendar_store  # noqa: E402
from evidence_hub.routes import router as evidence_hub_router  # noqa: E402
from evidence_hub.store import init_store as init_evidence_hub_store  # noqa: E402
from incidents.routes import router as incidents_router  # noqa: E402
from incidents.store import init_store as init_incidents_store  # noqa: E402


@asynccontextmanager
async def _app_lifespan(_app: FastAPI):

    try:
        from auth.deploy_guard import assert_safe_auth_posture
        assert_safe_auth_posture()
    except RuntimeError as e:
        print(f"[startup] AUTH POSTURE REFUSAL: {e}", file=sys.stderr)
        raise
    for _init_fn, _path in [
        (init_remediation_store, str(CMMC_DATA_DIR)),
        (init_policy_store, str(CMMC_DATA_DIR)),
        (init_orgs_store, str(CMMC_DATA_DIR)),
        (init_raci_store, str(CMMC_DATA_DIR)),
        (init_exception_store, str(CMMC_DATA_DIR)),
        (init_vendor_store, str(CMMC_DATA_DIR)),
        (init_audit_store, str(CMMC_DATA_DIR)),
        (init_risks_store, str(CMMC_DATA_DIR)),
        (init_control_tests_store, str(CMMC_DATA_DIR)),
        (init_testing_store, str(CMMC_DATA_DIR)),
        (init_findings_store, str(CMMC_DATA_DIR)),
        (init_audit_center_store, str(CMMC_DATA_DIR)),
        (init_assets_store, str(CMMC_DATA_DIR)),
        (init_evidence_hub_store, str(CMMC_DATA_DIR)),
        (init_incidents_store, str(CMMC_DATA_DIR)),
        (init_training_store, str(CMMC_DATA_DIR)),
        (init_personnel_store, str(CMMC_DATA_DIR)),
        (init_audit_log_store, str(CMMC_DATA_DIR)),
        (init_notification_store, str(CMMC_DATA_DIR)),
        (init_auth_secret, str(CMMC_DATA_DIR)),
        (init_compliance_calendar_store, str(CMMC_DATA_DIR)),
    ]:
        try:
            _init_fn(_path)
        except Exception as e:
            print(f"[lifespan] {_init_fn.__name__} failed: {e}", file=sys.stderr)
    try:
        add_builtin_templates()
    except Exception as e:
        print(f"[lifespan] add_builtin_templates failed: {e}", file=sys.stderr)
    if auth_mode() == "local":
        try:
            init_auth_store(str(CMMC_DATA_DIR))
        except Exception as e:
            print(f"[lifespan] init_auth_store failed: {e}", file=sys.stderr)

    # ── auto-load demo once; keep assessor password in sync with env ──
    auto_demo = os.environ.get("CMMC_AUTO_LOAD_DEMO", "").strip()
    if auto_demo:
        flag = Path(CMMC_DATA_DIR) / ".auto-demo-loaded"
        if not flag.exists():
            try:
                cid = create_client("Khestra Demo")
                load_demo(demo_id=auto_demo, client_id=cid)
                flag.write_text("done")
            except Exception as e:
                print(f"[startup] auto-demo failed: {e}")

    if auth_mode() == "local":
        try:
            admin = get_user_by_email("admin@example.com")
            pw = os.environ.get("CMMC_ASSESSOR_PASSWORD", "").strip()
            if admin and pw:
                from auth.password import verify_password

                sarah = get_user_by_email("sarah@localhost")
                if not sarah:
                    create_user(
                        email="sarah@localhost",
                        name="Sarah",
                        password=pw,
                        role="Assessor",
                        org_id=admin["org_id"],
                    )
                    print("[startup] created assessor sarah@localhost")
                else:
                    current_hash = sarah.get("password_hash", "")
                    if current_hash and not verify_password(pw, current_hash):
                        update_user_password(sarah["id"], pw)
                        print("[startup] synced assessor password from CMMC_ASSESSOR_PASSWORD")
        except Exception as e:
            print(f"[startup] assessor seed failed: {e}")

    try:
        from compliance_calendar.sweep import run_reminder_sweep
        outcome = run_reminder_sweep(window_days=7)
        if outcome.get("created"):
            print(f"[startup] compliance reminders: {outcome['created']} new", file=sys.stderr)
    except Exception as e:
        print(f"[startup] compliance reminder sweep failed: {e}", file=sys.stderr)

    async with lifespan_scheduler():
        yield


app = FastAPI(title="CMMC Platform API", version="0.1.0", lifespan=_app_lifespan, docs_url=None, redoc_url=None, openapi_url=None)


class StripFrameworkPrefixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/api/cmmc/"):
                scope["path"] = path.replace("/api/cmmc/", "/api/", 1)
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
    "/api/org-assets/",
    "/api/inventory",
    "/api/asset-scope",
    "/api/env-scope",
    "/api/system-scope",
    "/api/webhooks",
    "/api/webhook/",
    "/api/collectors/",
    "/api/demo/",
    "/api/audit-log",
    "/api/narratives/",
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
            framework_id="CMMC",
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


@app.exception_handler(OrgAccessError)
async def org_access_error_handler(_request: Request, exc: OrgAccessError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


class ControlPatch(BaseModel):
    status: Optional[str] = None
    implementation_narrative: Optional[str] = None
    assessor_notes: Optional[str] = None
    examine: Optional[str] = None
    interview: Optional[str] = None
    test: Optional[str] = None
    owner: Optional[str] = None
    target_date: Optional[str] = None
    remediation_plan: Optional[str] = None
    estimated_cost: Optional[str] = None
    likelihood: Optional[str] = None
    impact: Optional[str] = None
    maturity: Optional[str] = None
    linked_policies: Optional[list] = None
    linked_assets: Optional[list] = None
    linked_team: Optional[list] = None
    linked_subcontractors: Optional[list] = None
    objectives: Optional[list] = None
    override_active: Optional[bool] = None
    override_justification: Optional[str] = None
    fips_certificate_number: Optional[str] = None
    cloud_authorization_status: Optional[str] = None
    dfars_72hr_reporting_enabled: Optional[bool] = None
    # True: narrative was generated (or applied) from an AI draft. Absent/False
    # on narrative edits clears the AI provenance marker.
    ai_generated: Optional[bool] = None


class GenerateNarrativeBody(BaseModel):
    use_ai: bool = False
    force: bool = False
    # Default False: draft from evidence/objectives/etc., not the text being replaced.
    include_current_narrative: bool = False


class GenerateAllNarrativesBody(BaseModel):
    scope: str = "missing_met"
    use_ai: bool = False
    force: bool = False


class OrgProfilePatch(BaseModel):
    org_profile: Dict[str, str] = Field(default_factory=dict)


class InventoryPatch(BaseModel):
    assets: List[Dict[str, str]] = Field(default_factory=list)


class AssetScopePatch(BaseModel):
    asset_scope: Dict[str, int] = Field(default_factory=dict)


class EnvScopePatch(BaseModel):
    env_scope: Dict[str, str] = Field(default_factory=dict)


class SystemScopePatch(BaseModel):
    external_connections: str = Field(default="")
    cui_types: str = Field(default="")
    last_review: str = Field(default="")


class RolePatch(BaseModel):
    role: str


class UserNamePatch(BaseModel):
    name: str


class ControlCommentBody(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)


class CreateClientBody(BaseModel):
    display_name: str


class OrganizationCreateBody(BaseModel):
    name: str
    load_demo: bool = True
    demo_id: str = "trident"


class RenameClientBody(BaseModel):
    name: str = Field(..., min_length=1)


class MspModePatch(BaseModel):
    msp_mode: bool = False


STATUS_OPTIONS = [
    "NOT STARTED",
    "IN PROGRESS",
    "PARTIALLY MET",
    "PLANNED",
    "MET",
    "NOT MET",
    "NOT APPLICABLE",
    "INHERITED",
]


def _safe_filename(label: str) -> str:
    return re.sub(r"[^\w\-]+", "_", label.strip())[:40] or "Organization"


def _weight_tier(control_id: str) -> str:
    if control_id in VARIABLE_WEIGHT_CONTROLS:
        return "variable"
    w = annex_weight(control_id)
    if w >= 5:
        return "critical"
    if w == 3:
        return "standard"
    return "low"


def _weight_badge_label(control_id: str) -> str:
    if control_id in VARIABLE_WEIGHT_CONTROLS:
        return "5/3 PT"
    return f"{annex_weight(control_id)} PT"


def _control_summary(cid: str, ans: Dict[str, Any]) -> Dict[str, Any]:
    info = CMMC_FRAMEWORK[cid]
    auto = collector_status_for_control(cid)
    return {
        "id": cid,
        "family": info["family"],
        "name": info["name"],
        "weight": info["weight"],
        "weight_tier": _weight_tier(cid),
        "weight_badge": _weight_badge_label(cid),
        "weight_hint": sprs_weight_label(cid),
        "status": ans.get("status", "NOT STARTED"),
        "has_narrative": bool((ans.get("implementation_narrative") or "").strip()),
        "evidence_count": len(ans.get("evidence") or []),
        "owner": ans.get("owner", ""),
        "target_date": ans.get("target_date", ""),
        "overdue": target_date_overdue(ans.get("target_date", ""), ans.get("status", "NOT STARTED")),
        "comment_count": len(ans.get("comments") or []),
        "collector_status": auto["status"] if auto else None,
    }


def _ws_role(ws: Dict[str, Any], client_id: Optional[str] = None) -> str:
    cid = client_id or ws.get("client_id") or active_client_id()
    return resolve_workspace_role(ws, cid)


def _current_user_name(ws: Dict[str, Any]) -> str:
    user = get_auth_user()
    if user:
        return user.name or user.email
    return ws.get("current_user_name", "")


def _audit_log(
    ws: Dict[str, Any],
    action: str,
    resource_type: str,
    resource_id: str = "",
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
    outcome: str = "success",
) -> None:
    try:
        user = get_auth_user()
        user_id = user.oid if user else ""
        user_email = user.email if user else _current_user_name(ws)
        ip = request.client.host if request and request.client else ""
        ua = request.headers.get("user-agent", "") if request else ""
        log_event(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            framework_id="CMMC",
            user_id=user_id,
            user_email=user_email,
            ip_address=ip,
            user_agent=ua,
            details=details,
            outcome=outcome,
        )
    except Exception:
        pass


def _require_edit_controls(ws: Dict[str, Any]) -> None:
    if not can_edit_controls(_ws_role(ws, ws.get("client_id"))):
        raise HTTPException(403, "This role cannot edit controls")


def _require_edit_org(ws: Dict[str, Any]) -> None:
    if not can_edit_org(_ws_role(ws, ws.get("client_id"))):
        raise HTTPException(403, "This role cannot edit organization data")


def _require_export(ws: Dict[str, Any]) -> None:
    if not can_export(_ws_role(ws, ws.get("client_id"))):
        raise HTTPException(403, "This role cannot export data")


def _require_validate_config(ws: Dict[str, Any]) -> None:
    if not can_validate_config(_ws_role(ws, ws.get("client_id"))):
        raise HTTPException(403, "This role cannot run config validation")


def _require_view_dashboard(ws: Dict[str, Any]) -> None:
    if not can_view_dashboard(_ws_role(ws, ws.get("client_id"))):
        raise HTTPException(403, "This role cannot view dashboard analytics")


def _resolve_evidence_file(
    ws: Dict[str, Any], control_id: str, filename: str
) -> tuple[Dict[str, Any], bytes]:
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    safe = safe_evidence_filename(filename)
    for ev in ws["answers"].get(control_id, {}).get("evidence") or []:
        if ev.get("filename") == safe:
            data = get_evidence_bytes(control_id, ev, ws.get("restored_evidence"))
            if data is not None:
                return ev, data
    raise HTTPException(404, "Evidence file not found")


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", **ai_public_status(), "auth_enabled": auth_enabled()}


@app.get("/api/auth/config")
def get_auth_config() -> Dict[str, Any]:
    return public_auth_config()


@app.get("/api/clients")
def get_clients() -> List[Dict[str, str]]:
    return filter_clients_for_user(list_workspace_clients())


@app.post("/api/clients/{client_id}/activate")
def post_activate_client(client_id: str) -> Dict[str, str]:
    if sandbox_mode():
        require_org_access(client_id)
    activate_client(client_id)
    ws = load_workspace(client_id) if client_id != active_client_id() else load_workspace(active_client_id())
    _require_edit_org(ws)
    return {"active_client_id": client_id}


@app.post("/api/organizations")
def post_create_organization(body: OrganizationCreateBody) -> Dict[str, Any]:
    if not sandbox_mode():
        raise HTTPException(400, "Organization signup is only enabled in sandbox mode")
    user = require_sandbox_user()
    assert_may_create_org(user)
    name = (body.name or "").strip()
    if not name:
        raise HTTPException(400, "Organization name is required")
    cid = create_client(name)
    create_org_with_owner(
        client_id=cid,
        display_name=name,
        user_oid=user.oid,
        user_email=user.email,
        user_name=user.name,
    )
    activate_client(cid)
    if body.load_demo:
        try:
            load_demo(body.demo_id, cid)
        except KeyError as exc:
            raise HTTPException(400, f"Unknown demo: {body.demo_id}") from exc
    return {"client_id": cid, "name": name, "active_client_id": cid}


@app.post("/api/demo/load")
def post_load_demo(
    demo_id: str = Query("trident"),
    client_id: Optional[str] = Query(None),
    org_name: Optional[str] = Query(None),
) -> Dict[str, Any]:
    if not demo_api_enabled():
        raise HTTPException(403, "Demo workspaces are disabled in this environment")
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    try:
        ws = load_demo(demo_id, client_id, org_name=org_name)
    except KeyError as exc:
        raise HTTPException(400, f"Unknown demo: {demo_id}") from exc
    sprs = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])
    return {
        "client_id": ws["client_id"],
        "org_name": ws.get("org_name", ""),
        "demo_id": demo_id,
        "sprs_score": sprs["final_score"],
        **demo_status(ws["org_profile"]),
    }


@app.get("/api/demo/status")
def get_demo_status(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return demo_status(ws["org_profile"])


@app.post("/api/demo/clear")
def clear_demo(client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    if not demo_api_enabled():
        raise HTTPException(403, "Demo workspaces are disabled in this environment")
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    save_workspace(start_fresh_workspace_state(ws, ASSET_TYPES))
    return {"status": "cleared"}


@app.get("/api/dashboard")
def get_dashboard(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    scoped = ws["scoped_controls"]
    answers = ws["answers"]
    org_profile = ws["org_profile"]
    sprs = calculate_detailed_sprs(answers, scoped)
    readiness = evaluate_report_readiness(answers, org_profile, scoped)

    assessed = sum(
        1
        for cid in scoped
        if answers.get(cid, {}).get("status", "NOT STARTED") != "NOT STARTED"
    )

    return {
        "client_id": ws["client_id"],
        "org_name": org_profile.get("org_name") or ws.get("org_name") or "Organization",
        "sprs_score": sprs["final_score"],
        "sprs_max": 110,
        "open_gaps": readiness["open_gap_count"],
        "export_readiness_pct": readiness["score"],
        "controls_assessed": assessed,
        "controls_total": len(scoped),
        "last_export_at": ws.get("last_export_at"),
        "export_stale": export_stale(ws),
        "blockers": readiness.get("blockers") or [],
        "cmmc_status": build_assessment_status(ws),
    }


@app.get("/api/readiness/export-report")
def get_export_readiness_report(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    answers = ws["answers"]
    org_profile = ws["org_profile"]
    scoped = ws["scoped_controls"]
    report = evaluate_report_readiness(answers, org_profile, scoped)
    sprs = calculate_detailed_sprs(answers, scoped)
    missing_controls = []
    for cid in report.get("missing_narrative_sample") or []:
        if cid not in CMMC_FRAMEWORK:
            continue
        missing_controls.append(
            {
                "id": cid,
                "status": answers.get(cid, {}).get("status", "NOT STARTED"),
                "name": CMMC_FRAMEWORK[cid]["name"][:72],
            }
        )
    warning_items = []
    for item in report.get("warnings") or []:
        if " — " in item:
            title, detail = item.split(" — ", 1)
            warning_items.append({"title": title, "detail": detail})
        else:
            warning_items.append({"title": item, "detail": ""})
    narrative_stats = ssp_narrative_stats(answers, scoped)
    return {
        **report,
        "sprs_score": sprs["final_score"],
        "missing_narrative_controls": missing_controls,
        "warning_items": warning_items,
        "ssp_narratives": narrative_stats,
    }


@app.get("/api/readiness/sprs-entry-text")
def get_sprs_entry_text(client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    ws = load_workspace(client_id)
    sprs = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])
    text = build_sprs_entry_summary(
        ws["org_profile"], sprs, ws["scoped_controls"], ws.get("asset_scope", {}),
        cmmc_assessment=ws.get("cmmc_assessment"),
        cmmc_scope=ws.get("cmmc_scope"),
    )
    return {"text": text}


def _family_filter_options(scoped_controls: List[str]) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    for cid in scoped_controls:
        if cid not in CMMC_FRAMEWORK:
            continue
        fam = CMMC_FRAMEWORK[cid]["family"]
        counts[fam] = counts.get(fam, 0) + 1
    options: List[Dict[str, Any]] = []
    for _label, fam in sorted(FAMILY_MAPPING.items()):
        n = counts.get(fam, 0)
        if n:
            code = FAMILY_CODE.get(fam, fam[:2].upper())
            options.append({
                "code": code,
                "family": fam,
                "count": n,
                "label": f"{fam} ({n})",
            })
    return options


@app.get("/api/controls")
def get_controls(
    client_id: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    scoped = ws["scoped_controls"]
    answers = ws["answers"]
    user_name = (_current_user_name(ws) or "").strip()
    items = []
    for cid in scoped:
        if cid not in CMMC_FRAMEWORK:
            continue
        ans = answers.get(cid, {})
        if assigned_to == "me":
            owner = (ans.get("owner") or "").strip()
            if not user_name or not names_match(owner, user_name):
                continue
            if not assignment_open(ans):
                continue
        row = _control_summary(cid, ans)
        if family and row["family"] != family:
            continue
        if q:
            needle = q.lower()
            ans = answers.get(cid, {})
            haystack = f"{cid} {row['name']} {ans.get('assessor_notes', '')}".lower()
            if needle not in haystack:
                continue
        items.append(row)
    families = sorted({CMMC_FRAMEWORK[c]["family"] for c in scoped if c in CMMC_FRAMEWORK})
    return {
        "controls": items,
        "families": families,
        "family_options": _family_filter_options(scoped),
        "status_options": STATUS_OPTIONS,
    }


@app.get("/api/ssp/progress")
def get_ssp_progress(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return ssp_progress_detail(ws["answers"], ws["scoped_controls"])


@app.get("/api/controls/{control_id}/ssp-preview")
def get_control_ssp_preview(control_id: str, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    ans = ws["answers"].get(control_id, {})
    return control_ssp_preview(control_id, ans)


@app.get("/api/controls/{control_id}")
def get_control(control_id: str, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    ans = ws["answers"].get(control_id, {})
    info = CMMC_FRAMEWORK[control_id]
    workspace_evidence = [
        {
            "filename": e.get("filename"),
            "upload_date": e.get("upload_date"),
            "sha256": e.get("sha256"),
            "is_hub_evidence": False,
            "evidence_type": e.get("evidence_type", "other"),
            "display_title": e.get("display_title", e.get("filename", "")),
            "evidence_version": e.get("evidence_version", ""),
            "auto_status": e.get("auto_status", ""),
            "review_status": e.get("review_status", ""),
            "provenance": e.get("provenance") or {},
        }
        for e in (ans.get("evidence") or [])
    ]
    try:
        from evidence_hub.store import collector_period_summary, list_evidence
        hub_evidence = [
            {
                "filename": e.get("filename", ""),
                "upload_date": e.get("uploaded_at", ""),
                "sha256": e.get("sha256", ""),
                "is_hub_evidence": True,
                "hub_id": e.get("id", ""),
                "evidence_type": e.get("evidence_type", "other"),
                "display_title": e.get("display_title", e.get("filename", "")),
                "evidence_version": e.get("evidence_version", ""),
                "auto_status": e.get("auto_status", ""),
                "auto_summary": e.get("auto_summary", ""),
                "review_status": e.get("review_status", ""),
                "tags": e.get("tags") or [],
                "name": e.get("name", ""),
                "description": e.get("description", ""),
                "uploaded_by": e.get("uploaded_by", ""),
                "valid_until": e.get("valid_until", ""),
                "period_covered": e.get("period_covered") or e.get("evidence_version") or "",
            }
            for e in list_evidence(framework_id="CMMC", control_id=control_id, view="latest")
        ]
        evidence_history_summary = collector_period_summary("CMMC", control_id)
    except Exception:
        hub_evidence = []
        evidence_history_summary = []

    # ── Auto-link assets from inventory on first load ────
    auto_matched = auto_link_assets(
        control_id,
        ans,
        linking_profile_for_control(control_id),
        ws.get("org_inventory"),
    )
    if auto_matched:
        ans["linked_assets"] = auto_matched
        ans["_auto_linked"] = True
        ws["answers"][control_id] = ans
        save_workspace(ws)

    hub_sha256s = {e["sha256"] for e in hub_evidence if e.get("sha256")}
    evidence = enrich_evidence_list(
        [e for e in workspace_evidence if e.get("sha256") not in hub_sha256s] + hub_evidence
    )

    profile = linking_profile_for_control(control_id)
    coverage = automation_coverage_for_control(control_id, ans=ans, linking_profile=profile)

    objectives = build_control_objectives(control_id, ans)
    # Advisory only — does not rewrite stored status when objectives are incomplete
    computed = get_effective_status({**ans, "objectives": objectives})

    return {
        "id": control_id,
        "family": info["family"],
        "name": info["name"],
        "weight": info["weight"],
        "description": info.get("description", ""),
        "status": ans.get("status", "NOT STARTED"),
        "implementation_narrative": ans.get("implementation_narrative", ""),
        "ai_generated": bool(ans.get("ai_generated")),
        "ai_generated_at": ans.get("ai_generated_at") or None,
        "ai_draft": ans.get("ai_draft") or None,
        "ai_draft_created_at": ans.get("ai_draft_created_at") or None,
        "ai_draft_method": ans.get("ai_draft_method") or None,
        "assessor_notes": ans.get("assessor_notes", ""),
        "examine": ans.get("examine", ""),
        "interview": ans.get("interview", ""),
        "test": ans.get("test", ""),
        "owner": ans.get("owner", ""),
        "target_date": ans.get("target_date", ""),
        "remediation_plan": ans.get("remediation_plan", ""),
        "estimated_cost": str(ans.get("estimated_cost", "")),
        "likelihood": ans.get("likelihood", "Medium"),
        "impact": ans.get("impact", "Medium"),
        "maturity": ans.get("maturity", "Ad Hoc"),
        "evidence": evidence,
        "evidence_history_summary": evidence_history_summary,
        "status_options": STATUS_OPTIONS,
        "maturity_options": MATURITY_LEVELS,
        "likelihood_options": LIKELIHOOD_LEVELS,
        "impact_options": IMPACT_LEVELS,
        "comments": list(ans.get("comments") or []),
        "linked_policies": ans.get("linked_policies", []),
        "linked_assets": ans.get("linked_assets", []),
        "linked_team": ans.get("linked_team", []),
        "linked_subcontractors": ans.get("linked_subcontractors", []),
        "team_members": parse_team_roster(ws.get("org_profile") or {}),
        "scope_context": control_scope_context(
            control_id,
            merge_env_scope(ws.get("env_scope")),
            ws["answers"],
            ws["scoped_controls"],
        ),
        "linking_profile": profile,
        "readiness": compute_control_readiness(
            control_id,
            ans,
            linking_profile=profile,
        ),
        "auto_badge": collector_status_for_control(control_id),
        "automation_coverage": coverage,
        "objectives": objectives,
        "computed_status": computed,
        "override_active": bool(ans.get("override_active")),
        "override_justification": ans.get("override_justification") or "",
        "fips_certificate_number": ans.get("fips_certificate_number") or "",
        "cloud_authorization_status": ans.get("cloud_authorization_status") or "",
        "dfars_72hr_reporting_enabled": bool(ans.get("dfars_72hr_reporting_enabled")),
    }


@app.get("/api/controls/{control_id}/proof-package")
def get_control_proof_package(control_id: str, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Auditor-facing proof package for one control (JSON)."""
    # Reuse get_control assembly for evidence + provenance
    detail = get_control(control_id, client_id=client_id)
    ws = load_workspace(client_id)
    ans = ws["answers"].get(control_id, {})
    return build_proof_package(
        control_id,
        ans,
        list(detail.get("evidence") or []),
        info=CMMC_FRAMEWORK[control_id],
    )


@app.get("/api/controls/{control_id}/evidence-history")
def get_control_evidence_history(
    control_id: str,
    filename: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Period-covered collector history for a control (one row per collection day)."""
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    try:
        from evidence_hub.store import collector_period_summary, list_evidence

        summary = collector_period_summary("CMMC", control_id)
        if filename:
            summary = [s for s in summary if s.get("filename") == filename]
        periods = list_evidence(framework_id="CMMC", control_id=control_id, view="by_period")
        if filename:
            periods = [e for e in periods if e.get("filename") == filename]
        return {
            "control_id": control_id,
            "summary": summary,
            "periods": periods,
            "retention_note": "One artifact retained per collection day; older periods soft-archived after the retention window.",
        }
    except Exception as exc:
        raise HTTPException(500, f"Failed to load evidence history: {exc}") from exc


@app.get("/api/controls/{control_id}/sprs-preview")
def get_sprs_preview(
    control_id: str,
    status: str = Query(...),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    current = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])["final_score"]
    projected = preview_sprs_score(ws["answers"], ws["scoped_controls"], control_id, status)
    return {
        "current_score": current,
        "projected_score": projected,
        "delta": format_sprs_delta(current, projected),
    }


@app.patch("/api/controls/{control_id}")
def update_control(
    control_id: str,
    body: ControlPatch,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_controls(ws)
    old_ans = ws["answers"].get(control_id, {})
    old_diffs = {
        "status": old_ans.get("status"),
        "implementation_narrative": old_ans.get("implementation_narrative"),
        "linked_policies": old_ans.get("linked_policies"),
    }
    try:
        patch_control(
            ws,
            control_id,
            status=body.status,
            implementation_narrative=body.implementation_narrative,
            assessor_notes=body.assessor_notes,
            examine=body.examine,
            interview=body.interview,
            test=body.test,
            owner=body.owner,
            target_date=body.target_date,
            remediation_plan=body.remediation_plan,
            estimated_cost=body.estimated_cost,
            likelihood=body.likelihood,
            impact=body.impact,
            maturity=body.maturity,
            linked_policies=body.linked_policies,
            linked_assets=body.linked_assets,
            linked_team=body.linked_team,
            linked_subcontractors=body.linked_subcontractors,
            objectives=body.objectives,
            override_active=body.override_active,
            override_justification=body.override_justification,
            fips_certificate_number=body.fips_certificate_number,
            cloud_authorization_status=body.cloud_authorization_status,
            dfars_72hr_reporting_enabled=body.dfars_72hr_reporting_enabled,
            human_edited=True,
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    if body.implementation_narrative is not None:
        marker_state = load_workspace(client_id)
        m_ans = marker_state["answers"].setdefault(control_id, {})
        if body.ai_generated is True:
            m_ans["ai_generated"] = True
            m_ans["ai_generated_at"] = datetime.utcnow().isoformat()
        else:
            m_ans.pop("ai_generated", None)
            m_ans.pop("ai_generated_at", None)
        save_workspace(marker_state)
    changed = {k: v for k, v in body.dict(exclude_unset=True).items() if v is not None}
    new_vals = body.dict(exclude_unset=True)
    field_diffs = {}
    for field in ("status", "implementation_narrative", "linked_policies"):
        if field in changed:
            old_v = old_diffs[field]
            new_v = new_vals.get(field)
            if old_v != new_v:
                field_diffs[field] = {"old": old_v, "new": new_v}
    details = {"fields": list(changed.keys())}
    if field_diffs:
        details["field_diffs"] = field_diffs
    _audit_log(ws, "updated", "control", control_id, details)
    ws = load_workspace(client_id)
    sprs = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])
    return {
        "control": _control_summary(control_id, ws["answers"].get(control_id, {})),
        "sprs_score": sprs["final_score"],
        "export_stale": export_stale(ws),
    }


@app.get("/api/controls/my-work")
def get_my_work(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    org_profile = ws.get("org_profile") or {}
    user_name = (_current_user_name(ws) or "").strip()
    rows = my_work_rows(ws["answers"], ws["scoped_controls"], user_name)
    overdue = sum(1 for r in rows if r.get("overdue"))
    return {
        "current_user_name": user_name,
        "team_members": parse_team_roster(org_profile),
        "assigned_count": len(rows),
        "overdue_count": overdue,
        "controls": rows,
        "needs_user_name": not bool(user_name),
    }


@app.post("/api/controls/{control_id}/comments")
def post_control_comment(
    control_id: str,
    body: ControlCommentBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_controls(ws)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    author = author_display_name(_current_user_name(ws), _ws_role(ws))
    try:
        add_control_comment(ws, control_id, body.text, author)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    _audit_log(ws, "created", "comment", control_id, {"text": body.text[:100]})
    ws = load_workspace(client_id)
    return {"comments": ws["answers"].get(control_id, {}).get("comments") or []}


@app.get("/api/org-profile")
def get_org_profile(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {"org_profile": ws["org_profile"], "org_name": ws.get("org_name", "")}


@app.patch("/api/org-profile")
def update_org_profile(body: OrgProfilePatch, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    ws["org_profile"] = {**ws.get("org_profile", {}), **body.org_profile}
    ws["org_name"] = ws["org_profile"].get("org_name") or ws.get("org_name", "")
    save_workspace(ws)
    _audit_log(ws, "updated", "organization", "", {"fields": list(body.org_profile.keys())})
    return {"org_profile": ws["org_profile"]}


@app.get("/api/controls/{control_id}/guidance")
def get_control_guidance_route(
    control_id: str,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    return get_control_guidance(
        control_id,
        org_profile=ws.get("org_profile") or {},
        env_scope=merge_env_scope(ws.get("env_scope")),
        scoped_controls=ws.get("scoped_controls") or [],
    )


@app.post("/api/controls/{control_id}/generate-narrative")
def generate_narrative_route(
    control_id: str,
    body: GenerateNarrativeBody,
    client_id: Optional[str] = Query(None),
    request: Request = None,
) -> Dict[str, Any]:
    from narrative_generator import generate_narrative

    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    hub_files: List[Dict[str, Any]] = []
    try:
        from evidence_hub.store import list_evidence
        hub_files = list_evidence(framework_id="CMMC", control_id=control_id) or []
    except Exception:
        pass
    result = generate_narrative(
        control_id,
        ws["answers"],
        ws.get("org_profile") or {},
        merge_env_scope(ws.get("env_scope")),
        ws.get("scoped_controls") or [],
        ws.get("restored_evidence"),
        additional_evidence=hub_files,
        use_ai=body.use_ai,
        force=body.force,
        include_current_narrative=body.include_current_narrative,
    )
    _audit_log(
        ws,
        "generated",
        "narrative",
        control_id,
        {
            "use_ai": bool(body.use_ai),
            "force": bool(body.force),
            "method": result.get("method", ""),
            "ai_available": result.get("ai_available", False),
            "ai_error": result.get("ai_error"),
            "sources": (result.get("sources") or [])[:10],
            "evidence_items": len(hub_files),
        },
        request=request,
    )
    if result.get("method") == "ai" and result.get("narrative"):
        ans = ws["answers"].setdefault(control_id, {})
        now = datetime.utcnow().isoformat()
        ans["ai_draft"] = result["narrative"]
        ans["ai_draft_created_at"] = now
        ans["ai_draft_method"] = "ai"
        save_workspace(ws)
        result["draft_created"] = True
    return result


@app.post("/api/controls/{control_id}/ai-draft/approve")
def approve_ai_draft_route(
    control_id: str,
    client_id: Optional[str] = Query(None),
    request: Request = None,
) -> Dict[str, Any]:
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    ans = ws["answers"].setdefault(control_id, {})
    draft = ans.get("ai_draft")
    if not draft:
        raise HTTPException(400, "No AI draft to approve")
    ans["implementation_narrative"] = draft
    ans["ai_generated"] = True
    ans["ai_generated_at"] = datetime.utcnow().isoformat()
    ans.pop("ai_draft", None)
    ans.pop("ai_draft_created_at", None)
    ans.pop("ai_draft_method", None)
    save_workspace(ws)
    _audit_log(ws, "approved", "ai_draft", control_id, {"promoted_to": "implementation_narrative"}, request=request)
    return {"status": "approved", "ai_generated": True}


@app.post("/api/controls/{control_id}/ai-draft/reject")
def reject_ai_draft_route(
    control_id: str,
    client_id: Optional[str] = Query(None),
    request: Request = None,
) -> Dict[str, Any]:
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    ws = load_workspace(client_id)
    ans = ws["answers"].setdefault(control_id, {})
    ans.pop("ai_draft", None)
    ans.pop("ai_draft_created_at", None)
    ans.pop("ai_draft_method", None)
    save_workspace(ws)
    _audit_log(ws, "rejected", "ai_draft", control_id, {"draft": "discarded"}, request=request)
    return {"status": "rejected"}


@app.post("/api/narratives/generate-all")
def generate_all_narratives_route(
    body: GenerateAllNarrativesBody,
    client_id: Optional[str] = Query(None),
    request: Request = None,
) -> Dict[str, Any]:
    from narrative_generator import generate_all_narratives

    if body.scope not in ("missing_met", "all_empty", "all"):
        raise HTTPException(400, "scope must be missing_met, all_empty, or all")
    ws = load_workspace(client_id)
    _require_edit_controls(ws)
    result = generate_all_narratives(ws, scope=body.scope, use_ai=body.use_ai, force=body.force)  # type: ignore[arg-type]
    _audit_log(
        ws,
        "generated",
        "narratives_bulk",
        "",
        {
            "scope": body.scope,
            "use_ai": bool(body.use_ai),
            "candidate_count": result.get("candidate_count", 0),
            "generated": result.get("generated", 0),
            "skipped": result.get("skipped", 0),
        },
        request=request,
    )
    return result


class EvidenceSummaryApplyBody(BaseModel):
    mode: str = "append"  # append | replace


@app.get("/api/controls/{control_id}/evidence-summary")
def get_control_evidence_summary(
    control_id: str,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    from cmmc_collectors.evidence_summarize import summarize_control_collector_evidence

    ws = load_workspace(client_id)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    return summarize_control_collector_evidence(
        control_id, ws["answers"], ws.get("restored_evidence")
    )


@app.post("/api/controls/{control_id}/apply-evidence-summary")
def apply_control_evidence_summary(
    control_id: str,
    body: EvidenceSummaryApplyBody,
    client_id: Optional[str] = Query(None),
    request: Request = None,
) -> Dict[str, Any]:
    from cmmc_collectors.evidence_summarize import apply_evidence_summary_to_control

    ws = load_workspace(client_id)
    _require_edit_controls(ws)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    if body.mode not in ("append", "replace"):
        raise HTTPException(400, "mode must be append or replace")
    try:
        _ws, result = apply_evidence_summary_to_control(ws, control_id, mode=body.mode)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    _audit_log(
        ws,
        "applied",
        "evidence_summary",
        control_id,
        {"mode": body.mode, "collector_count": result.get("collector_count", 0)},
        request=request,
    )
    return {
        "examine": result["examine"],
        "test": result["test"],
        "mode": body.mode,
        "collector_count": result["collector_count"],
    }


@app.get("/api/controls/{control_id}/remediation-summary")
def get_control_remediation_summary(
    control_id: str,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    from cmmc_collectors.remediation_summarize import summarize_collector_remediation_gaps

    ws = load_workspace(client_id)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    return summarize_collector_remediation_gaps(
        control_id, ws["answers"], ws.get("restored_evidence")
    )


@app.post("/api/controls/{control_id}/apply-remediation-summary")
def apply_control_remediation_summary(
    control_id: str,
    body: EvidenceSummaryApplyBody,
    client_id: Optional[str] = Query(None),
    request: Request = None,
) -> Dict[str, Any]:
    from cmmc_collectors.remediation_summarize import apply_remediation_summary_to_control

    ws = load_workspace(client_id)
    _require_edit_controls(ws)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    if body.mode not in ("append", "replace"):
        raise HTTPException(400, "mode must be append or replace")
    try:
        _ws, result = apply_remediation_summary_to_control(ws, control_id, mode=body.mode)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    _audit_log(
        ws,
        "applied",
        "remediation_summary",
        control_id,
        {"mode": body.mode, "collector_count": result.get("collector_count", 0)},
        request=request,
    )
    return {
        "remediation_plan": result["remediation_plan"],
        "mode": body.mode,
        "gap_count": result["gap_count"],
        "collector_count": result["collector_count"],
    }


@app.post("/api/controls/{control_id}/evidence")
async def upload_evidence(
    control_id: str,
    files: List[UploadFile] = File(...),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_controls(ws)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    if not files:
        raise HTTPException(400, "No files uploaded")
    uploaded: List[Dict[str, str]] = []
    for file in files:
        data = await file.read()
        if len(data) > 10 * 1024 * 1024:
            raise HTTPException(413, f"File exceeds 10 MB limit: {file.filename}")
        sha = hashlib.sha256(data).hexdigest()
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws = attach_evidence(
            ws,
            control_id,
            filename=file.filename or "evidence.bin",
            data=data,
            sha256=sha,
            upload_date=stamp,
        )
        uploaded.append({"filename": safe_evidence_filename(file.filename or "evidence.bin"), "sha256": sha})
    fnames = [u["filename"] for u in uploaded]
    _audit_log(ws, "created", "evidence", control_id, {"filenames": fnames})
    return {"uploaded": uploaded, "count": len(uploaded)}


@app.delete("/api/controls/{control_id}/evidence/{filename}")
def delete_evidence(
    control_id: str,
    filename: str,
    client_id: Optional[str] = Query(None),
) -> Dict[str, str]:
    ws = load_workspace(client_id)
    _require_edit_controls(ws)
    try:
        detach_evidence(ws, control_id, filename=filename)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    _audit_log(ws, "deleted", "evidence", control_id, {"filename": safe_evidence_filename(filename)})
    return {"status": "deleted", "filename": safe_evidence_filename(filename)}


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


@app.get("/api/controls/{control_id}/evidence/{filename}/verify")
def verify_evidence_file(
    control_id: str,
    filename: str,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    ev, data = _resolve_evidence_file(ws, control_id, filename)
    expected = (ev.get("sha256") or "").strip().lower()
    ok = verify_evidence_hash(ev, data) if expected else False
    return {
        "verified": ok,
        "expected_sha256": expected,
        "filename": ev.get("filename", filename),
    }


@app.get("/api/organization")
def get_organization(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    org_profile = ws["org_profile"]
    env_scope = merge_env_scope(ws.get("env_scope"))
    scoped = ws.get("scoped_controls") or []
    answers = ws.get("answers") or {}
    hints = inheritance_hints(env_scope, scoped)
    map_rows = inheritance_map_rows(env_scope, scoped)
    suggestions = []
    for item in scoping_suggestions(env_scope, answers, scoped):
        suggestions.append(
            {
                **item,
                "status": answers.get(item["control_id"], {}).get("status", "NOT STARTED"),
            }
        )
    hint_rows = []
    for item in hints:
        hint_rows.append(
            {
                **item,
                "status": answers.get(item["control_id"], {}).get("status", "NOT STARTED"),
            }
        )
    return {
        "org_profile": org_profile,
        "asset_scope": ws.get("asset_scope", {}),
        "asset_types": ASSET_TYPES,
        "env_scope": env_scope,
        "env_scope_labels": {
            "yes_no": YES_NO_LABELS,
            "cloud": CLOUD_LABELS,
        },
        "env_scope_fields": [
            {"key": "processes_cui", "label": "Does this system process CUI?", "type": "yes_no"},
            {"key": "uses_wireless", "label": "Corporate Wi-Fi or wireless access to CUI systems?", "type": "yes_no"},
            {"key": "remote_workforce", "label": "Employees access CUI remotely (VPN, RDP, cloud)?", "type": "yes_no"},
            {"key": "uses_m365", "label": "Microsoft 365 / Entra ID in scope for CUI?", "type": "yes_no"},
            {"key": "uses_google", "label": "Google Workspace in scope for CUI?", "type": "yes_no"},
            {"key": "cloud_hosting", "label": "Cloud hosting for CUI workloads", "type": "cloud"},
        ],
        "env_scope_complete": env_scope_complete(env_scope),
        "env_scope_summary": format_env_scope_summary(env_scope) if env_scope_complete(env_scope) else "",
        "inheritance_hints": hint_rows,
        "inheritance_map": map_rows,
        "scoping_suggestions": suggestions,
        "org_inventory": ws.get("org_inventory", merge_org_inventory(None)),
        "org_assets": merge_org_assets(ws.get("org_assets")),
        "scoped_controls_count": len(scoped),
        "scope_confirmed": bool(ws.get("scope_confirmed")),
        "audit_log": ws.get("audit_log") or [],
        "needs_wizard": profile_needs_wizard(org_profile),
        "wizard_steps": WIZARD_STEPS,
        "field_labels": FIELD_LABELS,
        "field_placeholders": FIELD_PLACEHOLDERS,
        "team_members": parse_team_roster(org_profile),
        "scope_coverage": compute_scope_coverage(ws),
        "system_scope": ws.get("system_scope", {}),
    }


@app.get("/api/settings")
def get_settings(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    auth_user = get_auth_user()
    auth_cfg = public_auth_config()
    needs_org = user_needs_organization()

    if needs_org:
        role = auth_user.role if auth_user else "Assessor"
        return {
            "current_role": role,
            "current_user_name": auth_user.name if auth_user else "",
            "team_members": [],
            "user_roles": USER_ROLES,
            "permissions": ROLE_PERMISSIONS.get(role, {}),
            "capabilities": role_capabilities(role),
            "clients": [],
            "active_client_id": "",
            "msp_mode": False,
            "sprs_history": [],
            "app_version": APP_VERSION,
            "auth_enabled": auth_cfg["enabled"],
            "auth_role_locked": auth_cfg["role_locked"],
            "auth_user_email": auth_user.email if auth_user else "",
            "sandbox_mode": auth_cfg.get("sandbox_mode", False),
            "needs_organization": True,
            **ai_public_status(),
        }

    clients = filter_clients_for_user(list_workspace_clients())
    active = client_id or active_client_id()
    if sandbox_mode() and clients and active not in {c["id"] for c in clients}:
        active = clients[0]["id"]
        activate_client(active)

    ws = load_workspace(active)
    role = _ws_role(ws, ws.get("client_id"))
    return {
        "current_role": role,
        "current_user_name": _current_user_name(ws),
        "team_members": parse_team_roster(ws.get("org_profile") or {}),
        "user_roles": USER_ROLES,
        "permissions": ROLE_PERMISSIONS.get(role, {}),
        "capabilities": role_capabilities(role),
        "clients": clients,
        "active_client_id": ws.get("client_id") or active_client_id(),
        "msp_mode": bool(ws.get("msp_mode")) or (sandbox_mode() and len(clients) > 1),
        "sprs_history": ws.get("sprs_history") or [],
        "app_version": APP_VERSION,
        "auth_enabled": auth_cfg["enabled"],
        "auth_role_locked": auth_cfg["role_locked"] or sandbox_mode(),
        "auth_user_email": auth_user.email if auth_user else "",
        "sandbox_mode": auth_cfg.get("sandbox_mode", False),
        "needs_organization": False,
        **ai_public_status(),
    }


@app.patch("/api/settings/role")
def patch_role(body: RolePatch, client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    if auth_enabled():
        detail = (
            "Role is assigned per organization in sandbox mode"
            if sandbox_mode()
            else "Role is assigned by Microsoft Entra ID groups"
        )
        raise HTTPException(403, detail)
    if body.role not in USER_ROLES:
        raise HTTPException(400, f"Invalid role: {body.role}")
    ws = load_workspace(client_id)
    old_role = ws.get("current_role", "")
    ws["current_role"] = body.role
    save_workspace(ws)
    field_diffs = {}
    if old_role != body.role:
        field_diffs["role"] = {"old": old_role, "new": body.role}
    _audit_log(ws, "updated", "settings", "role", {"role": body.role, "field_diffs": field_diffs, "security": True})
    return {"current_role": body.role}


@app.patch("/api/settings/user-name")
def patch_user_name(body: UserNamePatch, client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    if auth_enabled():
        raise HTTPException(403, "User name comes from your Microsoft Entra ID profile")
    ws = load_workspace(client_id)
    ws["current_user_name"] = (body.name or "").strip()
    save_workspace(ws)
    _audit_log(ws, "updated", "settings", "user_name", {"name": ws["current_user_name"]})
    return {"current_user_name": ws["current_user_name"]}


@app.patch("/api/settings/msp-mode")
def patch_msp_mode(body: MspModePatch, client_id: Optional[str] = Query(None)) -> Dict[str, bool]:
    ws = load_workspace(client_id)
    ws["msp_mode"] = body.msp_mode
    save_workspace(ws)
    _audit_log(ws, "updated", "settings", "msp_mode", {"msp_mode": body.msp_mode})
    return {"msp_mode": body.msp_mode}


@app.post("/api/clients")
def post_create_client(body: CreateClientBody, client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    if sandbox_mode():
        raise HTTPException(400, "Use POST /api/organizations to create a sandbox organization")
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    cid = create_client(body.display_name)
    _audit_log(ws, "created", "client", cid, {"name": body.display_name})
    return {"client_id": cid}


@app.patch("/api/clients/{client_id}")
def patch_client(client_id: str, body: RenameClientBody) -> Dict[str, str]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    rename_client(client_id, body.name)
    _audit_log(ws, "updated", "client", client_id, {"name": body.name.strip()})
    return {"client_id": client_id, "name": body.name.strip()}


@app.delete("/api/clients/{client_id}")
def remove_client(client_id: str) -> Dict[str, Any]:
    ws = load_workspace(None)
    _require_edit_org(ws)
    if client_id == "default":
        raise HTTPException(400, "Cannot delete the default workspace")
    if not delete_client(client_id):
        raise HTTPException(404, "Client not found")
    _audit_log(ws, "deleted", "client", client_id)
    return {"deleted": client_id, "active_client_id": active_client_id()}


@app.get("/api/journey")
def get_journey(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return compute_user_journey(
        ws["answers"],
        ws["org_profile"],
        ws.get("asset_scope", {}),
        ws["scoped_controls"],
        scope_confirmed=bool(ws.get("scope_confirmed")),
    )


class AssessmentStatusBody(BaseModel):
    assessment_type: str = ""
    status: str = ""
    status_date: str = ""
    affirming_official: str = ""


@app.get("/api/assessment/status")
def get_assessment_status(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return build_assessment_status(ws)


@app.get("/api/assessment/scope")
def get_assessment_scope(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {"scope": merge_scope(ws.get("cmmc_scope"))}


@app.get("/api/contracts")
def get_contracts(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {"contracts": contracts_with_status(ws)}


class ContractBody(BaseModel):
    name: str = ""
    contract_number: str = ""
    clause: str = ""
    required_status: str = ""
    flowdown_required: bool = False
    notes: str = ""


@app.post("/api/contracts")
def post_contract(body: ContractBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    try:
        contract = add_contract(ws, body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    save_workspace(ws)
    _audit_log(
        ws,
        "created",
        "contract",
        contract["id"],
        {"name": contract["name"], "clause": contract["clause"]},
    )
    return {"contract": contract}


@app.patch("/api/contracts/{contract_id}")
def patch_contract(
    contract_id: str,
    body: ContractBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    try:
        contract = update_contract(ws, contract_id, body.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not contract:
        raise HTTPException(404, "Contract not found")
    save_workspace(ws)
    return {"contract": contract}


@app.delete("/api/contracts/{contract_id}")
def remove_contract(contract_id: str, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    if not delete_contract(ws, contract_id):
        raise HTTPException(404, "Contract not found")
    save_workspace(ws)
    return {"status": "deleted"}


class L1StatusBody(BaseModel):
    status: str = ""


@app.get("/api/assessment/l1")
def get_l1_status(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return build_l1_status(ws)


@app.put("/api/assessment/l1/{control_id}")
def put_l1_status(control_id: str, body: L1StatusBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    try:
        result = apply_l1_status(ws, control_id, body.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    save_workspace(ws)
    return result


class L1AssessmentBody(BaseModel):
    status_date: str = ""
    affirming_official: str = ""


@app.put("/api/assessment/l1")
def put_l1_assessment(body: L1AssessmentBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    result = save_l1_assessment(ws, body.model_dump())
    save_workspace(ws)
    return result


@app.get("/api/assessment/l1/entry-text")
def get_l1_entry_text(client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    ws = load_workspace(client_id)
    return {"text": build_l1_entry_text(ws, ws["org_profile"])}


@app.put("/api/assessment/scope")
def put_assessment_scope(body: dict, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    try:
        scope = apply_scope(ws, body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    save_workspace(ws)
    _audit_log(
        ws,
        "updated",
        "assessment_scope",
        "",
        {"esp": scope.get("esp"), "facilities": scope.get("facilities") or ""},
    )
    return {"scope": scope}


@app.put("/api/assessment/status")
def put_assessment_status(body: AssessmentStatusBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    try:
        result = apply_assessment_status(
            ws,
            assessment_type=body.assessment_type,
            status=body.status,
            status_date=body.status_date,
            affirming_official=body.affirming_official,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    save_workspace(ws)
    _audit_log(
        ws,
        "updated",
        "assessment_status",
        body.assessment_type or body.status or "status",
        {
            "assessment_type": body.assessment_type,
            "status": body.status,
            "status_date": body.status_date,
        },
    )
    return result


@app.post("/api/assessment/closeout")
def post_assessment_closeout(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    try:
        result = complete_closeout(ws)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    save_workspace(ws)
    _audit_log(ws, "completed", "assessment_closeout", result.get("assessment_type") or "closeout", {"status": "final"})
    return result


@app.get("/api/assessment/next")
def get_next_control(
    client_id: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    nxt = find_next_incomplete(ws["answers"], ws["scoped_controls"], family)
    priorities = priority_controls(ws["answers"], ws["scoped_controls"], limit=8)
    info = CMMC_FRAMEWORK.get(nxt, {}) if nxt else {}
    next_status = ws["answers"].get(nxt, {}).get("status", "NOT STARTED") if nxt else ""
    priority_details = []
    for cid in priorities:
        cinfo = CMMC_FRAMEWORK.get(cid, {})
        cans = ws["answers"].get(cid, {})
        priority_details.append(
            {
                "id": cid,
                "name": cinfo.get("name", ""),
                "family": cinfo.get("family", ""),
                "status": cans.get("status", "NOT STARTED"),
                "weight_tier": _weight_tier(cid),
                "weight_badge": _weight_badge_label(cid),
            }
        )
    return {
        "next_control_id": nxt,
        "next_control_name": info.get("name", ""),
        "next_control_status": next_status,
        "priority_controls": priorities,
        "priority_details": priority_details,
    }


@app.post("/api/org-assets/topology")
async def upload_topology(
    file: UploadFile = File(...),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(413, "File exceeds 10 MB limit")
    blobs = dict(ws.get("org_asset_bytes") or {})
    fname = file.filename or "topology.png"
    set_topology_bytes(blobs, fname, data)
    assets = merge_org_assets(ws.get("org_assets"))
    assets["topology_filename"] = fname
    ws["org_asset_bytes"] = blobs
    ws["org_assets"] = assets
    save_workspace(ws)
    _audit_log(ws, "created", "topology", "", {"filename": fname})
    return {"topology_filename": fname}


@app.delete("/api/org-assets/topology")
def delete_topology(client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    blobs = dict(ws.get("org_asset_bytes") or {})
    ws["org_assets"] = remove_topology(merge_org_assets(ws.get("org_assets")), blobs)
    ws["org_asset_bytes"] = blobs
    save_workspace(ws)
    _audit_log(ws, "deleted", "topology")
    return {"topology_filename": ""}


@app.post("/api/org-assets/appendix")
async def upload_appendix(
    file: UploadFile = File(...),
    label: str = Query(""),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(413, "File exceeds 10 MB limit")
    blobs = dict(ws.get("org_asset_bytes") or {})
    assets = add_appendix_file(
        merge_org_assets(ws.get("org_assets")),
        blobs,
        file.filename or "appendix.bin",
        data,
        label=label,
    )
    ws["org_asset_bytes"] = blobs
    ws["org_assets"] = assets
    save_workspace(ws)
    _audit_log(ws, "created", "appendix", "", {"filename": file.filename, "label": label})
    return {"org_assets": assets}


@app.delete("/api/org-assets/appendix/{filename}")
def delete_appendix(filename: str, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    blobs = dict(ws.get("org_asset_bytes") or {})
    ws["org_assets"] = remove_appendix(merge_org_assets(ws.get("org_assets")), blobs, filename)
    ws["org_asset_bytes"] = blobs
    save_workspace(ws)
    _audit_log(ws, "deleted", "appendix", "", {"filename": filename})
    return {"org_assets": ws["org_assets"]}


@app.patch("/api/inventory")
def update_inventory(body: InventoryPatch, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    cleaned = [{col: str(row.get(col, "")).strip() for col in INVENTORY_COLUMNS} for row in body.assets]
    cleaned = [r for r in cleaned if any(r.values())]
    ws["org_inventory"] = set_inventory_assets(cleaned)
    save_workspace(ws)
    _audit_log(ws, "updated", "inventory", "", {"count": len(cleaned)})
    return {"org_inventory": ws["org_inventory"]}


@app.post("/api/inventory/import")
async def import_inventory(
    file: UploadFile = File(...),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    imported, warnings = import_inventory_csv(await file.read())
    if imported:
        ws["org_inventory"] = set_inventory_assets(imported)
        save_workspace(ws)
    _audit_log(ws, "imported", "inventory", "", {"count": len(imported)})
    return {"imported": len(imported), "warnings": warnings, "org_inventory": ws.get("org_inventory")}


@app.patch("/api/asset-scope")
def update_asset_scope(body: AssetScopePatch, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    ws["asset_scope"] = body.asset_scope
    ws["scoped_controls"] = apply_scope_from_assets(body.asset_scope)
    ws["scope_confirmed"] = True
    save_workspace(ws)
    _audit_log(ws, "updated", "scope", "asset", {"control_count": len(ws["scoped_controls"])})
    return {"asset_scope": ws["asset_scope"], "scoped_controls_count": len(ws["scoped_controls"])}


@app.patch("/api/env-scope")
def update_env_scope(body: EnvScopePatch, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    ws["env_scope"] = merge_env_scope(body.env_scope)
    save_workspace(ws)
    _audit_log(ws, "updated", "scope", "environment")
    return {"env_scope": ws["env_scope"]}


@app.get("/api/system-scope")
def get_system_scope(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    profile = ws["org_profile"]
    env = merge_env_scope(ws.get("env_scope"))
    scope = ws.get("system_scope", {})
    return {
        "system_name": profile.get("system_name", profile.get("org_name", "")),
        "description": profile.get("system_description", profile.get("description", "")),
        "cui_types": scope.get("cui_types", ""),
        "boundary_diagram": (ws.get("org_assets") or {}).get("topology_filename", ""),
        "external_connections": scope.get("external_connections", ""),
        "owner": profile.get("system_owner", ""),
        "last_review": scope.get("last_review", ""),
        "has_cui": env.get("processes_cui") == "yes",
        "cui_asset_pct": (ws.get("asset_scope") or {}).get("CUI Assets", 0),
    }


@app.patch("/api/system-scope")
def update_system_scope(body: SystemScopePatch, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    current = ws.get("system_scope", {})
    ws["system_scope"] = {**current, **{k: v for k, v in body.dict().items() if v != "" or k in body.dict(exclude_unset=True)}}
    save_workspace(ws)
    _audit_log(ws, "updated", "scope", "system")
    return {"system_scope": ws["system_scope"]}


@app.get("/api/documents")
def get_documents(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    docs = build_documents_list(ws["answers"], ws["scoped_controls"])
    return {"documents": docs, "total": len(docs)}


@app.get("/api/readiness/pre-c3pao")
def get_pre_c3pao(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    readiness = evaluate_pre_c3pao_readiness(
        ws["answers"],
        ws["org_profile"],
        ws.get("asset_scope", {}),
        ws["scoped_controls"],
    )
    obj = objective_coverage(ws["answers"], ws["scoped_controls"])
    return {**readiness, "objective_coverage": obj}


@app.get("/api/sprs/ledger")
def get_sprs_ledger(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    from readiness import build_control_ledger
    ledger = build_control_ledger(ws["answers"], ws["scoped_controls"])
    return {"rows": ledger, "count": len(ledger)}


class SprsSimulateBody(BaseModel):
    changes: List[Dict[str, Any]] = Field(default_factory=list)


@app.post("/api/sprs/simulate")
def post_sprs_simulate(body: SprsSimulateBody, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    from readiness import simulate_sprs
    return simulate_sprs(ws["answers"], ws["scoped_controls"], body.changes)


@app.get("/api/export/ssp")
def download_ssp(
    client_id: Optional[str] = Query(None),
    fill_starters: bool = Query(False),
    version: str = Query(""),
    prepared_by: str = Query(""),
    approved_by: str = Query(""),
) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    org_profile = ws["org_profile"]
    org_name = org_profile.get("org_name") or "Organization"
    export_answers = answers_with_export_starters(
        ws["answers"],
        ws["scoped_controls"],
        org_profile,
        merge_env_scope(ws.get("env_scope")),
        fill_empty=fill_starters,
    )
    try:
        risks_by_control: dict[str, list[dict]] = {}
        for r in list_risk_items():
            for cid in list(set(r.get("control_ids", [])) | ({r.get("control_id")} if r.get("control_id") else set())):
                risks_by_control.setdefault(cid, []).append(r)
        data = assemble_ssp(
            export_answers,
            ws["asset_scope"],
            org_name=org_name,
            scoped_controls=ws["scoped_controls"],
            org_profile=org_profile,
            template_path=resolve_ssp_template(),
            org_assets=ws.get("org_assets"),
            org_asset_bytes=ws.get("org_asset_bytes"),
            audit_log=ws.get("audit_log"),
            org_inventory=ws.get("org_inventory"),
            risks_by_control=risks_by_control,
            system_scope=ws.get("system_scope", {}),
            ssp_version=version or ws.get("system_scope", {}).get("ssp_version", ""),
            prepared_by=prepared_by or ws.get("system_scope", {}).get("prepared_by", ""),
            approved_by=approved_by or ws.get("system_scope", {}).get("approved_by", ""),
        )
    except Exception as exc:
        raise HTTPException(500, f"SSP build failed: {exc}") from exc

    stamp_fields = export_stamp(ws)
    ws.update(stamp_fields)
    save_workspace(ws)

    safe = _safe_filename(org_name)
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="CMMC_SSP_{safe}_{stamp}.docx"'},
    )


@app.get("/api/export/poam")
def download_poam(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    data = export_poam_xlsx(ws["answers"], ws["scoped_controls"])
    org_name = ws["org_profile"].get("org_name") or "Organization"
    safe = _safe_filename(org_name)
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="CMMC_POAM_{safe}_{stamp}.xlsx"'},
    )


@app.get("/api/export/poam-csv")
def download_poam_csv(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    data = export_poam_csv(ws["answers"], ws["scoped_controls"])
    org_name = ws["org_profile"].get("org_name") or "Organization"
    safe = _safe_filename(org_name)
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="CMMC_POAM_{safe}_{stamp}.csv"'},
    )


@app.get("/api/export/poam-oscal")
def download_poam_oscal(client_id: Optional[str] = Query(None)) -> Response:
    from poam_export import export_poam_oscal

    ws = load_workspace(client_id)
    _require_export(ws)
    try:
        from exceptions.store import list_exceptions
        exceptions = list_exceptions() or []
    except Exception:
        exceptions = None
    doc = export_poam_oscal(
        ws["answers"],
        ws["scoped_controls"],
        exceptions=exceptions,
        org_name=ws["org_profile"].get("org_name") or "Organization",
    )
    org_name = ws["org_profile"].get("org_name") or "Organization"
    safe = _safe_filename(org_name)
    stamp = datetime.now().strftime("%Y%m%d")
    return JSONResponse(
        content=doc,
        headers={"Content-Disposition": f'attachment; filename="CMMC_POAM_OSCAL_{safe}_{stamp}.json"'},
    )


@app.get("/api/export/poam-exceptions")
def download_poam_exceptions(client_id: Optional[str] = Query(None)) -> Response:
    from exceptions.store import list_exceptions
    from poam_export import build_poam_dataframe, POAM_COLUMNS
    import io

    ws = load_workspace(client_id)
    org_name = ws["org_profile"].get("org_name") or "Organization"
    safe = _safe_filename(org_name)
    stamp = datetime.now().strftime("%Y%m%d")
    cid = ws.get("client_id") or ws.get("id") or client_id or ""
    exceptions = list_exceptions(workspace_id=cid, framework="CMMC")
    df = build_poam_dataframe(ws["answers"], ws["scoped_controls"], exceptions)
    if not df.empty:
        df = df[df["Weakness ID"].str.startswith("WK-EX-", na=False)]
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    data = buf.getvalue()
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="CMMC_POAM_Exceptions_{safe}_{stamp}.csv"'},
    )


@app.get("/api/export/sprs-summary")
def download_sprs_summary(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    sprs = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])
    text = build_sprs_entry_summary(
        ws["org_profile"], sprs, ws["scoped_controls"], ws.get("asset_scope", {}),
        cmmc_assessment=ws.get("cmmc_assessment"),
        cmmc_scope=ws.get("cmmc_scope"),
    )
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=text.encode("utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="SPRS_Entry_Summary_{stamp}.txt"'},
    )


@app.get("/api/export/sprs-one-pager")
def download_sprs_one_pager(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    sprs = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])
    text = build_sprs_one_pager(ws["org_profile"], sprs, ws["scoped_controls"], ws["answers"])
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=text.encode("utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="SPRS_One_Pager_{stamp}.txt"'},
    )


@app.get("/api/export/audit-package")
def download_audit_package(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    org_name = ws["org_profile"].get("org_name") or "Organization"
    safe = _safe_filename(org_name)
    stamp = datetime.now().strftime("%Y%m%d")
    try:
        data = build_export_package(
            ws["answers"],
            ws["org_profile"],
            ws.get("asset_scope", {}),
            ws["scoped_controls"],
            export_poam_fn=lambda: export_poam_csv(ws["answers"], ws["scoped_controls"]),
            audit_log=ws.get("audit_log"),
            org_assets=ws.get("org_assets"),
            org_asset_bytes=ws.get("org_asset_bytes"),
            org_inventory=ws.get("org_inventory"),
            restored_evidence=ws.get("restored_evidence"),
            env_scope=ws.get("env_scope"),
        )
    except Exception as exc:
        raise HTTPException(500, f"Package build failed: {exc}") from exc
    stamp_fields = export_stamp(ws)
    ws.update(stamp_fields)
    save_workspace(ws)
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="CMMC_Audit_Package_{safe}_{stamp}.zip"'},
    )


@app.get("/api/analytics")
def get_analytics(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_view_dashboard(ws)
    return build_analytics(ws["answers"], ws["scoped_controls"])


@app.get("/api/remediation")
def get_remediation(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return build_remediation(ws["answers"], ws["scoped_controls"], ws.get("sprs_history") or [])


@app.get("/api/controls/{control_id}/meta")
def get_control_meta(control_id: str, client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    if control_id not in CMMC_FRAMEWORK:
        raise HTTPException(404, "Control not found")
    return control_meta(ws["answers"], ws["scoped_controls"], control_id)


@app.post("/api/controls/{control_id}/validate-config")
async def validate_control_config(
    control_id: str,
    file: UploadFile = File(...),
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_validate_config(ws)
    if control_id not in VALIDATION_RULES:
        raise HTTPException(404, "No validation rules for this control")
    content = (await file.read()).decode("utf-8", errors="ignore")
    result = validate_evidence_against_rules(content, control_id)
    if result["passed"]:
        ans = ws["answers"].setdefault(control_id, {})
        ans["validation_passed"] = True
        passed_rules = [d["rule"] for d in result["details"] if d["passed"]]
        ans["test"] = f"Auto-validated: {', '.join(passed_rules)}"
        save_workspace(ws)
    return result


@app.get("/api/help")
def get_help() -> Dict[str, Any]:
    return {"views": VIEW_HELP, "faq": FAQ}


@app.get("/api/alerts")
def get_alerts(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return {
        "poam_overdue": poam_overdue_alerts(ws["answers"], ws["scoped_controls"]),
        "env_suggestions": scoping_suggestions(
            merge_env_scope(ws.get("env_scope")),
            ws["answers"],
            ws["scoped_controls"],
        )[:12],
    }


@app.get("/api/recent-activity")
def get_recent_activity(client_id: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    ws = load_workspace(client_id)
    activity: List[Dict[str, Any]] = []

    for entry in ws.get("audit_log") or []:
        ts = entry.get("timestamp", "")
        cid = entry.get("control_id", "")
        field = entry.get("field", "")
        new_val = entry.get("new_value", "")
        ctrl = CMMC_FRAMEWORK.get(cid, {})
        ctrl_name = f"{cid} – {ctrl.get('name', '')}" if cid else ""
        if field == "status":
            activity.append({"type": "status_change", "control_id": cid, "message": f"{ctrl_name} → {new_val}", "timestamp": ts})
        elif field == "implementation_narrative":
            activity.append({"type": "narrative", "control_id": cid, "message": f"Narrative updated for {ctrl_name}", "timestamp": ts})
        elif field == "owner":
            activity.append({"type": "owner", "control_id": cid, "message": f"Owner set to {new_val} for {ctrl_name}", "timestamp": ts})
        else:
            activity.append({"type": "field_change", "control_id": cid, "message": f"{field} updated for {ctrl_name}", "timestamp": ts})

    for cid, ans in ws.get("answers", {}).items():
        ctrl = CMMC_FRAMEWORK.get(cid, {})
        ctrl_name = f"{cid} – {ctrl.get('name', '')}" if cid else cid
        for ev in ans.get("evidence") or []:
            ts = ev.get("upload_date", "")
            if ts:
                activity.append({"type": "evidence_uploaded", "control_id": cid, "message": f"Evidence uploaded to {ctrl_name}", "timestamp": ts})
        for cmt in ans.get("comments") or []:
            ts = cmt.get("created_at", "")
            if ts:
                activity.append({"type": "comment_added", "control_id": cid, "message": f"Comment on {ctrl_name}", "timestamp": ts})

    export_ts = ws.get("last_export_at")
    if export_ts:
        activity.append({"type": "export_created", "control_id": "", "message": "SSP and POA&M exported", "timestamp": export_ts})

    activity.sort(key=lambda e: e["timestamp"], reverse=True)
    return activity[:20]


@app.get("/api/sprs-detail")
def get_sprs_detail(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])


@app.get("/api/readiness/review")
def get_readiness_review(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    review = run_readiness_review(
        ws["answers"],
        ws["org_profile"],
        ws["scoped_controls"],
        merge_env_scope(ws.get("env_scope")),
        ws.get("asset_scope"),
    )
    return review


@app.get("/api/readiness/evidence-coverage")
def get_evidence_coverage(client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return compute_readiness_scores(ws["answers"], ws["org_profile"], ws["scoped_controls"])


@app.get("/api/objectives/family/{family}")
def get_family_objectives(family: str) -> Dict[str, Any]:
    return {"family": family, "prompts": family_prompts(family)}


@app.get("/api/validation/sprs")
def get_sprs_validation() -> Dict[str, Any]:
    return {"scenarios": run_validation(), "report": format_validation_report()}


@app.post("/api/import/poam")
async def import_poam(file: UploadFile = File(...), client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_controls(ws)
    updated, applied, warnings = import_poam_csv(await file.read(), ws["answers"], ws["scoped_controls"])
    for cid in applied:
        ws["answers"][cid] = updated[cid]
    save_workspace(ws)
    return {"applied": applied, "warnings": warnings, "count": len(applied)}


@app.post("/api/import/workspace")
async def import_workspace(file: UploadFile = File(...), client_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    loaded, warnings = load_workspace_zip_bytes(await file.read())
    loaded["client_id"] = ws.get("client_id")
    save_workspace(loaded)
    return {"ok": True, "warnings": warnings}


@app.post("/api/workspace/reset")
def reset_workspace(client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    save_workspace(reset_workspace_state(ws))
    return {"status": "reset"}


@app.post("/api/workspace/reset-controls")
def reset_controls(client_id: Optional[str] = Query(None)) -> Dict[str, str]:
    ws = load_workspace(client_id)
    _require_edit_org(ws)
    save_workspace(reset_controls_only(ws))
    return {"status": "controls_reset"}


# ─── PDF exports ──────────────────────────────────────

@app.get("/api/export/pdf/ssp-summary")
def download_ssp_pdf(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    sprs = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])
    pdf_bytes = build_ssp_summary_pdf(ws, sprs)
    safe = _safe_filename(ws["org_profile"].get("org_name") or "Organization")
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="CMMC_SSP_Summary_{safe}_{stamp}.pdf"'},
    )


@app.get("/api/export/pdf/poam")
def download_poam_pdf(client_id: Optional[str] = Query(None)) -> Response:
    from exceptions.store import list_exceptions

    ws = load_workspace(client_id)
    _require_export(ws)
    cid = ws.get("client_id") or ws.get("id") or client_id or ""
    exceptions = list_exceptions(workspace_id=cid, framework="CMMC")
    df = build_poam_dataframe(ws["answers"], ws["scoped_controls"], exceptions)
    entries = df.to_dict("records") if not df.empty else []
    pdf_bytes = build_poam_pdf(ws, entries)
    safe = _safe_filename(ws["org_profile"].get("org_name") or "Organization")
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="CMMC_POAM_{safe}_{stamp}.pdf"'},
    )


@app.get("/api/export/pdf/sprs")
def download_sprs_pdf(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    sprs = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])
    pdf_bytes = build_sprs_pdf(ws, sprs, ws["answers"], ws["scoped_controls"])
    safe = _safe_filename(ws["org_profile"].get("org_name") or "Organization")
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="CMMC_SPRS_{safe}_{stamp}.pdf"'},
    )


@app.get("/api/export/pdf/executive-report")
def download_executive_report_pdf(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    sprs = calculate_detailed_sprs(ws["answers"], ws["scoped_controls"])
    eligibility = poam_eligibility(ws["answers"], ws["scoped_controls"])
    risks = list_risk_items()
    pdf_bytes = build_executive_report(ws, sprs, eligibility, risks)
    safe = _safe_filename(ws["org_profile"].get("org_name") or "Organization")
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Executive_Board_Report_{safe}_{stamp}.pdf"'},
    )


# ──────────────────────────────────────────────────────

@app.get("/api/export/workspace")
def export_workspace_zip(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    data = build_workspace_zip(ws)
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="CMMC_Workspace_{stamp}.zip"'},
    )


@app.get("/api/export/oscal")
def export_oscal(
    client_id: Optional[str] = Query(None),
    type: str = Query("ssp", pattern="^(ssp|poam)$"),
) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    org_name = ws["org_profile"].get("org_name") or "Organization"
    if type == "poam":
        text = export_oscal_poam_json(ws["answers"], ws["scoped_controls"], org_name)
        filename = "CMMC_POAM_OSCAL.json"
    else:
        text = export_oscal_json(ws["answers"], ws.get("asset_scope", {}), ws.get("audit_log", []), org_name)
        filename = "CMMC_OSCAL.json"
    return Response(
        content=text.encode("utf-8"),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/export/appendix-pack")
def export_appendix_pack(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    return Response(
        content=get_appendix_pack_zip(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="SSP_Appendix_Starter_Pack.zip"'},
    )


@app.get("/api/export/readiness-review")
def download_readiness_review(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    review = run_readiness_review(
        ws["answers"],
        ws["org_profile"],
        ws["scoped_controls"],
        merge_env_scope(ws.get("env_scope")),
        ws.get("asset_scope"),
    )
    org_name = ws["org_profile"].get("org_name") or "Organization"
    text = format_readiness_review_report(review, org_name)
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=text.encode("utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="Readiness_Review_{stamp}.txt"'},
    )


@app.get("/api/export/evidence-coverage")
def download_evidence_coverage(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    scores = compute_readiness_scores(ws["answers"], ws["org_profile"], ws["scoped_controls"])
    org_name = ws["org_profile"].get("org_name") or "Organization"
    text = format_evidence_coverage_report(scores["evidence_detail"], scores, org_name)
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=text.encode("utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="Evidence_Coverage_{stamp}.txt"'},
    )


@app.get("/api/export/validation-report")
def download_validation_report(client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=format_validation_report().encode("utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="SPRS_Validation_{stamp}.txt"'},
    )


@app.get("/api/export/ssp-family")
def download_ssp_family(family: str = Query(...), client_id: Optional[str] = Query(None)) -> Response:
    ws = load_workspace(client_id)
    _require_export(ws)
    if family not in FAMILY_ORDER:
        raise HTTPException(400, f"Unknown family: {family}")
    org_name = ws["org_profile"].get("org_name") or "Organization"
    try:
        risks_by_control: dict[str, list[dict]] = {}
        for r in list_risk_items():
            for cid in list(set(r.get("control_ids", [])) | ({r.get("control_id")} if r.get("control_id") else set())):
                risks_by_control.setdefault(cid, []).append(r)
        data = assemble_ssp_family(
            ws["answers"],
            family,
            org_name=org_name,
            scoped_controls=ws["scoped_controls"],
            risks_by_control=risks_by_control,
            org_profile=ws["org_profile"],
            org_inventory=ws.get("org_inventory"),
        )
    except Exception as exc:
        raise HTTPException(500, f"SSP family build failed: {exc}") from exc
    safe = _safe_filename(f"{org_name}_{family}")
    stamp = datetime.now().strftime("%Y%m%d")
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="CMMC_SSP_{safe}_{stamp}.docx"'},
    )


class CollectorCredentialsBody(BaseModel):
    credentials: Dict[str, str] = Field(default_factory=dict)


class AiKeyBody(BaseModel):
    api_key: str = ""


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


class WebhookCollectorBody(BaseModel):
    name: str
    source_system: str


def _bearer_token(request: Request) -> Optional[str]:
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


@app.get("/api/webhooks")
def get_webhook_collectors() -> Dict[str, Any]:
    collectors = [c.to_dict(include_token=False) for c in list_webhook_collectors()]
    return {
        "collectors": collectors,
        "env_token_configured": bool(env_webhook_token()),
        "ingest_url": "/api/webhook/external",
    }


@app.post("/api/webhooks")
def post_webhook_collector(body: WebhookCollectorBody) -> Dict[str, Any]:
    ws = load_workspace(active_client_id())
    _require_edit_controls(ws)
    try:
        collector = create_webhook_collector(body.name, body.source_system)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    _audit_log(ws={}, action="created", resource_type="webhook", resource_id=collector.id, details={"name": body.name, "source": body.source_system, "security": True})
    return {
        "collector": collector.to_dict(include_token=True),
        "usage": "POST /api/webhook/external with the webhook_token in the Authorization header",
    }


@app.delete("/api/webhooks/{collector_id}")
def delete_webhook_collector_route(collector_id: str) -> Dict[str, str]:
    ws = load_workspace(active_client_id())
    _require_edit_controls(ws)
    if not delete_webhook_collector(collector_id):
        raise HTTPException(404, "Webhook collector not found")
    _audit_log(ws={}, action="deleted", resource_type="webhook", resource_id=collector_id, details={"security": True})
    return {"status": "deleted"}


@app.post("/api/webhook/external")
def post_webhook_external(
    request: Request,
    body: Dict[str, Any],
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Arm's-length evidence ingestion (metadata-only). Bearer token required."""
    token = _bearer_token(request)
    try:
        result = ingest_webhook_payload(body, token=token, client_id=client_id, attach=True)
    except PermissionError as exc:
        raise HTTPException(401, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"Ingestion failed: {exc}") from exc

    payload = result.to_dict()
    if result.status == "duplicate":
        raise HTTPException(409, detail=payload)
    return JSONResponse(content=payload, status_code=201)


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


@app.get("/api/collectors/monitoring/events")
def get_collector_drift_events(
    connector_id: Optional[str] = Query(None),
    limit: int = Query(30, ge=1, le=100),
) -> Dict[str, Any]:
    return {"events": get_events(limit=limit, connector_id=connector_id)}


@app.get("/api/collectors/monitoring/freshness")
def get_collector_freshness(
    client_id: Optional[str] = Query(None),
    max_age_days: int = Query(7, ge=1, le=90),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    return freshness_for_workspace(ws["answers"], max_age_days=max_age_days)


@app.get("/api/collectors/health")
def get_collector_health() -> Dict[str, Any]:
    return collector_health_summary()


@app.post("/api/collectors/monitoring/run-due")
def post_run_due_collectors(
    request: Request,
    body: RunDueBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    internal_scheduler = scheduler_token_matches(_bearer_token(request))
    ws = load_workspace(client_id)
    if not internal_scheduler:
        _require_edit_controls(ws)
    _audit_log(ws, "run_due", "scheduler", "", {"use_fixture_if_unconfigured": body.use_fixture_if_unconfigured or sandbox_fixture_only()})
    try:
        return run_due_connectors(
            client_id=client_id,
            use_fixture_if_unconfigured=body.use_fixture_if_unconfigured or sandbox_fixture_only(),
        )
    except Exception as exc:
        raise HTTPException(500, f"Scheduled run failed: {exc}") from exc


@app.get("/api/collectors/monitoring/scheduler-status")
def get_scheduler_status() -> Dict[str, Any]:
    return read_scheduler_heartbeat()


@app.patch("/api/collectors/{connector_id}/schedule")
def patch_collector_schedule(connector_id: str, body: CollectorScheduleBody) -> Dict[str, Any]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    if body.interval is not None and body.interval not in ("manual", "daily", "weekly"):
        raise HTTPException(400, "interval must be manual, daily, or weekly")
    ws = load_workspace(active_client_id())
    _require_edit_controls(ws)
    state = patch_monitor_schedule(
        connector_id,
        enabled=body.enabled,
        interval=body.interval,  # type: ignore[arg-type]
        attach_on_run=body.attach_on_run,
    )
    _audit_log(ws, "updated", "schedule", connector_id, {"enabled": body.enabled, "interval": body.interval})
    return state.to_dict()


# Shared collector router (mappings, posture) moved to the Global service
# (/api/core) — this app keeps its own /api/collectors/{connector_id}
# run/schedule endpoints below.


@app.get("/api/collectors/{connector_id}")
def get_collector(connector_id: str) -> Dict[str, Any]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    meta = CONNECTOR_CATALOG[connector_id]
    return {**meta, **credentials_status(connector_id, meta["required_fields"])}


@app.put("/api/collectors/{connector_id}/credentials")
def put_collector_credentials(connector_id: str, body: CollectorCredentialsBody) -> Dict[str, Any]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    meta = CONNECTOR_CATALOG[connector_id]
    creds = body.credentials
    missing = [f for f in meta["required_fields"] if not creds.get(f)]
    if missing:
        raise HTTPException(400, f"Missing required fields: {', '.join(missing)}")
    ws = load_workspace(active_client_id())
    _require_edit_controls(ws)
    save_credentials(connector_id, creds)
    _audit_log(ws={}, action="saved", resource_type="credentials", resource_id=connector_id, details={"security": True})
    return credentials_status(connector_id, meta["required_fields"])


@app.delete("/api/collectors/{connector_id}/credentials")
def remove_collector_credentials(connector_id: str) -> Dict[str, str]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    ws = load_workspace(active_client_id())
    _require_edit_controls(ws)
    delete_credentials(connector_id)
    _audit_log(ws={}, action="deleted", resource_type="credentials", resource_id=connector_id, details={"security": True})
    return {"status": "deleted"}


# ── BYOK AI key (Integrations page) ──────────────────────────────────────
# The key is stored via credentials_store (encrypted at rest under the data
# dir). No endpoint ever returns the key itself — only has/source indicators
# (credential-echo safe; see ai_config.public_status).


@app.get("/api/settings/ai-key")
def get_ai_key_status() -> Dict[str, Any]:
    return {"has_ai_key": bool(ai_api_key()), "source": ai_key_source_name()}


@app.put("/api/settings/ai-key")
def put_ai_key(body: AiKeyBody) -> Dict[str, Any]:
    key = (body.api_key or "").strip()
    if not key:
        raise HTTPException(400, "api_key must not be empty")
    ws = load_workspace(active_client_id())
    _require_edit_controls(ws)
    save_credentials(AI_KEY_CONNECTOR_ID, {"api_key": key})
    _audit_log(ws={}, action="saved", resource_type="ai_key", resource_id=AI_KEY_CONNECTOR_ID, details={"security": True})
    return {"has_ai_key": True, "source": ai_key_source_name()}


@app.delete("/api/settings/ai-key")
def remove_ai_key() -> Dict[str, Any]:
    ws = load_workspace(active_client_id())
    _require_edit_controls(ws)
    delete_credentials(AI_KEY_CONNECTOR_ID)
    _audit_log(ws={}, action="deleted", resource_type="ai_key", resource_id=AI_KEY_CONNECTOR_ID, details={"security": True})
    return {"has_ai_key": bool(ai_api_key()), "source": ai_key_source_name()}


def _clear_last_error(connector_id: str) -> None:
    try:
        state = get_monitor_states([connector_id])[0]
        if state.last_error is not None:
            state.last_error = None
            save_monitor_state(state)
    except Exception:
        pass


@app.post("/api/collectors/{connector_id}/run")
def post_collector_run(
    connector_id: str,
    body: CollectorRunBody,
    client_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    ws = load_workspace(client_id)
    _require_edit_controls(ws)
    meta = CONNECTOR_CATALOG.get(connector_id) or {}
    if meta.get("import_only"):
        raise HTTPException(400, f"Connector '{connector_id}' is an import connector — use POST /api/collectors/{connector_id}/import")
    use_fixture = body.use_fixture or sandbox_fixture_only()
    try:
        if body.attach:
            result = run_and_attach(
                connector_id,
                use_fixture=use_fixture,
                client_id=client_id,
                control_ids=body.control_ids,
            )
            persist_live_asset_snapshot(
                connector_id,
                result.run.checks,
                client_id=client_id,
                synced_at=result.run.completed_at,
            )
            _audit_log(ws, "run", "connector", connector_id, {"fixture": use_fixture, "attached": True})
            _clear_last_error(connector_id)
            return result.to_dict()
        run = run_collector(connector_id, use_fixture=use_fixture, client_id=client_id)
        persist_live_asset_snapshot(
            connector_id,
            run.checks,
            client_id=client_id,
            synced_at=run.completed_at,
        )
        _audit_log(ws, "run", "connector", connector_id, {"fixture": use_fixture, "attached": False})
        _clear_last_error(connector_id)
        return {
            "run": run.to_dict(),
            "attached": [],
            "monitor_run_id": run.monitor_run_id,
            "drift_events": run.drift_events,
        }
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"Collector failed: {exc}") from exc


@app.post("/api/collectors/{connector_id}/import")
def post_collector_import(
    connector_id: str,
    file: UploadFile = File(...),
    client_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Import external scanner output (Prowler / ScubaGear JSON) as a collector run."""
    from collectors.config import collectors_state_dir

    meta = CONNECTOR_CATALOG.get(connector_id)
    if not meta or not meta.get("import_only"):
        raise HTTPException(400, f"Connector '{connector_id}' does not support imports")

    ws = load_workspace(client_id)
    _require_edit_controls(ws)

    MAX_IMPORT_MB = 50
    data = file.file.read(MAX_IMPORT_MB * 1024 * 1024 + 1) if file.file else b""
    if len(data) > MAX_IMPORT_MB * 1024 * 1024:
        raise HTTPException(413, f"Import file exceeds {MAX_IMPORT_MB} MB limit")
    if not data:
        raise HTTPException(400, "Empty import file")
    try:
        json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(400, f"Import file must be valid JSON: {exc}") from exc

    imports_dir = collectors_state_dir() / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    import time as _time

    stamp = _time.strftime("%Y%m%dT%H%M%SZ", _time.gmtime())
    path = imports_dir / f"{connector_id}_{stamp}.json"
    path.write_bytes(data)

    # Keep the imports dir bounded — retain the most recent 20 per connector.
    try:
        old = sorted(imports_dir.glob(f"{connector_id}_*.json"))
        for stale in old[:-20]:
            stale.unlink(missing_ok=True)
    except OSError:
        pass

    try:
        from cmmc_collectors.attach import run_and_attach

        result = run_and_attach(
            connector_id,
            creds_override={"import_file": str(path)},
            client_id=client_id,
        )
        persist_live_asset_snapshot(
            connector_id,
            result.run.checks,
            client_id=client_id,
            synced_at=result.run.completed_at,
        )
        _audit_log(ws, "import", "connector", connector_id, {"file": path.name, "checks": len(result.run.checks)})
        _clear_last_error(connector_id)
        return result.to_dict()
    except Exception as exc:
        raise HTTPException(500, f"Import failed: {exc}") from exc


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


app.include_router(audit_router)
app.include_router(testing_router)
app.include_router(auth_router)

_static_dir = os.environ.get("PLATFORM_STATIC")
if _static_dir and Path(_static_dir).is_dir():
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="frontend")
