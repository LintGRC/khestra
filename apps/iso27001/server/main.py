"""ISO 27001 Khestra API."""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from security_headers.ratelimit import add_rate_limiting
from security_headers.security import add_security_headers
from dotenv import load_dotenv

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
# CMMC core is appended so entra_auth / collectors / sandbox helpers resolve
# without shadowing ISO 27001 modules.
for path in (PACKAGES, EVIDENCE, CORE, PLATFORM / "server"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
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

from config import DATA_DIR as ISO_DATA_DIR, FRAMEWORK_ID, ORG_NAME  # noqa: E402
from kevidence.config import configure as configure_evidence  # noqa: E402
from kevidence.availability import collectors_available  # noqa: E402

configure_evidence(data_dir=ISO_DATA_DIR, platform_root=PLATFORM)
if collectors_available():
    import iso27001_collectors  # noqa: F401,E402 — register evidence mapping

from permissions_api import can_edit_controls, can_export  # noqa: E402
from soa import (  # noqa: E402
    init_store as init_soa_store,
    export_csv,
    export_docx,
    export_xlsx,
    get_control,
    linked_risks,
    list_soa,
    rollup,
    sync_soa_from_risks,
    update_control,
)
from iso_risk_report import export_risk_report_docx, export_risk_report_xlsx  # noqa: E402
from iso_audit_pack import (  # noqa: E402
    export_auditor_pack_zip,
    export_internal_audit_report_docx,
    export_management_review_minutes_docx,
    export_nc_capa_xlsx,
)
from demo_seed import load_demo as load_iso_demo  # noqa: E402
from control_tests.store import list_tests  # noqa: E402
from evidence_hub.store import list_evidence  # noqa: E402
EVIDENCE_GUIDANCE: dict = {}


def guidance_for(control_id: str) -> dict:
    """Check-keyed evidence guidance is part of the collectors edition."""
    return {}  # noqa: E402

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
from audit.store import init_store as init_audit_store  # noqa: E402
from audit.routes import router as audit_router  # noqa: E402
from risks.routes import router as risks_router  # noqa: E402
from risks.store import init_store as init_risks_store  # noqa: E402
from control_tests.store import init_store as init_control_tests_store  # noqa: E402
from control_tests.routes import router as control_tests_router  # noqa: E402
from testing.store import init_store as init_testing_store  # noqa: E402
from testing.routes import router as testing_router  # noqa: E402
from findings.store import init_store as init_findings_store  # noqa: E402
from findings.routes import router as findings_router  # noqa: E402
from audit_center.store import init_store as init_audit_center_store  # noqa: E402
from audit_center.routes import router as audit_center_router  # noqa: E402
from training.store import init_store as init_training_store  # noqa: E402
from training.routes import router as training_router  # noqa: E402
from personnel.store import init_store as init_personnel_store  # noqa: E402
from personnel.routes import router as personnel_router  # noqa: E402
from assets.store import init_store as init_assets_store  # noqa: E402
from assets.routes import router as assets_router  # noqa: E402
from audit_log.store import init_store as init_audit_log_store  # noqa: E402
from audit_log.routes import router as audit_log_router  # noqa: E402
from evidence_hub.store import init_store as init_evidence_hub_store  # noqa: E402
from evidence_hub.routes import router as evidence_hub_router  # noqa: E402
from incidents.store import init_store as init_incidents_store  # noqa: E402
from incidents.routes import router as incidents_router  # noqa: E402
from reviews.store import init_store as init_reviews_store  # noqa: E402
from reviews.routes import router as reviews_router  # noqa: E402
from org_context.store import init_store as init_org_context_store  # noqa: E402
from org_context.routes import router as org_context_router  # noqa: E402
from management_review.store import init_store as init_management_review_store  # noqa: E402
from management_review.routes import router as management_review_router  # noqa: E402
from notifications.store import init_store as init_notification_store  # noqa: E402
from compliance_calendar.store import init_store as init_compliance_calendar_store  # noqa: E402
from notifications.routes import router as notifications_router  # noqa: E402
from compliance_calendar.routes import router as compliance_calendar_router  # noqa: E402
from effectiveness.routes import router as effectiveness_router  # noqa: E402

if collectors_available():
    from collectors.routes import router as collectors_router  # noqa: E402
    from collectors.credentials_store import (  # noqa: E402
        credentials_status,
        delete_credentials,
        save_credentials,
    )
    from collectors.engine import recent_runs, run_collector  # noqa: E402
    from collectors.monitor_store import get_events, patch_monitor_schedule  # noqa: E402
    from collectors.registry import CONNECTOR_CATALOG, list_connectors  # noqa: E402
    from collectors.dev_scheduler import lifespan_scheduler  # noqa: E402
    from iso27001_collectors.attach import run_and_attach  # noqa: E402
    from iso27001_collectors.scheduler import monitoring_summary, run_due_connectors  # noqa: E402
    COLLECTORS_AVAILABLE = True
else:
    COLLECTORS_AVAILABLE = False

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
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _noop_lifespan_scheduler():
        yield

    lifespan_scheduler = _noop_lifespan_scheduler
    run_and_attach = lambda connector_id, **kw: (_MockRun(), [], [])
    monitoring_summary = lambda: {}
    run_due_connectors = lambda **kw: {"ran_count": 0, "due_count": 0}


@asynccontextmanager
async def _lifespan(_app: FastAPI):

    try:
        from auth.deploy_guard import assert_safe_auth_posture
        assert_safe_auth_posture()
    except RuntimeError as e:
        print(f"[startup] AUTH POSTURE REFUSAL: {e}", file=sys.stderr)
        raise
    for _init_fn, _path in [
        (init_remediation_store, str(ISO_DATA_DIR)),
        (init_policy_store, str(ISO_DATA_DIR)),
        (init_orgs_store, str(ISO_DATA_DIR)),
        (init_raci_store, str(ISO_DATA_DIR)),
        (init_exception_store, str(ISO_DATA_DIR)),
        (init_vendor_store, str(ISO_DATA_DIR)),
        (init_audit_store, str(ISO_DATA_DIR)),
        (init_risks_store, str(ISO_DATA_DIR)),
        (init_control_tests_store, str(ISO_DATA_DIR)),
        (init_testing_store, str(ISO_DATA_DIR)),
        (init_findings_store, str(ISO_DATA_DIR)),
        (init_audit_center_store, str(ISO_DATA_DIR)),
        (init_training_store, str(ISO_DATA_DIR)),
        (init_personnel_store, str(ISO_DATA_DIR)),
        (init_assets_store, str(ISO_DATA_DIR)),
        (init_audit_log_store, str(ISO_DATA_DIR)),
        (init_evidence_hub_store, str(ISO_DATA_DIR)),
        (init_incidents_store, str(ISO_DATA_DIR)),
        (init_reviews_store, str(ISO_DATA_DIR)),
        (init_org_context_store, str(ISO_DATA_DIR)),
        (init_management_review_store, str(ISO_DATA_DIR)),
        (init_notification_store, str(ISO_DATA_DIR)),
        (init_soa_store, str(ISO_DATA_DIR)),
        (init_compliance_calendar_store, str(ISO_DATA_DIR)),
        (init_auth_secret, str(ISO_DATA_DIR)),
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
            init_auth_store(str(ISO_DATA_DIR))
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
        from compliance_calendar.framework_milestones import sync_iso_milestones
        sync_iso_milestones({})
    except Exception as e:
        print(f"[startup] ISO milestone sync failed: {e}", file=sys.stderr)

    async with lifespan_scheduler():
        yield


app = FastAPI(title="Khestra ISO 27001", lifespan=_lifespan, docs_url=None, redoc_url=None, openapi_url=None)


class StripFrameworkPrefixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/api/iso27001/"):
                scope["path"] = path.replace("/api/iso27001/", "/api/", 1)
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
    "/api/collectors/",
    "/api/demo/",
    "/api/audit-log",
    "/api/evidence",
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
        from audit_log.store import log_event
        log_event(
            action=request.method.lower(),
            resource_type=path.split("/")[2] if len(path.split("/")) > 2 else "unknown",
            framework_id="ISO 27001",
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


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": "khestra-iso27001",
        "framework": FRAMEWORK_ID,
        "demo_api_enabled": demo_api_enabled(),
    }


@app.post("/api/iso/demo/load")
def post_iso_demo_load() -> Dict[str, Any]:
    if not demo_api_enabled():
        raise HTTPException(403, "Demo workspaces are disabled in this environment")
    return load_iso_demo()


def _ws_role() -> str:
    try:
        user = get_auth_user()
        if user:
            return user.role
    except Exception:
        pass
    return "Assessor"


def _require_edit_controls() -> None:
    if not can_edit_controls(_ws_role()):
        raise HTTPException(403, "Your role does not have permission to edit controls")


def _require_export() -> None:
    if not can_export(_ws_role()):
        raise HTTPException(403, "Your role does not have permission to export data")


class CollectorCredentialsBody(BaseModel):
    credentials: Dict[str, str] = Field(default_factory=dict)


class CollectorRunBody(BaseModel):
    use_fixture: bool = False
    attach: bool = True
    control_ids: Optional[list[str]] = None


class CollectorScheduleBody(BaseModel):
    enabled: Optional[bool] = None
    interval: Optional[str] = None
    attach_on_run: Optional[bool] = None


class RunDueBody(BaseModel):
    use_fixture_if_unconfigured: bool = False


@app.get("/api/dashboard")
def dashboard() -> Dict[str, Any]:
    rl = rollup()
    applicable = max(rl.get("applicable_total", 0), 1)
    implemented = rl.get("counts", {}).get("implemented", 0)
    readiness_pct = round(implemented / applicable * 100, 1)
    implementation_pct = round(
        (implemented + rl.get("counts", {}).get("partially implemented", 0)) / applicable * 100, 1
    )
    tests_total = sum(1 for t in list_tests() if (t.get("framework") or "") == FRAMEWORK_ID)
    evidence = list_evidence(framework_id=FRAMEWORK_ID)
    evidence_linked = sum(1 for e in evidence if (e.get("mappings") or []))
    return {
        "org_name": ORG_NAME,
        "readiness_pct": readiness_pct,
        "implementation_pct": implementation_pct,
        "rollup": rl,
        "tests_total": tests_total,
        "evidence_total": len(evidence),
        "evidence_linked": evidence_linked,
        "framework": FRAMEWORK_ID,
    }


@app.get("/api/settings")
def settings() -> Dict[str, Any]:
    user = get_auth_user()
    cfg = public_auth_config()
    role = user.role if user else "Assessor"
    return {
        "org_name": ORG_NAME,
        "current_role": role,
        "current_user_name": user.name if user else "",
        "capabilities": {"edit_controls": can_edit_controls(role), "view_dashboard": True},
        "status_options": ["implemented", "partially implemented", "not implemented", "excluded"],
        "operating_status_options": ["Active", "Degraded", "Retired"],
        "user_roles": ["Assessor", "Auditor", "User", "Externals"],
        "is_demo": False,
        "demo_id": "",
        "workspace_locked": False,
        "auth_enabled": cfg["enabled"],
        "auth_role_locked": cfg["role_locked"],
        "auth_user_email": user.email if user else "",
    }


@app.get("/api/soa")
def soa_list() -> dict:
    sync_soa_from_risks()
    return {"rows": list_soa(), "rollup": rollup()}


@app.get("/api/soa/evidence-guidance")
def soa_evidence_guidance_all() -> dict:
    return {"guidance": EVIDENCE_GUIDANCE}


@app.get("/api/soa/evidence-guidance/{control_id}")
def soa_evidence_guidance(control_id: str) -> dict:
    return {"control_id": control_id, "guidance": guidance_for(control_id)}


@app.patch("/api/soa/{control_id}")
def soa_update(control_id: str, data: dict | None = None) -> dict:
    _require_edit_controls()
    fields = data or {}
    try:
        control = update_control(control_id, fields)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    if not control:
        raise HTTPException(404, "Control not found")
    return {"control": control}


@app.get("/api/soa/export.csv")
def soa_export() -> Response:
    _require_export()
    csv_data = export_csv()
    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="iso27001_soa.csv"'},
    )


@app.get("/api/soa/export.xlsx")
def soa_export_xlsx() -> Response:
    _require_export()
    return Response(
        content=export_xlsx(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="iso27001_soa.xlsx"'},
    )


@app.get("/api/soa/export.docx")
def soa_export_docx() -> Response:
    _require_export()
    return Response(
        content=export_docx(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="iso27001_soa.docx"'},
    )


@app.post("/api/soa/sync-from-risks")
def soa_sync_from_risks() -> dict:
    _require_edit_controls()
    return sync_soa_from_risks()


@app.get("/api/iso/risk-report.docx")
def iso_risk_report_docx() -> Response:
    _require_export()
    return Response(
        content=export_risk_report_docx(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="iso27001_risk_assessment_report.docx"'},
    )


@app.get("/api/iso/risk-report.xlsx")
def iso_risk_report_xlsx() -> Response:
    _require_export()
    return Response(
        content=export_risk_report_xlsx(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="iso27001_risk_register.xlsx"'},
    )


@app.get("/api/iso/audit-report.docx")
def iso_audit_report_docx() -> Response:
    _require_export()
    return Response(
        content=export_internal_audit_report_docx(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="iso27001_internal_audit_report.docx"'},
    )


@app.get("/api/iso/management-review.docx")
def iso_management_review_docx() -> Response:
    _require_export()
    return Response(
        content=export_management_review_minutes_docx(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="iso27001_management_review_minutes.docx"'},
    )


@app.get("/api/iso/nc-capa.xlsx")
def iso_nc_capa_xlsx() -> Response:
    _require_export()
    return Response(
        content=export_nc_capa_xlsx(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="iso27001_nc_capa_register.xlsx"'},
    )


@app.get("/api/iso/auditor-pack.zip")
def iso_auditor_pack_zip() -> Response:
    _require_export()
    return Response(
        content=export_auditor_pack_zip(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="iso27001_auditor_pack.zip"'},
    )


@app.get("/api/soa/{control_id}")
def soa_get(control_id: str) -> dict:
    control = get_control(control_id)
    if not control:
        raise HTTPException(404, "Control not found")
    control["linked_risks"] = linked_risks(control_id)
    return {"control": control}


# ── Collector integration endpoints (shared engine, ISO 27001 wiring) ──


@app.get("/api/collectors")
def get_collectors() -> Dict[str, Any]:
    return {
        "connectors": list_connectors(),
        "monitoring": monitoring_summary(),
        "drift_events": get_events(limit=25),
        "recent_runs": recent_runs(),
    }


@app.get("/api/collectors/monitoring/events")
def get_collector_drift_events(
    connector_id: Optional[str] = Query(None),
    limit: int = Query(30, ge=1, le=100),
) -> Dict[str, Any]:
    return {"events": get_events(limit=limit, connector_id=connector_id)}


@app.get("/api/collectors/health")
def get_collector_health() -> Dict[str, Any]:
    try:
        from collectors.monitor_store import read_scheduler_heartbeat
        return {"scheduler": read_scheduler_heartbeat(), "status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


@app.post("/api/collectors/monitoring/run-due")
def post_run_due_collectors(body: RunDueBody) -> Dict[str, Any]:
    _require_edit_controls()
    try:
        return run_due_connectors(
            use_fixture_if_unconfigured=body.use_fixture_if_unconfigured,
        )
    except Exception as exc:
        raise HTTPException(500, f"Scheduled run failed: {exc}") from exc


@app.patch("/api/collectors/{connector_id}/schedule")
def patch_collector_schedule(connector_id: str, body: CollectorScheduleBody) -> Dict[str, Any]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    if body.interval is not None and body.interval not in ("manual", "daily", "weekly"):
        raise HTTPException(400, "interval must be manual, daily, or weekly")
    _require_edit_controls()
    state = patch_monitor_schedule(
        connector_id,
        enabled=body.enabled,
        interval=body.interval,  # type: ignore[arg-type]
        attach_on_run=body.attach_on_run,
    )
    return state.to_dict()


# Shared collectors router (mappings, posture) must register before the
# app-level /api/collectors/{connector_id} catch-all route below.
if COLLECTORS_AVAILABLE:
    app.include_router(collectors_router)


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
    _require_edit_controls()
    save_credentials(connector_id, creds)
    return credentials_status(connector_id, meta["required_fields"])


@app.delete("/api/collectors/{connector_id}/credentials")
def remove_collector_credentials(connector_id: str) -> Dict[str, str]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    _require_edit_controls()
    delete_credentials(connector_id)
    return {"status": "deleted"}


@app.post("/api/collectors/{connector_id}/run")
def post_collector_run(connector_id: str, body: CollectorRunBody) -> Dict[str, Any]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    _require_edit_controls()
    try:
        if body.attach:
            result = run_and_attach(
                connector_id,
                use_fixture=body.use_fixture,
                control_ids=body.control_ids,
            )
            return {
                "run": result.run.to_dict(),
                "attached": [a.to_dict() for a in result.attached],
                "monitor_run_id": result.monitor_run_id,
                "drift_events": result.drift_events,
            }
        run = run_collector(connector_id, use_fixture=body.use_fixture)
        return {"run": run.to_dict(), "attached": [], "monitor_run_id": run.monitor_run_id, "drift_events": run.drift_events}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"Collector run failed: {exc}") from exc


app.include_router(audit_router)
app.include_router(testing_router)
app.include_router(auth_router)
