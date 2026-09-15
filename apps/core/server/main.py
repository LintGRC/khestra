"""Khestra Global service — the single home for all cross-framework services.

Serves the neutral `/api` surface: collectors (catalog, run, import,
schedules, monitoring), posture, the Evidence Hub, and every shared
workspace entity (personnel, policies, risks, assets, vendors, incidents,
audit log, trust center, compliance calendar, effectiveness, control tests)
plus the shared auth routes. No framework-specific logic — frameworks are
just consumers (via CMMC_FRAMEWORK-independent CHECK_TO_FRAMEWORKS
mappings) that keep their own domain routes on their own services.
"""

from __future__ import annotations

import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from security_headers.ratelimit import add_rate_limiting
from security_headers.security import add_security_headers
from pydantic import BaseModel

PLATFORM = Path(__file__).resolve().parents[1]
CORE = PLATFORM / "server"
PACKAGES = Path(__file__).resolve().parents[3] / "packages"
if str(PACKAGES) not in sys.path:
    sys.path.insert(0, str(PACKAGES))
if str(PACKAGES / "evidence") not in sys.path:
    sys.path.insert(0, str(PACKAGES / "evidence"))
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from kevidence.config import configure as configure_evidence  # noqa: E402
from kevidence.availability import collectors_available

if collectors_available():
    from collectors.credentials_store import (  # noqa: E402
        credentials_status,
        delete_credentials,
        save_credentials,
    )
    from collectors.monitor_store import (  # noqa: E402
        get_events,
        get_monitor_states,
        get_run_records,
        patch_monitor_schedule,
        read_scheduler_heartbeat,
        save_monitor_state,
    )
    from collectors.registry import CONNECTOR_CATALOG, list_connectors  # noqa: E402
    from collectors.routes import router as collectors_router  # noqa: E402
    from collectors.scheduler_config import scheduler_token_matches  # noqa: E402
    COLLECTORS_AVAILABLE = True
else:
    COLLECTORS_AVAILABLE = False

    class _MockRun:
        def to_dict(self):
            return {"status": "unavailable"}
        status = "unavailable"

    class _MockResult:
        run = _MockRun()
        attached = []
        drift_events = []

    CONNECTOR_CATALOG = {}
    list_connectors = lambda: []
    credentials_status = lambda connector_id, fields: {"connector_id": connector_id, "configured": False}
    save_credentials = lambda *a, **k: None
    delete_credentials = lambda *a, **k: None
    get_events = lambda limit=0: []
    get_monitor_states = lambda: []
    get_run_records = lambda *a, **k: []
    patch_monitor_schedule = lambda connector_id, **k: {"connector_id": connector_id}
    read_scheduler_heartbeat = lambda: {}
    save_monitor_state = lambda *a, **k: None
    run_and_attach_core = lambda connector_id, **kw: (_MockRun(), [], [])
    collectors_state_dir = lambda: None
from evidence_hub.routes import router as evidence_hub_router  # noqa: E402

from core_auth import core_auth_middleware  # noqa: E402
if COLLECTORS_AVAILABLE:
    from attach import run_and_attach_core  # noqa: E402

# Global workspace entities (merged from the platform app — one home for
# every shared router: personnel, policies, risks, assets, vendors, ...).
from personnel.routes import router as personnel_router  # noqa: E402
from personnel.store import init_store as init_personnel_store  # noqa: E402
from evidence_hub.store import init_store as init_evidence_hub_store  # noqa: E402
from policies.routes import router as policies_router  # noqa: E402
from policies.store import init_store as init_policies_store  # noqa: E402
from auth.jwt import init_secret as init_auth_secret  # noqa: E402
from auth.store import init_store as init_auth_store  # noqa: E402
from auth_routes import router as auth_router  # noqa: E402
from trust_center import router as trust_center_router  # noqa: E402
from compliance_calendar.routes import router as compliance_calendar_router  # noqa: E402
from effectiveness.routes import router as effectiveness_router  # noqa: E402
from control_tests.routes import router as control_tests_router  # noqa: E402
from ccf.routes import router as ccf_router  # noqa: E402
from remediation.routes import router as remediation_router  # noqa: E402
from orgs.routes import router as orgs_router  # noqa: E402
from raci.routes import router as raci_router  # noqa: E402
from exceptions.routes import router as exceptions_router  # noqa: E402
from findings.routes import router as findings_router  # noqa: E402
from audit_center.routes import router as audit_center_router  # noqa: E402
from training.routes import router as training_router  # noqa: E402
from reviews.routes import router as reviews_router  # noqa: E402
from org_context.routes import router as org_context_router  # noqa: E402
from management_review.routes import router as management_review_router  # noqa: E402
from notifications.routes import router as notifications_router  # noqa: E402

DATA_DIR = Path(os.environ.get("CORE_DATA_DIR") or (PLATFORM / "data"))
PLATFORM_ROOT = Path(os.environ.get("CORE_PLATFORM_ROOT") or (PLATFORM.parents[1] / "apps" / "cmmc"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# JWT signing secret — shared identity: CMMC_AUTH_SECRET env, or the
# auth_secret file next to the shared AUTH_DB_PATH.
try:
    init_auth_secret(str(DATA_DIR))
except Exception as exc:  # pragma: no cover
    print(f"[global] auth secret init skipped: {exc}")

configure_evidence(data_dir=DATA_DIR, platform_root=PLATFORM_ROOT)


@asynccontextmanager
async def _lifespan(_app: FastAPI):

    try:
        from auth.deploy_guard import assert_safe_auth_posture
        assert_safe_auth_posture()
    except RuntimeError as e:
        print(f"[startup] AUTH POSTURE REFUSAL: {e}", file=sys.stderr)
        raise
    from risks.store import init_store as init_risks_store
    from notifications.store import init_store as init_notification_store
    from control_tests.store import init_store as init_control_tests_store
    from orgs.store import init_store as init_orgs_store
    from raci.store import init_store as init_raci_store
    from exceptions.store import init_store as init_exception_store
    from findings.store import init_store as init_findings_store
    from audit_center.store import init_store as init_audit_center_store
    from training.store import init_store as init_training_store
    from reviews.store import init_store as init_reviews_store
    from org_context.store import init_store as init_org_context_store
    from management_review.store import init_store as init_management_review_store
    from remediation.routes import init_store as init_remediation_store
    from compliance_calendar.store import init_store as init_compliance_calendar_store

    for _init_fn, _path in [
        (init_personnel_store, str(DATA_DIR)),
        (init_evidence_hub_store, str(DATA_DIR)),
        (init_policies_store, str(DATA_DIR)),
        (init_risks_store, str(DATA_DIR)),
        (init_control_tests_store, str(DATA_DIR)),
        (init_notification_store, str(DATA_DIR)),
        (init_auth_store, str(DATA_DIR)),
        (init_orgs_store, str(DATA_DIR)),
        (init_raci_store, str(DATA_DIR)),
        (init_exception_store, str(DATA_DIR)),
        (init_findings_store, str(DATA_DIR)),
        (init_audit_center_store, str(DATA_DIR)),
        (init_training_store, str(DATA_DIR)),
        (init_reviews_store, str(DATA_DIR)),
        (init_org_context_store, str(DATA_DIR)),
        (init_management_review_store, str(DATA_DIR)),
        (init_remediation_store, str(DATA_DIR)),
        (init_compliance_calendar_store, str(DATA_DIR)),
    ]:
        try:
            _init_fn(_path)
        except Exception as e:
            print(f"[global] {_init_fn.__name__} failed: {e}", file=sys.stderr)

    try:
        from compliance_calendar.sweep import run_reminder_sweep
        outcome = run_reminder_sweep(window_days=7)
        if outcome.get("created"):
            print(f"[startup] compliance reminders: {outcome['created']} new", file=sys.stderr)
    except Exception as e:
        print(f"[startup] compliance reminder sweep failed: {e}", file=sys.stderr)

    yield


def _allowed_cors_origins() -> list[str]:
    """CORS allowlist from CMMC_ALLOWED_ORIGINS; common dev origins when unset."""
    raw = os.environ.get("CMMC_ALLOWED_ORIGINS", "").strip()
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return ["http://localhost:5173", "http://127.0.0.1:5173"]


app = FastAPI(title="Khestra Global", version="0.1.0", lifespan=_lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)
add_security_headers(app)
add_rate_limiting(app)

app.middleware("http")(core_auth_middleware)


class RunDueBody(BaseModel):
    use_fixture_if_unconfigured: bool = False


class CollectorScheduleBody(BaseModel):
    enabled: Optional[bool] = None
    interval: Optional[str] = None
    attach_on_run: Optional[bool] = None


class CollectorRunBody(BaseModel):
    use_fixture: bool = False
    attach: bool = True
    control_ids: Optional[List[str]] = None


class CollectorCredentialsBody(BaseModel):
    credentials: Dict[str, str]


def _bearer_token(request: Request) -> str | None:
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


def _audit_log(action: str, resource_type: str, resource_id: str = "", details: Optional[Dict[str, Any]] = None) -> None:
    try:
        from audit_log.store import log_event
        user = getattr(getattr(app, "state", None), "user", None)
        log_event(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=(user or {}).get("id", ""),
            details=details or {},
        )
    except Exception as exc:
        print(f"[core] audit log failed: {exc}")


def _clear_last_error(connector_id: str) -> None:
    try:
        state = get_monitor_states([connector_id])[0]
        if state.last_error is not None:
            state.last_error = None
            save_monitor_state(state)
    except Exception:
        pass


def _use_fixture(body_use_fixture: bool) -> bool:
    return body_use_fixture or os.environ.get("DEMO_MODE", "") == "1"


# ── Collectors ────────────────────────────────────────────────────────────


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "core"}


@app.get("/api/collectors")
def get_collectors() -> Dict[str, Any]:
    return {
        "connectors": list_connectors(),
        "monitoring": _monitoring_summary(),
        "drift_events": get_events(limit=25),
        "freshness": {},
        "recent_runs": _recent_runs(),
    }


def _monitoring_summary() -> Dict[str, Any]:
    ids = list(CONNECTOR_CATALOG.keys())
    states = get_monitor_states(ids)
    due = [s.connector_id for s in states if s.enabled and s.interval != "manual" and not s.last_run_at]
    return {
        "connectors": [s.to_dict() for s in states],
        "due_connectors": due,
        "recent_runs": get_run_records(limit=15),
    }


def _recent_runs() -> List[Dict[str, Any]]:
    from collectors.engine import recent_runs
    return recent_runs(limit=10)


@app.get("/api/collectors/monitoring/events")
def get_collector_drift_events(
    connector_id: Optional[str] = Query(None),
    limit: int = Query(30, ge=1, le=100),
) -> Dict[str, Any]:
    return {"events": get_events(limit=limit, connector_id=connector_id)}


@app.get("/api/collectors/monitoring/scheduler-status")
def get_scheduler_status() -> Dict[str, Any]:
    return read_scheduler_heartbeat()


@app.post("/api/collectors/monitoring/run-due")
def post_run_due_collectors(request: Request, body: RunDueBody) -> Dict[str, Any]:
    if not scheduler_token_matches(_bearer_token(request)):
        raise HTTPException(403, "Scheduler token required")
    from scheduler import run_due_connectors as run_due_core
    try:
        return run_due_core(use_fixture_if_unconfigured=body.use_fixture_if_unconfigured)
    except Exception as exc:
        raise HTTPException(500, f"Scheduled run failed: {exc}") from exc


@app.patch("/api/collectors/{connector_id}/schedule")
def patch_collector_schedule(connector_id: str, body: CollectorScheduleBody) -> Dict[str, Any]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    if body.interval is not None and body.interval not in ("manual", "daily", "weekly"):
        raise HTTPException(400, "interval must be manual, daily, or weekly")
    state = patch_monitor_schedule(
        connector_id,
        enabled=body.enabled,
        interval=body.interval,  # type: ignore[arg-type]
        attach_on_run=body.attach_on_run,
    )
    _audit_log("updated", "schedule", connector_id, {"enabled": body.enabled, "interval": body.interval})
    return state.to_dict()


if COLLECTORS_AVAILABLE:
    app.include_router(collectors_router)
else:
    # Manual posture endpoint — serves posture from evidence hub when collectors
    # are not installed (free-tier posture path, D9).
    from kevidence.manual_posture import build_manual_posture

    @app.get("/api/posture")
    def get_manual_posture(framework: str = Query(...)) -> Dict[str, Any]:
        """Compute posture from approved manual evidence in the Evidence Hub."""
        from evidence_hub.store import list_evidence, canonical_framework_id

        fw = canonical_framework_id(framework)
        evidence_items = list_evidence(framework_id=fw, view="latest")

        # Group by control_id
        by_control: Dict[str, List[Dict[str, Any]]] = {}
        for item in evidence_items:
            mappings = item.get("mappings", [])
            for m in mappings:
                cid = m.get("control_id", "")
                if cid:
                    by_control.setdefault(cid, []).append(item)

        return build_manual_posture(framework, by_control)


# ── Global entities (shared by all frameworks) ────────────────────────────

from risks.routes import router as risks_router  # noqa: E402
from assets.routes import router as assets_router  # noqa: E402
from vendors.routes import router as vendors_router  # noqa: E402
from incidents.routes import router as incidents_router  # noqa: E402

app.include_router(policies_router)
app.include_router(risks_router)
app.include_router(assets_router)
app.include_router(vendors_router)
app.include_router(incidents_router)

from audit_log.routes import router as audit_log_router  # noqa: E402
app.include_router(audit_log_router)

# Workspace services merged from the former platform app.
app.include_router(personnel_router)
app.include_router(trust_center_router)
app.include_router(compliance_calendar_router)
app.include_router(effectiveness_router)
app.include_router(control_tests_router)
app.include_router(auth_router)

# Remaining global workspace routers (one home, stripped from framework apps).
app.include_router(ccf_router)
app.include_router(remediation_router)
app.include_router(orgs_router)
app.include_router(raci_router)
app.include_router(exceptions_router)
app.include_router(findings_router)
app.include_router(audit_center_router)
app.include_router(training_router)
app.include_router(reviews_router)
app.include_router(org_context_router)
app.include_router(management_review_router)
app.include_router(notifications_router)


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
    save_credentials(connector_id, creds)
    _audit_log("saved", "credentials", connector_id)
    return credentials_status(connector_id, meta["required_fields"])


@app.delete("/api/collectors/{connector_id}/credentials")
def remove_collector_credentials(connector_id: str) -> Dict[str, str]:
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    delete_credentials(connector_id)
    _audit_log("deleted", "credentials", connector_id)
    return {"status": "deleted"}


@app.post("/api/collectors/{connector_id}/run")
def post_collector_run(connector_id: str, body: CollectorRunBody) -> Dict[str, Any]:
    meta = CONNECTOR_CATALOG.get(connector_id) or {}
    if meta.get("import_only"):
        raise HTTPException(400, f"Connector '{connector_id}' is an import connector — use POST /api/collectors/{connector_id}/import")
    use_fixture = _use_fixture(body.use_fixture)
    try:
        if body.attach:
            run, attached = run_and_attach_core(connector_id, use_fixture=use_fixture)
            _audit_log("run", "connector", connector_id, {"fixture": use_fixture, "attached": True})
            _clear_last_error(connector_id)
            return {"run": run.to_dict(), "attached": attached, "monitor_run_id": run.monitor_run_id, "drift_events": run.drift_events}
        from collectors.engine import run_collector
        run = run_collector(connector_id, use_fixture=use_fixture)
        _audit_log("run", "connector", connector_id, {"fixture": use_fixture, "attached": False})
        _clear_last_error(connector_id)
        return {"run": run.to_dict(), "attached": [], "monitor_run_id": run.monitor_run_id, "drift_events": run.drift_events}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"Collector failed: {exc}") from exc


@app.post("/api/collectors/{connector_id}/import")
def post_collector_import(connector_id: str, file: UploadFile = File(...)) -> Dict[str, Any]:
    """Import external scanner output (Prowler / ScubaGear / GRC finding JSON)."""
    from collectors.config import collectors_state_dir

    meta = CONNECTOR_CATALOG.get(connector_id)
    if not meta or not meta.get("import_only"):
        raise HTTPException(400, f"Connector '{connector_id}' does not support imports")

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

    try:
        for stale in sorted(imports_dir.glob(f"{connector_id}_*.json"))[:-20]:
            stale.unlink(missing_ok=True)
    except OSError:
        pass

    try:
        run, attached = run_and_attach_core(connector_id, creds_override={"import_file": str(path)})
        _audit_log("import", "connector", connector_id, {"file": path.name, "checks": len(run.checks)})
        _clear_last_error(connector_id)
        return {"run": run.to_dict(), "attached": attached, "monitor_run_id": run.monitor_run_id, "drift_events": run.drift_events}
    except Exception as exc:
        raise HTTPException(500, f"Import failed: {exc}") from exc


# ── Evidence Hub ──────────────────────────────────────────────────────────

app.include_router(evidence_hub_router)
