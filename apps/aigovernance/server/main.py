from typing import Any, Dict, Optional
import os, json, csv, io, sys
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from security_headers.ratelimit import add_rate_limiting
from security_headers.security import add_security_headers
from dotenv import load_dotenv
from fastapi.responses import Response
from pydantic import BaseModel

# ─── Shared packages setup ────────────────────────────
PLATFORM = Path(__file__).resolve().parents[1]
SERVER = Path(__file__).resolve().parent
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))
CORE = PLATFORM / "core"
PACKAGES = PLATFORM / "packages"
if not PACKAGES.is_dir():
    PACKAGES = PLATFORM.parents[1] / "packages"  # local dev: khestra/
EVIDENCE = PACKAGES / "evidence"
for path in (PACKAGES, EVIDENCE, CORE):
    p = str(path)
    if p not in sys.path:
        sys.path.insert(0, p)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
if str(PACKAGES) in sys.path:
    sys.path.remove(str(PACKAGES))
    sys.path.insert(0, str(PACKAGES))

from kevidence.config import configure as configure_evidence  # noqa: E402
configure_evidence(
    data_dir=PLATFORM / "data",
    platform_root=PLATFORM,
)

from auth.jwt import init_secret as init_auth_secret  # noqa: E402
from auth.store import init_store as init_auth_store  # noqa: E402
from aigov_auth import aigov_auth_middleware  # noqa: E402

from ccf.routes import router as ccf_router  # noqa: E402
from remediation.routes import router as remediation_router  # noqa: E402
from remediation.routes import init_store as init_remediation_store  # noqa: E402
from policies.routes import router as policy_router  # noqa: E402
from policies.store import init_store as init_policy_store  # noqa: E402
from policies.store import add_builtin_templates  # noqa: E402
from policies.store import create_document  # noqa: E402
from orgs.routes import router as orgs_router  # noqa: E402
from orgs.store import init_store as init_orgs_store  # noqa: E402
from raci.routes import router as raci_router  # noqa: E402
from raci.store import init_store as init_raci_store  # noqa: E402
from vendors.store import init_store as init_vendor_store  # noqa: E402
from audit.routes import router as audit_router  # noqa: E402
from audit.store import init_store as init_audit_store  # noqa: E402
from risks.routes import router as risks_router  # noqa: E402
from risks.store import init_store as init_risks_store  # noqa: E402
from testing.routes import router as testing_router  # noqa: E402
from testing.store import init_store as init_testing_store  # noqa: E402
from findings.routes import router as findings_router  # noqa: E402
from findings.store import init_store as init_findings_store  # noqa: E402
from audit_center.routes import router as audit_center_router  # noqa: E402
from audit_center.store import init_store as init_audit_center_store  # noqa: E402
from training.routes import router as training_router  # noqa: E402
from training.store import init_store as init_training_store  # noqa: E402
from personnel.routes import router as personnel_router  # noqa: E402
from compliance_calendar.routes import router as compliance_calendar_router  # noqa: E402
from effectiveness.routes import router as effectiveness_router  # noqa: E402
from control_tests.routes import router as control_tests_router  # noqa: E402
from control_tests.store import init_store as init_control_tests_store  # noqa: E402
from personnel.store import init_store as init_personnel_store  # noqa: E402
from assets.routes import router as assets_router  # noqa: E402
from assets.store import init_store as init_assets_store  # noqa: E402
from audit_log.store import init_store as init_audit_log_store, list_events, log_event, export_events_csv  # noqa: E402
from compliance_calendar.store import init_store as init_compliance_calendar_store  # noqa: E402
from evidence_hub.routes import router as evidence_hub_router  # noqa: E402
from evidence_hub.store import init_store as init_evidence_hub_store  # noqa: E402
from incidents.routes import router as incidents_router  # noqa: E402
from incidents.store import init_store as init_incidents_store  # noqa: E402
from permissions_api import can_edit_controls, can_edit_org, can_export, role_capabilities  # noqa: E402
from guidance.objectives_data import AI_GENERATED_CONTROL_OBJECTIVES  # noqa: E402
from conformity_routes import FRAMEWORKS, gap_analysis_rows  # noqa: E402

# ─── Collector integration ──────────────────────────────
from kevidence.availability import collectors_available

if collectors_available():
    import aigovernance_collectors  # noqa: F401,E402 — register AI control mapping
    from aigovernance_collectors.attach import run_and_attach_ai  # noqa: E402
    from collectors.routes import router as collectors_router  # noqa: E402
    from collectors.credentials_store import credentials_status, delete_credentials, save_credentials  # noqa: E402
    from collectors.engine import recent_runs, run_collector as run_collector_engine  # noqa: E402
    from collectors.monitor_store import get_events, patch_monitor_schedule  # noqa: E402
    from collectors.registry import CONNECTOR_CATALOG, list_connectors  # noqa: E402
else:
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
    recent_runs = lambda: []
    get_events = lambda limit=0: []
    credentials_status = lambda connector_id, fields: {"connector_id": connector_id, "configured": False, "fields_missing": fields}
    save_credentials = lambda *a, **k: None
    patch_monitor_schedule = lambda connector_id, **k: {"connector_id": connector_id, "enabled": False, "interval": "manual"}
    run_collector_engine = lambda connector_id, use_fixture=False: _MockRun()
    run_and_attach_ai = lambda connector_id, use_fixture=False: _MockResult()

from conformity_routes import router as conformity_router
from fria_routes import router as fria_router
from vendors.routes import router as shared_vendor_router
from vendors.store import init_store as init_shared_vendor_store, DB_PATH as SHARED_VENDOR_DB_PATH
from vendor_routes import router as vendor_intake_router
from tabletop.routes import router as tabletop_router
from tabletop.store import init_store as init_tabletop_store
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False


@asynccontextmanager
async def _lifespan(_app: FastAPI):

    try:
        from auth.deploy_guard import assert_safe_auth_posture
        assert_safe_auth_posture()
    except RuntimeError as e:
        print(f"[startup] AUTH POSTURE REFUSAL: {e}", file=sys.stderr)
        raise
    for _init_fn, _path in [
        (init_remediation_store, str(PLATFORM / "data")),
        (init_policy_store, str(PLATFORM / "data")),
        (init_orgs_store, str(PLATFORM / "data")),
        (init_raci_store, str(PLATFORM / "data")),
        (init_vendor_store, str(PLATFORM / "data")),
        (init_audit_store, str(PLATFORM / "data")),
        (init_risks_store, str(PLATFORM / "data")),
        (init_control_tests_store, str(PLATFORM / "data")),
        (init_testing_store, str(PLATFORM / "data")),
        (init_findings_store, str(PLATFORM / "data")),
        (init_audit_center_store, str(PLATFORM / "data")),
        (init_training_store, str(PLATFORM / "data")),
        (init_personnel_store, str(PLATFORM / "data")),
        (init_assets_store, str(PLATFORM / "data")),
        (init_audit_log_store, str(PLATFORM / "data")),
        (init_compliance_calendar_store, str(PLATFORM / "data")),
        (init_evidence_hub_store, str(PLATFORM / "data")),
        (init_incidents_store, str(PLATFORM / "data")),
        (init_auth_secret, str(PLATFORM / "data")),
        (init_auth_store, str(PLATFORM / "data")),
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
        from incidents.store import migrate_from_json
        migrate_from_json(str(PLATFORM / "data" / "incidents.json"))
    except Exception:
        pass
    try:
        init_tabletop_store(str(PLATFORM / "data"))
    except Exception as e:
        print(f"[lifespan] init_tabletop_store failed: {e}", file=sys.stderr)
    os.environ["VENDOR_DB_PATH"] = str(PLATFORM / "data" / "vendors.db")
    try:
        init_shared_vendor_store(str(PLATFORM / "data"))
    except Exception as e:
        print(f"[lifespan] init_shared_vendor_store failed: {e}", file=sys.stderr)

    try:
        from compliance_calendar.sweep import run_reminder_sweep
        outcome = run_reminder_sweep(window_days=7)
        if outcome.get("created"):
            print(f"[startup] compliance reminders: {outcome['created']} new", file=sys.stderr)
    except Exception as e:
        print(f"[startup] compliance reminder sweep failed: {e}", file=sys.stderr)

    try:
        from compliance_calendar.framework_milestones import sync_aigov_milestones
        for system in (_load("systems") or {}).values():
            sync_aigov_milestones(system)
    except Exception as e:
        print(f"[startup] AIGov milestone sync failed: {e}", file=sys.stderr)

    yield


app = FastAPI(title="AI Governance API", lifespan=_lifespan, docs_url=None, redoc_url=None, openapi_url=None)


class StripFrameworkPrefixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/api/ai-governance/"):
                scope["path"] = path.replace("/api/ai-governance/", "/api/", 1)
        await self.app(scope, receive, send)


def _allowed_cors_origins() -> list[str]:
    """CORS allowlist from CMMC_ALLOWED_ORIGINS; common dev origins when unset."""
    raw = os.environ.get("CMMC_ALLOWED_ORIGINS", "").strip()
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return ["http://localhost:5173", "http://127.0.0.1:5173"]


app.add_middleware(StripFrameworkPrefixMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)
add_security_headers(app)
add_rate_limiting(app)

app.include_router(vendor_intake_router)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVIDENCE_DIR = os.path.join(DATA_DIR, "evidence")
CONTRACT_FILES_DIR = os.path.join(DATA_DIR, "contract_files")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(CONTRACT_FILES_DIR, exist_ok=True)

# ─── Helpers ──────────────────────────────────────────

def _load(name: str) -> dict:
    p = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(p):
        return {}
    try:
        with open(p) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"WARNING: Corrupt state file {p}, returning empty", file=sys.stderr)
        return {}

def _save(name: str, data: dict):
    p = os.path.join(DATA_DIR, f"{name}.json")
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, p)

def _id() -> str:
    return uuid4().hex[:12]

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ws_role() -> str:
    try:
        from entra_auth import auth_enabled, get_auth_user
        user = get_auth_user()
        if user and auth_enabled():
            return user.role
    except ImportError:
        pass
    return "Assessor"


def _require_edit_controls() -> None:
    role = _ws_role()
    if not can_edit_controls(role):
        raise HTTPException(403, "Your role does not have permission to edit controls")


def _require_edit_org() -> None:
    role = _ws_role()
    if not can_edit_org(role):
        raise HTTPException(403, "Your role does not have permission to edit organization data")


def _require_export() -> None:
    role = _ws_role()
    if not can_export(role):
        raise HTTPException(403, "Your role does not have permission to export data")


ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".png", ".jpg", ".jpeg", ".txt", ".md", ".json", ".log"}
MAX_EVIDENCE_MB = 50


def _audit_log(
    action: str,
    resource_type: str,
    resource_id: str = "",
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
    outcome: str = "success",
) -> None:
    try:
        ip = request.client.host if request and request.client else ""
        ua = request.headers.get("user-agent", "") if request else ""
        log_event(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            framework_id="AIGov",
            user_id="",
            user_email="",
            ip_address=ip,
            user_agent=ua,
            details=details,
            outcome=outcome,
        )
    except Exception:
        pass

# ─── Pydantic ─────────────────────────────────────────

class SystemCreate(BaseModel):
    name: str
    description: str = ""
    risk_classification: str = "unclassified"
    owner: str = ""
    business_owner: str = ""
    technical_owner: str = ""
    risk_owner: str = ""
    vendor: str = ""
    foundation_model: str = ""
    deployment_status: str = "development"
    environment: str = "development"
    purpose: str = ""
    framework: str = ""
    tags: list[str] = []
    version: str = "1.0.0"
    review_date: str = ""
    review_owner: str = ""
    approval_status: str = "draft"
    evidence_links: list[dict] = []
    is_public_facing: bool = False
    transparency_notice_url: str = ""
    input_data_sources: str = ""
    processing_location: str = ""
    output_destinations: str = ""
    performance_metrics: str = ""
    known_limitations: str = ""
    out_of_scope_uses: str = ""
    human_oversight: str = ""
    bias_fairness_notes: str = ""
    training_data: str = ""
    is_fine_tuned: bool = False
    ai_profile: str = "provider"

class ReviewCycleCreate(BaseModel):
    label: str
    start: str = ""
    end: str = ""

class EvaluationCreate(BaseModel):
    name: str
    system_id: str = ""
    system_name: str = ""
    evaluation_type: str = "accuracy"
    status: str = "planned"
    methodology: str = ""
    criteria: str = ""
    results: str = ""
    score: float = 0.0
    tester: str = ""
    test_date: str = ""
    reviewer: str = ""
    review_date: str = ""
    notes: str = ""
    evidence_ids: list[str] = []
    control_ids: list[str] = []

class TrainingDatasetCreate(BaseModel):
    name: str
    system_id: str = ""
    system_name: str = ""
    description: str = ""
    data_sources: str = ""
    volume: str = ""
    data_types: str = ""
    contains_pii: bool = False
    pii_handling: str = ""
    consent_status: str = "not_applicable"
    consent_mechanism: str = ""
    quality_measures: str = ""
    bias_mitigation: str = ""
    copyright_compliance: str = ""
    governance_status: str = "draft"
    reviewed_by: str = ""
    review_date: str = ""
    notes: str = ""

class PlanCreate(BaseModel):
    name: str
    plan_type: str = ""
    framework: str = ""
    description: str = ""
    systems: list[str] = []
    owner: str = ""
    status: str = "draft"
    due_date: str = ""
    content: str = ""
    notes: str = ""
    evidence_ids: list[str] = []

class ContractCreate(BaseModel):
    name: str
    contract_type: str = ""
    framework: str = ""
    counterparty: str = ""
    description: str = ""
    guidance: str = ""
    status: str = "not_started"
    expiry_date: str = ""
    notes: str = ""
    evidence_ids: list[str] = []

# ─── Mutation Middleware (for shared sub-routers) ──────

_EXCLUDED_MUTATION_PREFIXES = (
    "/api/systems",
    "/api/review-cycles",
    "/api/evaluations",
    "/api/training-datasets",
    "/api/plans",
    "/api/contracts",
    "/api/competence",
    "/api/collectors",
    "/api/webhooks",
    "/api/webhook/",
    "/api/seed",
    "/api/clear",
    "/api/audit-log",
    "/api/corrective-actions",
    "/api/health",
    "/api/auth",
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
        ip = request.client.host if request.client else ""
        ua = request.headers.get("user-agent", "")
        details = {}
        if outcome == "failure":
            details = {"denied_path": path, "method": request.method, "security": True}
        log_event(
            action=request.method.lower(),
            resource_type=path.split("/")[2] if len(path.split("/")) > 2 else "unknown",
            framework_id="AIGov",
            user_id="",
            user_email="",
            ip_address=ip,
            user_agent=ua,
            outcome=outcome,
            details=details,
        )
    except Exception:
        pass
    return response


# ─── Health & Auth Config ──────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ai-governance"}

@app.get("/api/auth/config")
def auth_config():
    return {
        "enabled": True,
        "mode": "local",
        "tenant_id": "",
        "client_id": "",
        "scopes": [],
        "role_locked": False,
        "login_hint": "",
        "sandbox_mode": False,
        "sandbox_fixture_only": False,
    }


@app.post("/api/auth/login")
def auth_login(body: dict):
    from auth.jwt import create_token
    from auth.store import authenticate

    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))
    user = authenticate(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(
        user_id=user["id"],
        email=user["email"],
        name=user.get("name", ""),
        role=user.get("role", "Viewer"),
        org_id=user.get("org_id", ""),
        is_org_owner=bool(user.get("is_org_owner", 0)),
        is_msp=bool(user.get("is_msp", 0)),
        token_version=int(user.get("token_version", 0) or 0),
    )
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name", ""),
            "role": user.get("role", "Viewer"),
        },
    }


# Auth runs outermost — mirrors core_auth_middleware ordering.
app.middleware("http")(aigov_auth_middleware)

# ─── AI Systems (Model Registry) ──────────────────────

@app.get("/api/systems")
def list_systems(q: str | None = None, status: str | None = None, tier: str | None = None, tag: str | None = None):
    db = _load("systems")
    systems = list(db.values())
    if q:
        q = q.lower()
        systems = [s for s in systems if q in (s.get("name", "") + " " + s.get("description", "") + " " + s.get("owner", "") + " " + " ".join(s.get("tags", []))).lower()]
    if status:
        systems = [s for s in systems if s.get("deployment_status") == status]
    if tier:
        systems = [s for s in systems if s.get("risk_classification") == tier]
    if tag:
        systems = [s for s in systems if tag in s.get("tags", [])]
    return {"systems": systems, "total": len(systems)}

@app.post("/api/systems")
def create_system(data: SystemCreate):
    _require_edit_controls()
    db = _load("systems")
    sid = _id()
    now = _now()
    record = data.model_dump()
    record["id"] = sid
    record["system_id"] = sid
    record["created_at"] = now
    record["updated_at"] = now
    record.setdefault("approval_status", "draft")
    record["archived"] = False
    record.setdefault("version", "1.0.0")
    record.setdefault("review_date", "")
    record.setdefault("review_owner", "")
    record.setdefault("evidence_links", [])
    record["history"] = [{"timestamp": now, "action": "created", "detail": "System registered"}]
    record["risk_assessment"] = {}
    record["evidence"] = []
    record["changes"] = []
    if record.get("risk_classification") in ("high", "unacceptable"):
        record["pms_plan"] = f"Post-Market Monitoring Plan for {record['name']}\n\nReview frequency: monthly\nMetrics: accuracy, drift, incident rate\nOwner: {record.get('owner', 'TBD')}"
    db[sid] = record
    _save("systems", db)
    _audit_log("created", "system", sid, {"name": record["name"]})
    return {"id": sid}

@app.get("/api/systems/{sid}")
def get_system(sid: str):
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    system = dict(db[sid])
    answers = system.get("answers", {})
    enriched = {}
    for cid, ans in answers.items():
        enriched[cid] = dict(ans)
        if cid in AI_GENERATED_CONTROL_OBJECTIVES:
            enriched[cid]["objectives"] = AI_GENERATED_CONTROL_OBJECTIVES[cid]
    system["answers"] = enriched
    return {"system": system}

@app.patch("/api/systems/{sid}")
def update_system(sid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    old = {"risk_classification": record.get("risk_classification"), "deployment_status": record.get("deployment_status")}
    for k, v in data.items():
        if v is not None and k not in ("id", "system_id", "created_at"):
            record[k] = v
    record["updated_at"] = _now()
    record.setdefault("history", []).append({"timestamp": _now(), "action": "updated", "detail": "System updated"})
    db[sid] = record
    _save("systems", db)
    field_diffs = {}
    for field in ("risk_classification", "deployment_status"):
        if field in data and old[field] != record.get(field):
            field_diffs[field] = {"old": old[field], "new": record.get(field)}
    details = {"name": record.get("name")}
    if field_diffs:
        details["field_diffs"] = field_diffs
    _audit_log("updated", "system", sid, details)
    return {"system": record}


@app.get("/api/systems/{sid}/objectives")
def get_system_objectives(sid: str, framework: Optional[str] = Query(None)):
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    fw_map = {}
    if framework and framework in FRAMEWORKS:
        fw_map[framework] = FRAMEWORKS[framework]
    elif framework:
        raise HTTPException(404, "Unknown framework: {framework}")
    else:
        fw_map = FRAMEWORKS

    result = {}
    for fw_name, fw_data in fw_map.items():
        for article in fw_data.get("articles", []):
            cid = article.get("control_id")
            if cid and cid in AI_GENERATED_CONTROL_OBJECTIVES:
                if fw_name not in result:
                    result[fw_name] = []
                result[fw_name].append({
                    "article_id": article["id"],
                    "title": article["title"],
                    "control_id": cid,
                    "objectives": AI_GENERATED_CONTROL_OBJECTIVES[cid],
                })
    return {"frameworks": result}


@app.delete("/api/systems/{sid}")
def delete_system(sid: str):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    name = db[sid].get("name", "")
    del db[sid]
    _save("systems", db)
    _audit_log("deleted", "system", sid, {"name": name})
    return {"ok": True}

@app.get("/api/systems/{sid}/history")
def get_history(sid: str):
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    return {"history": db[sid].get("history", [])}

# ─── Risk Classification ──────────────────────────────

RISK_QUESTIONS = [
    {"key": "affects_people", "label": "Makes decisions affecting people?", "weight": 3},
    {"key": "healthcare", "label": "Used in healthcare decisions?", "weight": 3},
    {"key": "employment", "label": "Used in employment decisions?", "weight": 3},
    {"key": "financial", "label": "Used in financial decisions?", "weight": 2},
    {"key": "public_facing", "label": "Public-facing application?", "weight": 1},
    {"key": "biometric", "label": "Uses biometric data?", "weight": 3},
    {"key": "personal_info", "label": "Processes personal information?", "weight": 2},
    {"key": "autonomous", "label": "Takes autonomous actions?", "weight": 2},
    {"key": "critical_infrastructure", "label": "Used in critical infrastructure?", "weight": 3},
    {"key": "human_approval", "label": "Human approval always required?", "weight": -1},
    {"key": "prohibited_use", "label": "Prohibited use case?", "weight": 99},
    {"key": "general_purpose", "label": "General-purpose AI model?", "weight": 0},
]

@app.get("/api/risk-questions")
def list_risk_questions():
    return {"questions": RISK_QUESTIONS}

@app.post("/api/systems/{sid}/classify")
def classify_system(sid: str, answers: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    body = dict(answers or {})
    requested_profile = body.pop("ai_profile", None)
    answers = body
    score = 0
    flags = []
    for q in RISK_QUESTIONS:
        if answers.get(q["key"]):
            score += q["weight"]
            if q["weight"] > 0:
                flags.append(q["label"])
    if answers.get("prohibited_use"):
        tier = "unacceptable"
    elif answers.get("general_purpose"):
        tier = "gpa"
    elif score >= 8:
        tier = "high"
    elif score >= 5:
        tier = "limited"
    else:
        tier = "minimal"
    allowed_profiles = {"provider", "deployer", "gpai", "agentic"}
    if requested_profile in allowed_profiles:
        profile = requested_profile
    elif answers.get("autonomous"):
        profile = "agentic"
    elif answers.get("general_purpose"):
        profile = "gpai"
    else:
        profile = record.get("ai_profile") or "provider"
    if record.get("risk_assessment", {}).get("score") != score:
        record.setdefault("history", []).append({"timestamp": _now(), "action": "classified", "detail": f"Classified as {tier} (score: {score})"})
    record["risk_classification"] = tier
    record["ai_profile"] = profile
    record["risk_assessment"] = {"answers": answers, "score": score, "flags": flags, "classified_at": _now()}
    if tier in ("high", "unacceptable") and not record.get("pms_plan"):
        record["pms_plan"] = f"Post-Market Monitoring Plan for {record['name']}\n\nReview frequency: monthly\nOwner: {record.get('owner', 'TBD')}"
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("classified", "system", sid, {"tier": tier, "score": score})
    return {"system": record}

@app.get("/api/risk-tiers")
def list_risk_tiers():
    return {"tiers": {"unacceptable": "Prohibited", "high": "High Risk", "limited": "Limited Risk", "minimal": "Minimal Risk", "gpa": "General Purpose AI", "unclassified": "Unclassified"}}

# ─── Review Cycles ────────────────────────────────────


@app.get("/api/review-cycles")
def list_review_cycles():
    items = list(_load("review_cycles").values())
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"cycles": items}


@app.post("/api/review-cycles")
def create_review_cycle(data: ReviewCycleCreate):
    _require_edit_controls()
    db = _load("review_cycles")
    cid = _id()
    now = _now()
    record = {
        "id": cid,
        "label": data.label,
        "status": "scheduled",
        "start": data.start,
        "end": data.end,
        "models_reviewed": 0,
        "frameworks": ["ISO 42001", "NIST AI RMF", "EU AI Act"],
        "created_at": now,
        "updated_at": now,
    }
    db[cid] = record
    _save("review_cycles", db)
    _audit_log("created", "review_cycle", cid, {"label": data.label})
    return {"cycle": record}


@app.patch("/api/review-cycles/{cid}")
def update_review_cycle(cid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("review_cycles")
    if cid not in db:
        raise HTTPException(404, "Review cycle not found")
    record = db[cid]
    for k, v in data.items():
        if v is not None and k != "id":
            record[k] = v
    record["updated_at"] = _now()
    db[cid] = record
    _save("review_cycles", db)
    _audit_log("updated", "review_cycle", cid, {"label": record.get("label")})
    return {"cycle": record}


@app.delete("/api/review-cycles/{cid}")
def delete_review_cycle(cid: str):
    _require_edit_controls()
    db = _load("review_cycles")
    if cid not in db:
        raise HTTPException(404, "Review cycle not found")
    label = db[cid].get("label", "")
    del db[cid]
    _save("review_cycles", db)
    _audit_log("deleted", "review_cycle", cid, {"label": label})
    return {"status": "deleted"}


# ─── Evidence ─────────────────────────────────────────

@app.post("/api/systems/{sid}/evidence")
def upload_system_evidence(sid: str, file: UploadFile = File(...), label: str = Form("")):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    ext = os.path.splitext(file.filename or "file")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {ext} not allowed")
    data = file.file.read()
    if len(data) > MAX_EVIDENCE_MB * 1024 * 1024:
        raise HTTPException(400, f"File exceeds {MAX_EVIDENCE_MB}MB limit")
    evd = os.path.join(EVIDENCE_DIR, sid)
    os.makedirs(evd, exist_ok=True)
    eid = uuid4().hex[:8]
    fname = f"{eid}{ext}"
    path = os.path.join(evd, fname)
    with open(path, "wb") as f:
        f.write(data)
    record = db[sid]
    entry = {"id": eid, "filename": file.filename or fname, "label": label or file.filename or fname, "size": len(data), "uploaded_at": _now()}
    record.setdefault("evidence", []).append(entry)
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("created", "evidence", sid, {"eid": eid, "filename": file.filename})
    return {"evidence": entry}


@app.get("/api/systems/{sid}/evidence/{eid}")
def download_system_evidence(sid: str, eid: str):
    evd = os.path.join(EVIDENCE_DIR, sid)
    if not os.path.exists(evd):
        raise HTTPException(404, "Evidence not found")
    for fname in os.listdir(evd):
        if fname.startswith(eid):
            path = os.path.join(evd, fname)
            with open(path, "rb") as f:
                return Response(f.read(), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={fname}"})
    raise HTTPException(404, "Evidence not found")


@app.delete("/api/systems/{sid}/evidence/{eid}")
def delete_system_evidence(sid: str, eid: str):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    record["evidence"] = [e for e in record.get("evidence", []) if e["id"] != eid]
    evd = os.path.join(EVIDENCE_DIR, sid)
    for fname in os.listdir(evd) if os.path.exists(evd) else []:
        if fname.startswith(eid):
            os.remove(os.path.join(evd, fname))
            break
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("deleted", "evidence", sid, {"eid": eid})
    return {"ok": True}

@app.get("/api/systems/{sid}/evidence/{eid}")
def download_system_evidence(sid: str, eid: str):
    evd = os.path.join(EVIDENCE_DIR, sid)
    if not os.path.exists(evd):
        raise HTTPException(404, "Evidence not found")
    for fname in os.listdir(evd):
        if fname.startswith(eid):
            path = os.path.join(evd, fname)
            with open(path, "rb") as f:
                return Response(f.read(), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={fname}"})
    raise HTTPException(404, "Evidence not found")

@app.delete("/api/systems/{sid}/evidence/{eid}")
def delete_system_evidence(sid: str, eid: str):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    record["evidence"] = [e for e in record.get("evidence", []) if e["id"] != eid]
    evd = os.path.join(EVIDENCE_DIR, sid)
    for fname in os.listdir(evd) if os.path.exists(evd) else []:
        if fname.startswith(eid):
            os.remove(os.path.join(evd, fname))
            break
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    return {"ok": True}

# ─── Governance Dashboard ────────────────────────────

@app.get("/api/governance")
def get_governance():
    systems = list(_load("systems").values())
    from incidents.store import list_incidents
    incidents, _ = list_incidents(limit=9999)
    frias = list(_load("frias").values())
    from vendors.store import list_vendors
    vendor_list = list_vendors()

    total_systems = len(systems)
    high_risk = len([s for s in systems if s.get("risk_classification") in ("high", "unacceptable")])
    production_systems = len([s for s in systems if s.get("deployment_status") == "production"])
    total_incidents = len(incidents)
    open_incidents = len([i for i in incidents if i.get("status") not in ("closed",)])
    overdue_regulatory = len([i for i in incidents if i.get("regulatory_clock", {}).get("deadline", "") and not i["regulatory_clock"].get("notified") and i["regulatory_clock"]["deadline"] < _now()])

    frias_total = len(frias)
    frias_approved = len([f for f in frias if f.get("status") == "approved"])
    frias_draft = len([f for f in frias if f.get("status") == "draft"])

    vendor_total = len(vendor_list)
    vendor_assessed = len([v for v in vendor_list if v.get("status") == "assessed" or v.get("risk_level")])

    review_cycles_data = _load("review_cycles")
    review_cycles_list = list(review_cycles_data.values())
    cycles_total = len(review_cycles_list)
    cycles_active = len([c for c in review_cycles_list if c.get("status") == "in_progress"])

    # Framework coverage (imports comprehensive definitions from conformity)
    try:
        from conformity_routes import FRAMEWORKS as FW_DEFS
    except ImportError:
        FW_DEFS = {}

    controls = []
    for fw_key, fw_def in FW_DEFS.items():
        for art in fw_def["articles"]:
            controls.append({
                "framework": fw_key,
                "control_id": art["ref"],
                "control": art["title"],
                "description": art["summary"],
            })
    controls_original = controls[:]

    by_framework = {}
    for c in controls:
        fw = c["framework"]
        by_framework.setdefault(fw, {"total": 0, "covered": 0, "clauses": []})

    for sys in systems:
        tags = [t.lower() for t in sys.get("controls", [])]
        sys_status = sys.get("classification_status", "")
        covered_frameworks = set()
        for c in controls_original:
            cid_lower = c["control_id"].replace(" ", "").replace(".", "").lower()
            if any(cid_lower in t.replace(".", "").replace(" ", "") for t in tags) or sys_status in ("high", "prohibited"):
                covered_frameworks.add(c["framework"])
        for fw_key in covered_frameworks:
            by_framework[fw_key]["covered"] += 1

    for c in controls_original:
        fw = c["framework"]
        by_framework[fw]["total"] += 1
        by_framework[fw]["clauses"].append({
            "control_id": c["control_id"],
            "control": c["control"],
            "description": c["description"],
            "covered": False,
        })

    framework_coverage = {}
    covered_count = 0
    total_count = 0
    for fw_key, fw_data in by_framework.items():
        covered = fw_data["covered"]
        total = fw_data["total"]
        pct = round((covered / max(total, 1)) * 100)
        covered_count += covered
        total_count += total
        framework_coverage[fw_key] = {
            "covered": covered,
            "total": total,
            "coverage_pct": pct,
            "status": "covered" if pct >= 80 else "partial" if pct >= 30 else "missing",
        }

    overall_pct = round((covered_count / max(total_count, 1)) * 100)

    any_classified = len([s for s in systems if s.get("risk_classification")])
    any_conformity = overall_pct > 0
    onboarding_steps = [
        {"id": "welcome", "label": "Welcome", "done": True},
        {"id": "system", "label": "Register a System", "done": total_systems > 0},
        {"id": "classify", "label": "Classify Risk", "done": any_classified > 0},
        {"id": "conformity", "label": "Conformity Assessment", "done": any_conformity},
        {"id": "monitoring", "label": "Monitoring & Review", "done": cycles_total > 0 or total_incidents > 0},
    ]
    onboarding_required = [s for s in onboarding_steps if s["id"] != "welcome"]
    onboarding_done = sum(1 for s in onboarding_required if s["done"])
    onboarding_progress = round(100 * onboarding_done / len(onboarding_required)) if onboarding_required else 0

    return {
        "org_name": "Trident Defense Systems",
        "total_systems": total_systems,
        "total_incidents": total_incidents,
        "high_risk": high_risk,
        "production_systems": production_systems,
        "open_incidents": open_incidents,
        "overdue_regulatory": overdue_regulatory,
        "framework_coverage": {
            "overall_pct": overall_pct,
            "overall_status": "covered" if overall_pct >= 80 else "partial" if overall_pct >= 30 else "missing",
            "frameworks": framework_coverage,
        },
        "tools": {
            "systems": {"total": total_systems, "high_risk": high_risk, "production": production_systems},
            "incidents": {"total": total_incidents, "open": open_incidents, "overdue_regulatory": overdue_regulatory},
            "frias": {"total": frias_total, "approved": frias_approved, "draft": frias_draft},
            "vendors": {"total": vendor_total, "assessed": vendor_assessed},
            "review_cycles": {"total": cycles_total, "active": cycles_active},
        },
        "onboarding": {
            "steps": onboarding_steps,
            "progress_pct": onboarding_progress,
        },
    }

# ─── Dossier ──────────────────────────────────────────

@app.get("/api/systems/{sid}/dossier")
def get_dossier(sid: str):
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    from incidents.store import list_incidents
    all_incidents, _ = list_incidents(limit=9999)
    incidents = [i for i in all_incidents if i.get("system_id") == sid or i.get("system_id") == db[sid].get("name")]
    return {
        "system": db[sid],
        "related_incidents": incidents[:20],
        "dossier_exported_at": _now(),
    }


@app.post("/api/systems/{sid}/dossier/export")
def export_dossier(sid: str):
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    from eu_artifacts import export_dossier_pack

    buffer = export_dossier_pack(db[sid])
    return Response(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=regulatory-dossier-{sid}.zip"},
    )

# ─── Approval Workflow ────────────────────────────────

@app.post("/api/systems/{sid}/submit")
def submit_system(sid: str):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    record["approval_status"] = "submitted"
    record.setdefault("history", []).append({"timestamp": _now(), "action": "submitted", "detail": "Submitted for review"})
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("submitted", "system", sid)
    return {"system": record}

@app.post("/api/systems/{sid}/approve")
def approve_system(sid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    record["approval_status"] = "approved"
    record["reviewed_by"] = data.get("reviewed_by", "")
    record["reviewed_at"] = _now()
    record["review_comment"] = data.get("review_comment", "")
    record.setdefault("history", []).append({"timestamp": _now(), "action": "approved", "detail": f"Approved by {data.get('reviewed_by', 'unknown')}"})
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("approved", "system", sid, {"reviewed_by": data.get("reviewed_by")})
    return {"system": record}

@app.post("/api/systems/{sid}/reject")
def reject_system(sid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    record["approval_status"] = "rejected"
    record["reviewed_by"] = data.get("reviewed_by", "")
    record["reviewed_at"] = _now()
    record["review_comment"] = data.get("review_comment", "")
    record.setdefault("history", []).append({"timestamp": _now(), "action": "rejected", "detail": f"Rejected by {data.get('reviewed_by', 'unknown')}"})
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("rejected", "system", sid, {"reviewed_by": data.get("reviewed_by")})
    return {"system": record}

# ─── Model Card PDF Export ─────────────────────────────

@app.get("/api/systems/{sid}/export")
def export_model_card(sid: str):
    if not HAS_FPDF:
        raise HTTPException(501, "PDF generation not available — install fpdf2")
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    s = db[sid]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "AI System Card", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, f"Generated: {_now()[:10]} | PostureAI", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    def sec(title):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
    def fld(label, value):
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(40, 4, label)
        pdf.set_font("Helvetica", "", 8)
        pdf.multi_cell(0, 4, str(value) if value else "-")
        pdf.ln(1)
    sec("1. System Identification")
    fld("Name:", s.get("name"))
    fld("Description:", s.get("description"))
    fld("Purpose:", s.get("purpose"))
    fld("Foundation Model:", s.get("foundation_model"))
    fld("Vendor:", s.get("vendor"))
    sec("2. Ownership & Accountability")
    fld("Owner:", s.get("owner"))
    fld("Business Owner:", s.get("business_owner"))
    fld("Technical Owner:", s.get("technical_owner"))
    fld("Risk Owner:", s.get("risk_owner"))
    sec("3. Risk Classification")
    fld("Risk Tier:", s.get("risk_classification", "unclassified"))
    ra = s.get("risk_assessment", {})
    fld("Risk Score:", str(ra.get("score", "-")))
    sec("4. Deployment")
    fld("Status:", s.get("deployment_status"))
    fld("Environment:", s.get("environment"))
    fld("Approval:", s.get("approval_status", "draft"))
    sec("5. Transparency & Data")
    fld("Public-facing:", "Yes" if s.get("is_public_facing") else "No")
    fld("Input Data:", s.get("input_data_sources") or "-")
    fld("Processing:", s.get("processing_location") or "-")
    fld("Output Dest:", s.get("output_destinations") or "-")
    sec("6. Model Card Details")
    fld("Performance Metrics:", s.get("performance_metrics") or "-")
    fld("Known Limitations:", s.get("known_limitations") or "-")
    fld("Out-of-Scope Uses:", s.get("out_of_scope_uses") or "-")
    fld("Human Oversight:", s.get("human_oversight") or "-")
    fld("Bias & Fairness:", s.get("bias_fairness_notes") or "-")
    fld("Training Data:", s.get("training_data") or "-")
    buffer = bytes(pdf.output())
    return Response(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=model-card-{sid}.pdf"})

# ─── Bulk Operations ──────────────────────────────────

@app.post("/api/systems/bulk")
def bulk_operation(data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    ids = data.get("ids", [])
    action = data.get("action", "")
    now = _now()
    affected = 0
    for sid in ids:
        if sid not in db:
            continue
        if action == "archive":
            db[sid]["archived"] = True
        elif action == "unarchive":
            db[sid]["archived"] = False
        elif action == "delete":
            del db[sid]
            affected += 1
            continue
        elif action == "update" and data.get("updates"):
            allowed = {"deployment_status", "environment", "owner", "risk_classification", "source"}
            for k, v in data["updates"].items():
                if k in allowed:
                    db[sid][k] = v
        db[sid].setdefault("history", []).append({"timestamp": now, "action": f"bulk_{action}", "detail": f"Bulk {action}"})
        db[sid]["updated_at"] = now
        affected += 1
    _save("systems", db)
    _audit_log("bulk", "system", "", {"action": action, "affected": affected})
    return {"ok": True, "affected": affected}

# ─── Change Management ────────────────────────────────

@app.post("/api/systems/{sid}/changes")
def create_change(sid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    change = {
        "id": uuid4().hex[:8],
        "change_type": data.get("change_type", "other"),
        "description": data.get("description", ""),
        "reason": data.get("reason", ""),
        "requested_by": data.get("requested_by", ""),
        "risk_review": data.get("risk_review", ""),
        "approved_by": data.get("approved_by", ""),
        "approval_status": "pending",
        "timestamp": _now(),
    }
    record.setdefault("changes", []).append(change)
    record.setdefault("history", []).append({"timestamp": _now(), "action": "change_requested", "detail": f"Change: {data.get('change_type', '')} — {data.get('description', '')[:80]}"})
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("created", "change", sid, {"change_type": data.get("change_type")})
    return {"change": change}

@app.patch("/api/systems/{sid}/changes/{cid}")
def update_change(sid: str, cid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    for c in db[sid].get("changes", []):
        if c.get("id") == cid:
            if "approval_status" in data:
                c["approval_status"] = data["approval_status"]
            if "approved_by" in data:
                c["approved_by"] = data["approved_by"]
            if "risk_review" in data:
                c["risk_review"] = data["risk_review"]
            now = _now()
            db[sid].setdefault("history", []).append({"timestamp": now, "action": "change_" + data.get("approval_status", "updated"), "detail": f"Change {cid}: {data.get('approval_status', 'updated')}"})
            db[sid]["updated_at"] = now
            _save("systems", db)
            _audit_log("updated", "change", cid, {"system_id": sid, "status": c.get("approval_status")})
            return {"change": c}
    raise HTTPException(404, "Change not found")

@app.get("/api/systems/{sid}/changes")
def list_changes(sid: str):
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    return {"changes": db[sid].get("changes", [])}

# ─── AI Literacy Log ──────────────────────────────────

@app.post("/api/systems/{sid}/literacy")
def add_literacy(sid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    entry = {
        "id": uuid4().hex[:8],
        "person_name": data.get("person_name", ""),
        "person_email": data.get("person_email", ""),
        "role": data.get("role", ""),
        "training_date": data.get("training_date", ""),
        "training_type": data.get("training_type", ""),
        "notes": data.get("notes", ""),
        "created_at": _now(),
    }
    db[sid].setdefault("ai_literacy_log", []).append(entry)
    db[sid]["updated_at"] = _now()
    _save("systems", db)
    _audit_log("created", "literacy", sid, {"person": data.get("person_name")})
    return {"entry": entry}

@app.delete("/api/systems/{sid}/literacy/{eid}")
def delete_literacy(sid: str, eid: str):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    old_len = len(db[sid].get("ai_literacy_log", []))
    db[sid]["ai_literacy_log"] = [e for e in db[sid].get("ai_literacy_log", []) if e.get("id") != eid]
    if len(db[sid]["ai_literacy_log"]) == old_len:
        raise HTTPException(404, "Entry not found")
    db[sid]["updated_at"] = _now()
    _save("systems", db)
    _audit_log("deleted", "literacy", eid, {"system_id": sid})
    return {"ok": True}

# ─── Corrective Actions (Art. 20) ─────────────────────

@app.get("/api/systems/{sid}/corrective-actions")
def list_corrective_actions(sid: str):
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    ca_db = _load("corrective_actions")
    actions = [a for a in ca_db.values() if a.get("system_id") == sid]
    actions.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    return {"actions": actions}

@app.post("/api/systems/{sid}/corrective-actions")
def create_corrective_action(sid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    ca_db = _load("corrective_actions")
    aid = _id()
    now = _now()
    action = {
        "id": aid,
        "system_id": sid,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "source": data.get("source", "other"),
        "severity": data.get("severity", "medium"),
        "status": "open",
        "related_article": data.get("related_article", ""),
        "root_cause": data.get("root_cause", ""),
        "action_plan": data.get("action_plan", ""),
        "assigned_to": data.get("assigned_to", ""),
        "deadline": data.get("deadline", ""),
        "resolution_notes": "",
        "resolved_at": "",
        "created_at": now,
        "updated_at": now,
    }
    ca_db[aid] = action
    _save("corrective_actions", ca_db)
    sys_record = db[sid]
    sys_record.setdefault("history", []).append({"timestamp": now, "action": "corrective_action_created", "detail": f"Corrective action: {action['title'][:80]}"})
    sys_record["updated_at"] = now
    _save("systems", db)
    _audit_log("created", "corrective_action", aid, {"system_id": sid, "title": action["title"]})
    return {"action": action}

@app.patch("/api/corrective-actions/{aid}")
def update_corrective_action(aid: str, data: dict = {}):
    _require_edit_controls()
    ca_db = _load("corrective_actions")
    if aid not in ca_db:
        raise HTTPException(404, "Corrective action not found")
    action = ca_db[aid]
    old = {"status": action.get("status"), "severity": action.get("severity")}
    allowed = {"title", "description", "source", "severity", "status", "related_article", "root_cause", "action_plan", "assigned_to", "deadline", "resolution_notes"}
    now = _now()
    for k, v in data.items():
        if k in allowed and v is not None:
            action[k] = v
    if data.get("status") == "resolved" and not action.get("resolved_at"):
        action["resolved_at"] = now
    action["updated_at"] = now
    ca_db[aid] = action
    _save("corrective_actions", ca_db)
    field_diffs = {}
    for field in ("status", "severity"):
        if field in data and old[field] != action.get(field):
            field_diffs[field] = {"old": old[field], "new": action.get(field)}
    details = {"status": action.get("status")}
    if field_diffs:
        details["field_diffs"] = field_diffs
    _audit_log("updated", "corrective_action", aid, details)
    return {"action": action}

@app.delete("/api/corrective-actions/{aid}")
def delete_corrective_action(aid: str):
    _require_edit_controls()
    ca_db = _load("corrective_actions")
    if aid not in ca_db:
        raise HTTPException(404, "Corrective action not found")
    del ca_db[aid]
    _save("corrective_actions", ca_db)
    _audit_log("deleted", "corrective_action", aid)
    return {"ok": True}

# ─── Model Versions ────────────────────────────────────

@app.post("/api/systems/{sid}/versions")
def create_version(sid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    entry = {
        "id": uuid4().hex[:8],
        "version": data.get("version", ""),
        "release_date": data.get("release_date", _now()[:10]),
        "change_log": data.get("change_log", ""),
        "status": data.get("status", "development"),
        "created_by": data.get("created_by", ""),
        "created_at": _now(),
    }
    record.setdefault("versions", []).append(entry)
    record["version"] = entry["version"]
    record.setdefault("history", []).append({"timestamp": _now(), "action": "version_created", "detail": f"Version {entry['version']} created"})
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("created", "version", sid, {"version": entry["version"]})
    return {"version": entry}

@app.get("/api/systems/{sid}/versions")
def list_versions(sid: str):
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    versions = list(reversed(db[sid].get("versions", [])))
    return {"versions": versions, "total": len(versions)}

@app.delete("/api/systems/{sid}/versions/{vid}")
def delete_version(sid: str, vid: str):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    before = len(record.get("versions", []))
    record["versions"] = [v for v in record.get("versions", []) if v.get("id") != vid]
    if len(record["versions"]) == before:
        raise HTTPException(404, "Version not found")
    record.setdefault("history", []).append({"timestamp": _now(), "action": "version_deleted", "detail": f"Version deleted"})
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("deleted", "version", vid, {"system_id": sid})
    return {"ok": True}

# ─── Incident Playbooks ───────────────────────────────

# ─── Audit Log ────────────────────────────────────────

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
    return Response(csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audit-log.csv"})


# ─── Deploy ───────────────────────────────────────────

@app.post("/api/systems/{sid}/deploy")
def deploy_system(sid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("systems")
    if sid not in db:
        raise HTTPException(404, "System not found")
    record = db[sid]
    entry = {
        "id": uuid4().hex[:8],
        "environment": data.get("environment", record.get("environment", "unknown")),
        "version": data.get("version", record.get("version", "1.0.0")),
        "timestamp": _now(),
        "deployed_by": data.get("deployed_by", ""),
        "notes": data.get("notes", ""),
    }
    record.setdefault("deployments", []).append(entry)
    record["deployment_status"] = "production"
    record["environment"] = entry["environment"]
    record.setdefault("history", []).append({"timestamp": _now(), "action": "deployed", "detail": f"Deployed to {entry['environment']} by {entry['deployed_by'] or 'unknown'}"})
    record["updated_at"] = _now()
    db[sid] = record
    _save("systems", db)
    _audit_log("deployed", "system", sid, {"environment": entry["environment"], "version": entry["version"]})
    return {"system": record, "deployment": entry}

# ─── Systems CSV Export ─────────────────────────────

@app.get("/api/systems/export/csv")
def export_systems_csv():
    items = list(_load("systems").values())
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "name", "version", "description", "owner", "risk_classification", "deployment_status", "environment", "approval_status", "created_at"])
    for s in items:
        w.writerow([s.get("id"), s.get("name"), s.get("version"), s.get("description"), s.get("owner"), s.get("risk_classification"), s.get("deployment_status"), s.get("environment"), s.get("approval_status"), s.get("created_at")])
    return Response(buf.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=systems-export.csv"})


# ─── Review Reminders ─────────────────────────────────

@app.get("/api/reminders")
def get_reminders():
    now = datetime.now(timezone.utc)
    systems = list(_load("systems").values())
    overdue, upcoming = [], []
    for s in systems:
        rd = s.get("review_date")
        if not rd:
            continue
        try:
            rd_dt = datetime.fromisoformat(rd.replace("Z", "+00:00"))
            days = (rd_dt - now).days
            info = {"id": s["id"], "name": s["name"], "review_date": rd, "days_overdue": abs(days) if days < 0 else 0, "days_until": days if days >= 0 else 0}
            if days < 0:
                overdue.append(info)
            elif days <= 30:
                upcoming.append(info)
        except Exception:
            pass
    return {"overdue": overdue, "upcoming": upcoming}

# ─── Gap Analysis ──────────────────────────────────────

@app.get("/api/gap-analysis")
def gap_analysis(framework: str | None = Query(None)):
    systems = _load("systems")
    results = gap_analysis_rows(systems, framework)
    return {"results": results, "total_controls": len(results), "total_systems": len(systems)}


@app.post("/api/seed")
def seed_data():
    _require_edit_controls()
    systems = _load("systems")
    existing_count = len(systems)
    now = _now()

    # Seed from conformity_routes for article IDs
    try:
        from conformity_routes import FRAMEWORKS
    except ImportError:
        FRAMEWORKS = {}

    samples = [
        {"name": "Trident Hiring Intelligence", "description": "AI-powered resume screening and candidate assessment for cleared positions", "risk_classification": "high", "owner": "Sam Patel", "deployment_status": "staging", "purpose": "HR recruitment for cleared roles", "tags": ["recruitment", "high-risk"], "version": "2.1.0", "vendor": "Trident Defense Systems", "foundation_model": "Llama-3-8B (fine-tuned)", "is_fine_tuned": True, "input_data_sources": "Resume uploads, HR database", "processing_location": "us-east-1", "output_destinations": "Recruiter dashboard", "controls": ["Art.9", "Art.10", "Art.11", "Art.12", "Art.14", "GOV.1", "GOV.5", "MAP.1", "MEASURE.1", "A.5", "A.7"]},
        {"name": "Trident Mission Support Assistant", "description": "GPT-4o based assistant for mission planning and threat analysis", "risk_classification": "limited", "owner": "Jordan Lee", "deployment_status": "production", "purpose": "Mission planning support", "tags": ["gpt-4o", "mission"], "version": "1.0.0", "vendor": "OpenAI", "foundation_model": "gpt-4o", "is_fine_tuned": False, "controls": ["Art.13", "Art.50", "GOV.1", "MAP.1", "MEASURE.1", "MANAGE.1", "A.5", "A.9"]},
        {"name": "Trident Financial Monitoring", "description": "Transaction fraud detection across DoD supply chain payments", "risk_classification": "high", "owner": "Taylor Reed", "deployment_status": "production", "purpose": "Financial monitoring", "tags": ["fraud-detection", "high-risk"], "version": "3.2.0", "controls": ["Art.9", "Art.10", "Art.11", "Art.12", "Art.14", "Art.15", "GOV.1", "GOV.4", "MAP.1", "MAP.3", "MEASURE.1", "MEASURE.3", "MANAGE.1", "A.5", "A.7", "A.8"]},
        {"name": "Trident Document Classifier", "description": "Automated document classification for CUI handling", "risk_classification": "minimal", "owner": "Alex Kim", "deployment_status": "development", "purpose": "Document processing", "tags": ["nlp", "minimal-risk"], "version": "0.5.0", "controls": ["GOV.1", "GOV.2", "MAP.1", "MEASURE.1", "MEASURE.5", "MANAGE.1", "A.9"]},
        {"name": "Trident Supply Chain Risk Analyzer", "description": "Risk analysis of subcontractor supply chains using ML", "risk_classification": "limited", "owner": "Morgan Chen", "deployment_status": "staging", "purpose": "Supply chain risk", "tags": ["supply-chain", "limited-risk"], "version": "1.2.0", "controls": ["Art.13", "GOV.1", "GOV.3", "MAP.1", "MAP.4", "MEASURE.1", "MEASURE.4", "MANAGE.1", "A.5", "A.7", "A.10"]},
        {"name": "Trident Personnel Advisor", "description": "LLM-based career development and skills matching for personnel", "risk_classification": "limited", "owner": "Riley Santos", "deployment_status": "production", "purpose": "HR development", "tags": ["hr", "limited-risk"], "version": "2.0.0", "controls": ["Art.13", "Art.50", "GOV.1", "MAP.1", "MEASURE.1", "MEASURE.5", "MANAGE.1", "A.5", "A.9", "A.10"]},
    ]

    # Clear and re-seed
    systems = {}
    for s in samples:
        sid = _id()
        s["id"] = sid
        s["system_id"] = sid
        s["created_at"] = now
        s["updated_at"] = now
        s["approval_status"] = "draft"
        s["archived"] = False
        s["history"] = [{"timestamp": now, "action": "created", "detail": "Seeded"}]
        s["risk_assessment"] = {"score": 12 if s["risk_classification"] == "high" else 6 if s["risk_classification"] == "limited" else 2, "classified_at": now, "flags": []}
        s["evidence"] = []
        s["changes"] = []
        systems[sid] = s
    _save("systems", systems)

    # Pre-seed conformity assessments for each framework
    ca_db = _load("conformity")
    ca_db.clear()
    for sid, sys in systems.items():
        tier = sys.get("risk_classification", "unclassified")
        for fw_key, fw_def in FRAMEWORKS.items():
            applicable = [a for a in fw_def["articles"] if tier in a["tiers"]]
            if not applicable:
                continue
            articles = {}
            for art in applicable:
                # Random-ish status — mark some compliant, some partial, keep a few missing
                i = ord(art["id"][0]) if art["id"] else 0
                if i % 3 == 0:
                    st = "missing"
                elif i % 3 == 1:
                    st = "partial"
                else:
                    st = "compliant"
                articles[art["id"]] = {"status": st, "notes": f"Assessment for {art['ref']}" if st != "compliant" else ""}
            key = f"{sid}:{fw_key}"
            ca_db[key] = {
                "system_id": sid,
                "framework": fw_key,
                "status": "in_progress",
                "articles": articles,
                "created_at": now,
                "updated_at": now,
            }
    _save("conformity", ca_db)

    # Pre-seed corrective actions for high-risk systems
    ca_action_db = _load("corrective_actions")
    ca_action_db.clear()
    for sid, sys in systems.items():
        if sys.get("risk_classification") not in ("high", "unacceptable"):
            continue
        aid = _id()
        ca_action_db[aid] = {
            "id": aid,
            "system_id": sid,
            "title": "Human oversight mechanism needed",
            "description": "High-risk systems require effective human oversight per applicable framework requirements.",
            "source": "conformity_assessment",
            "severity": "high",
            "status": "open",
            "related_article": "Art. 14",
            "root_cause": "Initial deployment lacked human-in-the-loop review step",
            "action_plan": "Implement human review gate before automated decisions are executed",
            "assigned_to": sys.get("owner", "TBD"),
            "deadline": "2026-09-30",
            "resolution_notes": "",
            "resolved_at": "",
            "created_at": now,
            "updated_at": now,
        }
    _save("corrective_actions", ca_action_db)

    # ── Seed evaluations ─────────────────────────────────────────
    eval_db = _load("evaluations")
    eval_db.clear()
    owner_of = {sys["name"]: sys["owner"] for sys in systems.values()}
    sids = {sys["name"]: sid for sid, sys in systems.items()}

    evaluations = [
        # Hiring Intelligence
        {"name": "Bias Audit — Resume Screening", "system_id": sids["Trident Hiring Intelligence"], "system_name": "Trident Hiring Intelligence", "evaluation_type": "bias", "status": "completed", "score": 0.87, "tester": owner_of["Trident Hiring Intelligence"], "test_date": "2026-03-15", "reviewer": "Maria Gonzalez", "review_date": "2026-03-22", "methodology": "Disparate impact analysis across demographic groups using blinded resume sets", "criteria": "Statistical parity difference < 0.1 for all protected attributes", "results": "Minor skew detected on name-based filter — mitigated in v2.2.0", "notes": "Recommend quarterly re-audits as training data evolves"},
        {"name": "Accuracy Assessment — Candidate Ranking", "system_id": sids["Trident Hiring Intelligence"], "system_name": "Trident Hiring Intelligence", "evaluation_type": "accuracy", "status": "completed", "score": 0.82, "tester": owner_of["Trident Hiring Intelligence"], "test_date": "2026-04-01", "reviewer": "Maria Gonzalez", "review_date": "2026-04-08", "methodology": "Holdout validation against 5,000 labelled candidate profiles", "criteria": "Top-5 recall >= 0.85", "results": "Top-5 recall 0.82 — below threshold, requires retraining", "notes": "Scheduled retraining with expanded dataset for Q3 2026"},
        {"name": "Human Oversight Review", "system_id": sids["Trident Hiring Intelligence"], "system_name": "Trident Hiring Intelligence", "evaluation_type": "human_review", "status": "planned", "score": 0.0, "tester": "", "test_date": "2026-07-01", "reviewer": "", "review_date": "", "methodology": "Simulated hiring decisions with and without human-in-the-loop", "criteria": "Human override rate < 5%", "results": "", "notes": "Dependent on oversight mechanism implementation (see CA-001)"},
        {"name": "Cybersecurity Penetration Test", "system_id": sids["Trident Hiring Intelligence"], "system_name": "Trident Hiring Intelligence", "evaluation_type": "cybersecurity", "status": "completed", "score": 0.91, "tester": "Red Team Alpha", "test_date": "2026-02-20", "reviewer": "Alex Kim", "review_date": "2026-03-01", "methodology": "OWASP Top 10 + AI-specific attack vectors (prompt injection, model inversion)", "criteria": "No critical or high-severity findings", "results": "Two medium findings (rate limiting, input sanitization) — remediated"},
        # Mission Support Assistant
        {"name": "Hallucination Benchmark", "system_id": sids["Trident Mission Support Assistant"], "system_name": "Trident Mission Support Assistant", "evaluation_type": "hallucination", "status": "completed", "score": 0.76, "tester": owner_of["Trident Mission Support Assistant"], "test_date": "2026-03-10", "reviewer": "Sam Patel", "review_date": "2026-03-17", "methodology": "500 factual queries against verified ground truth data", "criteria": "Factual accuracy >= 0.85", "results": "Accuracy 0.76 — fine-tuning and RAG pipeline improvements needed", "notes": "RAG foundation model upgrade planned for Q3 2026"},
        {"name": "Performance Benchmark — Latency & Throughput", "system_id": sids["Trident Mission Support Assistant"], "system_name": "Trident Mission Support Assistant", "evaluation_type": "performance", "status": "completed", "score": 0.88, "tester": owner_of["Trident Mission Support Assistant"], "test_date": "2026-02-25", "reviewer": "Taylor Reed", "review_date": "2026-03-05", "methodology": "1,000 concurrent requests measured over 24h period", "criteria": "p95 latency < 3s, throughput > 100 req/s", "results": "p95 latency 2.1s, throughput 145 req/s — meets targets"},
        {"name": "Adversarial Red Team — Mission Scenario", "system_id": sids["Trident Mission Support Assistant"], "system_name": "Trident Mission Support Assistant", "evaluation_type": "red_team", "status": "in_progress", "score": 0.0, "tester": "Red Team Alpha", "test_date": "2026-05-01", "reviewer": "", "review_date": "", "methodology": "Simulated adversary probing for information leakage, jailbreaking, and prompt injection", "criteria": "Zero successful extractions of classified information", "results": "", "notes": "Interim findings expected by 2026-05-15"},
        {"name": "Robustness Testing — Input Perturbation", "system_id": sids["Trident Mission Support Assistant"], "system_name": "Trident Mission Support Assistant", "evaluation_type": "robustness", "status": "planned", "score": 0.0, "tester": "", "test_date": "2026-06-15", "reviewer": "", "review_date": "", "methodology": "Adversarial input perturbations (typos, paraphrasing, noise)", "criteria": "Output stability > 0.90 across perturbations", "results": "", "notes": ""},
        # Financial Monitoring
        {"name": "Fraud Detection Accuracy", "system_id": sids["Trident Financial Monitoring"], "system_name": "Trident Financial Monitoring", "evaluation_type": "accuracy", "status": "completed", "score": 0.94, "tester": owner_of["Trident Financial Monitoring"], "test_date": "2026-03-01", "reviewer": "Morgan Chen", "review_date": "2026-03-10", "methodology": "Holdout validation on 50K labelled transactions", "criteria": "AUC-ROC >= 0.92", "results": "AUC-ROC 0.94 — exceeds target", "notes": ""},
        {"name": "Fairness Audit — Transaction Monitoring", "system_id": sids["Trident Financial Monitoring"], "system_name": "Trident Financial Monitoring", "evaluation_type": "fairness", "status": "completed", "score": 0.85, "tester": owner_of["Trident Financial Monitoring"], "test_date": "2026-03-20", "reviewer": "Jordan Lee", "review_date": "2026-04-01", "methodology": "False positive rate analysis across vendor tiers and regions", "criteria": "FPR disparity < 0.05 across all segments", "results": "FPR disparity 0.03 — acceptable", "notes": ""},
        {"name": "Cybersecurity Assessment — Payment Pipeline", "system_id": sids["Trident Financial Monitoring"], "system_name": "Trident Financial Monitoring", "evaluation_type": "cybersecurity", "status": "completed", "score": 0.79, "tester": "Red Team Alpha", "test_date": "2026-01-15", "reviewer": "Riley Santos", "review_date": "2026-01-28", "methodology": "PCI DSS + AI-specific attack surface review", "criteria": "No critical findings", "results": "One critical finding (unencrypted model cache) — remediated in v3.2.1", "notes": "Follow-up scan scheduled Q3 2026"},
        {"name": "Internal Compliance Audit", "system_id": sids["Trident Financial Monitoring"], "system_name": "Trident Financial Monitoring", "evaluation_type": "internal_audit", "status": "planned", "score": 0.0, "tester": "", "test_date": "2026-08-01", "reviewer": "", "review_date": "", "methodology": "Full compliance review against EU AI Act Art. 9-15 and NIST AI RMF", "criteria": "All high-risk requirements satisfiable", "results": "", "notes": "Part of Q3 2026 internal audit cycle"},
        # Document Classifier
        {"name": "Classification Accuracy Benchmark", "system_id": sids["Trident Document Classifier"], "system_name": "Trident Document Classifier", "evaluation_type": "accuracy", "status": "completed", "score": 0.96, "tester": owner_of["Trident Document Classifier"], "test_date": "2026-04-05", "reviewer": "Sam Patel", "review_date": "2026-04-12", "methodology": "10K labelled CUI documents across 15 classification categories", "criteria": "F1 >= 0.90", "results": "F1 0.96 — exceeds target", "notes": ""},
        {"name": "Performance — Throughput Test", "system_id": sids["Trident Document Classifier"], "system_name": "Trident Document Classifier", "evaluation_type": "performance", "status": "completed", "score": 0.93, "tester": owner_of["Trident Document Classifier"], "test_date": "2026-04-06", "reviewer": "Taylor Reed", "review_date": "2026-04-10", "methodology": "Batch processing 5K documents", "criteria": "Throughput > 100 docs/min", "results": "143 docs/min — meets target", "notes": "Memory usage spiked at 4.2 GB for largest batch — optimization ticket filed"},
        # Supply Chain Risk Analyzer
        {"name": "Robustness — Supplier Data Drift", "system_id": sids["Trident Supply Chain Risk Analyzer"], "system_name": "Trident Supply Chain Risk Analyzer", "evaluation_type": "robustness", "status": "completed", "score": 0.81, "tester": owner_of["Trident Supply Chain Risk Analyzer"], "test_date": "2026-02-10", "reviewer": "Alex Kim", "review_date": "2026-02-20", "methodology": "Introduce synthetic data drift in supplier financial features", "criteria": "Risk score stability > 0.80 under 10% feature perturbation", "results": "Stability 0.81 — marginal pass", "notes": "Monitor drift detection pipeline for feature set changes"},
        {"name": "Fairness — Subcontractor Tier Analysis", "system_id": sids["Trident Supply Chain Risk Analyzer"], "system_name": "Trident Supply Chain Risk Analyzer", "evaluation_type": "fairness", "status": "completed", "score": 0.89, "tester": owner_of["Trident Supply Chain Risk Analyzer"], "test_date": "2026-03-05", "reviewer": "Morgan Chen", "review_date": "2026-03-12", "methodology": "Risk score distribution analysis across small vs. large subcontractors", "criteria": "No systematic bias against small business tier", "results": "Small business scores within 2% of large business — acceptable", "notes": ""},
        {"name": "Regulatory Conformity — Supply Chain AI", "system_id": sids["Trident Supply Chain Risk Analyzer"], "system_name": "Trident Supply Chain Risk Analyzer", "evaluation_type": "conformity", "status": "in_progress", "score": 0.0, "tester": owner_of["Trident Supply Chain Risk Analyzer"], "test_date": "2026-05-10", "reviewer": "", "review_date": "", "methodology": "Gap analysis against NIST AI RMF MEASURE and ISO 42001 Clause 9", "criteria": "Zero non-conformities for limited-risk classification", "results": "", "notes": "Preliminary findings available 2026-05-20"},
        # Personnel Advisor
        {"name": "Bias Audit — Career Recommendations", "system_id": sids["Trident Personnel Advisor"], "system_name": "Trident Personnel Advisor", "evaluation_type": "bias", "status": "completed", "score": 0.92, "tester": owner_of["Trident Personnel Advisor"], "test_date": "2026-01-20", "reviewer": "Jordan Lee", "review_date": "2026-02-01", "methodology": "Recommendation analysis across role, tenure, and demographic attributes", "criteria": "Recommendation parity across all segments", "results": "No statistically significant bias detected", "notes": "Clean audit — no remediation needed"},
        {"name": "Human Review — Skills Matching Quality", "system_id": sids["Trident Personnel Advisor"], "system_name": "Trident Personnel Advisor", "evaluation_type": "human_review", "status": "completed", "score": 0.78, "tester": owner_of["Trident Personnel Advisor"], "test_date": "2026-02-15", "reviewer": "Riley Santos", "review_date": "2026-02-22", "methodology": "HR team blind review of 200 matched recommendations", "criteria": "Human approval rate >= 0.80", "results": "Approval rate 0.78 — slightly below target", "notes": "False positive matches in cross-domain skills (e.g., finance -> engineering); tuning in progress"},
        {"name": "Performance — Recommendation Latency", "system_id": sids["Trident Personnel Advisor"], "system_name": "Trident Personnel Advisor", "evaluation_type": "performance", "status": "planned", "score": 0.0, "tester": "", "test_date": "2026-07-15", "reviewer": "", "review_date": "", "methodology": "p95 latency for batch and real-time recommendation endpoints", "criteria": "p95 < 500ms for real-time, < 5s for batch", "results": "", "notes": ""},
    ]
    for ev in evaluations:
        eid = _id()
        ev["id"] = eid
        ev["created_at"] = now
        ev["updated_at"] = now
        eval_db[eid] = ev
    _save("evaluations", eval_db)

    # ── Seed training datasets ────────────────────────────────────────
    tds_db = _load("training_datasets")
    tds_db.clear()

    datasets = [
        {"name": "Candidate Resume Database", "system_id": sids["Trident Hiring Intelligence"], "system_name": "Trident Hiring Intelligence", "description": "Historical candidate resumes and screening outcomes for cleared positions", "data_sources": "HR database, applicant tracking system, security clearance records", "volume": "85,000 records", "data_types": "Text resumes, skills tags, clearance level, screening decisions", "contains_pii": True, "pii_handling": "PII masked at ingestion; only anonymized feature vectors stored long-term", "consent_status": "explicit", "consent_mechanism": "Applicant consent collected via ATS during application submission", "quality_measures": "Deduplication, format normalization, missing field tagging", "bias_mitigation": "Stratified sampling by clearance level and role type enforced", "copyright_compliance": "All resumes submitted voluntarily by applicants", "governance_status": "approved", "reviewed_by": "Maria Gonzalez", "review_date": "2026-01-15", "notes": "Core training set for v2.x models"},
        {"name": "Cleared Personnel Records", "system_id": sids["Trident Hiring Intelligence"], "system_name": "Trident Hiring Intelligence", "description": "Anonymized personnel records from DoD cleared workforce database", "data_sources": "Workforce management system", "volume": "12,000 records", "data_types": "Role history, skills, clearance level, performance ratings", "contains_pii": True, "pii_handling": "Fully anonymized — names, SSN, contact info removed at source", "consent_status": "legitimate_interest", "consent_mechanism": "Legitimate interest basis under workforce analytics policy", "quality_measures": "Cross-referenced with HR master data for accuracy", "bias_mitigation": "Oversampling of underrepresented clearance levels and role families", "copyright_compliance": "Internal data — no third-party copyright concerns", "governance_status": "approved", "reviewed_by": "Maria Gonzalez", "review_date": "2026-02-01", "notes": "Supplemental dataset for fairness evaluation"},
        {"name": "Mission Planning Knowledge Base", "system_id": sids["Trident Mission Support Assistant"], "system_name": "Trident Mission Support Assistant", "description": "Curated corpus of mission planning documents, threat intelligence reports, and operational doctrine", "data_sources": "DoD field manuals, declassified after-action reports, threat intelligence feeds", "volume": "250,000 documents", "data_types": "PDF, DOCX, structured threat reports, geospatial data", "contains_pii": False, "pii_handling": "", "consent_status": "not_applicable", "consent_mechanism": "", "quality_measures": "Manual curation by subject matter experts", "bias_mitigation": "Multi-source cross-referencing to reduce single-source bias", "copyright_compliance": "DoD-produced materials — no external copyright restrictions", "governance_status": "approved", "reviewed_by": "Sam Patel", "review_date": "2026-01-10", "notes": "Foundation corpus for RAG pipeline"},
        {"name": "Threat Analysis Corpus", "system_id": sids["Trident Mission Support Assistant"], "system_name": "Trident Mission Support Assistant", "description": "Open-source intelligence reports and sanitized threat assessments for model fine-tuning", "data_sources": "OSINT aggregators, sanitized intelligence summaries", "volume": "40,000 reports", "data_types": "Structured threat indicators, narrative reports, geospatial annotations", "contains_pii": False, "pii_handling": "", "consent_status": "not_applicable", "consent_mechanism": "", "quality_measures": "Reviewed by intelligence analysts", "bias_mitigation": "Sourced from multiple geographic regions and threat types", "copyright_compliance": "Open-source materials with appropriate licensing", "governance_status": "under_review", "reviewed_by": "Jordan Lee", "review_date": "2026-03-20", "notes": "Awaiting final classification review before production use"},
        {"name": "DoD Payment Transaction Logs", "system_id": sids["Trident Financial Monitoring"], "system_name": "Trident Financial Monitoring", "description": "Anonymized transaction logs from DoD supply chain payment systems", "data_sources": "Payment processing system, supply chain finance database", "volume": "2.1M transactions", "data_types": "Transaction amounts, vendor IDs, timestamps, payment methods, fraud flags", "contains_pii": True, "pii_handling": "Vendor names and banking details replaced with pseudonymous IDs", "consent_status": "contractual_necessity", "consent_mechanism": "Processing necessary under vendor payment contract terms", "quality_measures": "Reconciliation with general ledger monthly", "bias_mitigation": "None required — fraud labels are ground truth from investigations", "copyright_compliance": "Internal financial data", "governance_status": "approved", "reviewed_by": "Taylor Reed", "review_date": "2025-12-01", "notes": "Core training set updated monthly with new transactions"},
        {"name": "CUI Document Training Set", "system_id": sids["Trident Document Classifier"], "system_name": "Trident Document Classifier", "description": "Labelled CUI and non-CUI documents for classification model training", "data_sources": "Internal document management system, declassified CUI examples", "volume": "50,000 documents", "data_types": "PDF, DOCX, plain text — labelled with CUI category and handling caveats", "contains_pii": False, "pii_handling": "", "consent_status": "not_applicable", "consent_mechanism": "", "quality_measures": "Double-labelled by trained CUI custodians", "bias_mitigation": "Balanced across all 15 classification categories", "copyright_compliance": "Internal documents and declassified training materials", "governance_status": "approved", "reviewed_by": "Alex Kim", "review_date": "2026-02-28", "notes": "Training set for v0.5 model; expansion to 100K planned for v1.0"},
        {"name": "Subcontractor Risk Profiles", "system_id": sids["Trident Supply Chain Risk Analyzer"], "system_name": "Trident Supply Chain Risk Analyzer", "description": "Historical risk assessment data for DoD subcontractors", "data_sources": "Supplier risk database, financial reports, performance reviews", "volume": "15,000 supplier profiles", "data_types": "Financial health scores, delivery performance, compliance history, risk ratings", "contains_pii": False, "pii_handling": "", "consent_status": "not_applicable", "consent_mechanism": "", "quality_measures": "Quarterly reconciliation with supplier self-assessments", "bias_mitigation": "Multi-factor model reduces reliance on single data source", "copyright_compliance": "Internal supply chain data", "governance_status": "under_review", "reviewed_by": "Morgan Chen", "review_date": "2026-04-10", "notes": "Supplemental data from external credit agencies pending approval"},
        {"name": "Personnel Skills Database", "system_id": sids["Trident Personnel Advisor"], "system_name": "Trident Personnel Advisor", "description": "Anonymized skills, certifications, and career progression records", "data_sources": "HR skills inventory, certification tracking system, performance reviews", "volume": "30,000 personnel records", "data_types": "Skills inventory, certifications, career history, training completions", "contains_pii": True, "pii_handling": "Names replaced with employee IDs; contact info excluded", "consent_status": "explicit", "consent_mechanism": "Employee consent obtained during annual skills assessment", "quality_measures": "Cross-referenced with manager reviews", "bias_mitigation": "Skills taxonomy normalized across all departments", "copyright_compliance": "Internal HR data", "governance_status": "approved", "reviewed_by": "Riley Santos", "review_date": "2025-11-15", "notes": "Primary training set for recommendation model"},
        {"name": "Career Development Records", "system_id": sids["Trident Personnel Advisor"], "system_name": "Trident Personnel Advisor", "description": "Voluntary career development plans and outcomes used for path recommendation training", "data_sources": "Career development platform, mentorship program records", "volume": "8,000 plans", "data_types": "Career goals, development activities, mentor feedback, outcomes", "contains_pii": True, "pii_handling": "De-identified at collection — no direct identifiers stored", "consent_status": "explicit", "consent_mechanism": "Opt-in consent during career planning session", "quality_measures": "Outcome validation at 6-month and 12-month intervals", "bias_mitigation": "Recommendation model penalized for stereotypical career path suggestions", "copyright_compliance": "Internal data", "governance_status": "approved", "reviewed_by": "Riley Santos", "review_date": "2026-01-20", "notes": "Supplemental dataset enhancing recommendation diversity"},
    ]
    for ds in datasets:
        did = _id()
        ds["id"] = did
        ds["created_at"] = now
        ds["updated_at"] = now
        tds_db[did] = ds
    _save("training_datasets", tds_db)

    # ── Seed model versions ───────────────────────────────────────────
    version_data = {
        "Trident Hiring Intelligence": [
            {"version": "2.1.0", "release_date": "2026-04-01", "change_log": "Bias mitigation patch — retrained with stratified curriculum dataset", "status": "staging", "created_by": owner_of["Trident Hiring Intelligence"]},
            {"version": "2.0.0", "release_date": "2026-01-15", "change_log": "Major architecture upgrade to transformer-based ranking model; 15% precision improvement", "status": "production", "created_by": owner_of["Trident Hiring Intelligence"]},
            {"version": "1.0.0", "release_date": "2025-06-01", "change_log": "Initial release — gradient-boosted ranking model", "status": "archived", "created_by": owner_of["Trident Hiring Intelligence"]},
        ],
        "Trident Mission Support Assistant": [
            {"version": "1.0.0", "release_date": "2026-02-01", "change_log": "Initial production release — GPT-4o based assistant with RAG pipeline", "status": "production", "created_by": owner_of["Trident Mission Support Assistant"]},
        ],
        "Trident Financial Monitoring": [
            {"version": "3.2.0", "release_date": "2026-03-01", "change_log": "Added graph neural network for transaction relationship analysis", "status": "production", "created_by": owner_of["Trident Financial Monitoring"]},
            {"version": "3.1.0", "release_date": "2025-11-15", "change_log": "Enhanced feature engineering pipeline; 5% AUC-ROC improvement", "status": "production", "created_by": owner_of["Trident Financial Monitoring"]},
            {"version": "3.0.0", "release_date": "2025-08-01", "change_log": "Complete rewrite — migrated from random forest to XGBoost ensemble", "status": "archived", "created_by": owner_of["Trident Financial Monitoring"]},
        ],
        "Trident Document Classifier": [
            {"version": "0.5.0", "release_date": "2026-04-01", "change_log": "Fine-tuned BERT-based classifier; added CUI category detection", "status": "development", "created_by": owner_of["Trident Document Classifier"]},
            {"version": "0.4.0", "release_date": "2026-02-01", "change_log": "Initial prototype with TF-IDF + SVM baseline classifier", "status": "development", "created_by": owner_of["Trident Document Classifier"]},
        ],
        "Trident Supply Chain Risk Analyzer": [
            {"version": "1.2.0", "release_date": "2026-03-15", "change_log": "Integration with external credit scoring API; added temporal risk decay factor", "status": "staging", "created_by": owner_of["Trident Supply Chain Risk Analyzer"]},
            {"version": "1.1.0", "release_date": "2025-12-01", "change_log": "Improved supplier clustering; added geographic risk overlay", "status": "production", "created_by": owner_of["Trident Supply Chain Risk Analyzer"]},
        ],
        "Trident Personnel Advisor": [
            {"version": "2.0.0", "release_date": "2026-01-10", "change_log": "Multi-modal architecture — skills, career history, and goals jointly embedded", "status": "production", "created_by": owner_of["Trident Personnel Advisor"]},
            {"version": "1.5.0", "release_date": "2025-09-15", "change_log": "Added mentorship matching module", "status": "production", "created_by": owner_of["Trident Personnel Advisor"]},
        ],
    }
    for sys_name, versions in version_data.items():
        if sys_name not in sids:
            continue
        sid = sids[sys_name]
        rec = systems.get(sid)
        if not rec:
            continue
        rec["versions"] = []
        for v in versions:
            entry = {
                "id": uuid4().hex[:8],
                **v,
                "created_at": _now(),
            }
            rec["versions"].append(entry)
        rec["version"] = versions[0]["version"] if versions else ""
        systems[sid] = rec
    _save("systems", systems)

    # ── Seed plans ─────────────────────────────────────────────────
    plan_db = _load("plans")
    plan_db.clear()
    from plan_templates import PLAN_TEMPLATES
    for fw, types in PLAN_TEMPLATES.items():
        for pt, tmpl in types.items():
            pid = _id()
            now = _now()
            plan_db[pid] = {
                "id": pid,
                "name": tmpl["name"],
                "plan_type": pt,
                "framework": fw,
                "description": tmpl.get("description", ""),
                "systems": [],
                "owner": "",
                "status": "draft",
                "due_date": "",
                "content": tmpl.get("content", ""),
                "notes": "",
                "evidence_ids": [],
                "created_at": now,
                "updated_at": now,
            }
    _save("plans", plan_db)

    # ── Seed contracts ──────────────────────────────────────────────
    contract_db = _load("contracts")
    contract_db.clear()
    from contract_templates import CONTRACT_TEMPLATES
    for fw, types in CONTRACT_TEMPLATES.items():
        for ct, tmpl in types.items():
            cid = _id()
            now = _now()
            contract_db[cid] = {
                "id": cid,
                "name": tmpl["name"],
                "contract_type": ct,
                "framework": fw,
                "counterparty": "",
                "description": tmpl.get("description", ""),
                "guidance": tmpl.get("guidance", ""),
                "status": "not_started",
                "expiry_date": "",
                "notes": "",
                "evidence_ids": [],
                "created_at": now,
                "updated_at": now,
            }
    _save("contracts", contract_db)

    # ── Seed competence records ─────────────────────────────────────────
    comp_db = _load("competence")
    comp_db.clear()
    from competence_requirements import REQUIRED_COMPETENCIES
    people = [
        {"name": "Maria Gonzalez", "role": "reviewer"},
        {"name": "Sam Patel", "role": "provider"},
        {"name": "Jordan Lee", "role": "deployer"},
        {"name": "Alex Kim", "role": "operator"},
        {"name": "Taylor Reed", "role": "risk_owner"},
        {"name": "Riley Santos", "role": "deployer"},
        {"name": "Morgan Chen", "role": "provider_repr"},
    ]
    now = _now()
    for person in people:
        reqs = REQUIRED_COMPETENCIES.get(person["role"], [])
        for req in reqs:
            cid = _id()
            import random
            y = random.choice(["2025", "2026"])
            m = f"{random.randint(1, 12):02d}"
            d = f"{random.randint(1, 28):02d}"
            comp_db[cid] = {
                "id": cid,
                "person_name": person["name"],
                "role": person["role"],
                "qualification": req["qualification"],
                "provider": f"{random.choice(['Internal', 'TrainingProvider Inc.', 'ComplianceAcademy', 'EU AI Institute'])}",
                "date_completed": f"{y}-{m}-{d}",
                "expiry_date": f"{int(y) + 2}-{m}-{d}",
                "status": "current",
                "notes": "",
                "created_at": now,
                "updated_at": now,
            }
    _save("competence", comp_db)

    # ── Seed evidence hub (AIGov) ───────────────────────────────────
    from evidence_hub.store import upload_evidence_file, map_evidence

    # Clear only AIGov-mapped evidence (not shared CMMC/SOC2 evidence)
    from evidence_hub.store import _get_db
    _db = _get_db()
    try:
        aigov_ids = _db.execute(
            "SELECT DISTINCT evidence_id FROM evidence_mappings WHERE framework_id = ?",
            ("AIGov",),
        ).fetchall()
        for row in aigov_ids:
            eid = row[0]
            _db.execute("DELETE FROM evidence_mappings WHERE evidence_id = ?", (eid,))
            _db.execute("DELETE FROM evidence WHERE id = ?", (eid,))
        _db.execute("DELETE FROM evidence_requests WHERE framework_id = ?", ("AIGov",))
        _db.commit()
    finally:
        _db.close()

    seed_evidence = [
        {
            "name": "EU AI Act Conformity Assessment — Hiring Intelligence",
            "filename": "eu-conformity-hiring.pdf",
            "mime_type": "application/pdf",
            "content": "CONFORMITY ASSESSMENT: Trident Hiring Intelligence — EU AI Act Art. 19\nDate: 2026-04-15\nAssessor: Maria Gonzalez\nStatus: Compliant — all high-risk requirements satisfied.\nDocumented: Risk management (Art.9), data governance (Art.10), technical docs (Art.11), records (Art.12), transparency (Art.13), human oversight (Art.14).",
            "tags": ["conformity", "eu-ai-act"],
            "evidence_type": "audit_report",
            "display_title": "EU AI Act Conformity Assessment — Hiring Intelligence",
            "evidence_version": "1.0",
            "mappings": [("AIGov", "Art.19"), ("AIGov", "Art.9"), ("AIGov", "Art.10")],
        },
        {
            "name": "NIST AI RMF Risk Assessment — Financial Monitoring",
            "filename": "nist-rmf-financial.pdf",
            "mime_type": "application/pdf",
            "content": "NIST AI RMF RISK ASSESSMENT: Trident Financial Monitoring\nDate: 2026-03-01\nAssessor: Taylor Reed\nGOVERN: Governance framework established, roles assigned.\nMAP: Context documented, risks identified.\nMEASURE: Metrics defined, bias testing complete.\nMANAGE: Treatment plan active, monitoring quarterly.",
            "tags": ["risk-assessment", "nist-rmf"],
            "evidence_type": "audit_report",
            "display_title": "NIST AI RMF Risk Assessment — Financial Monitoring",
            "evidence_version": "1.0",
            "mappings": [("AIGov", "GOV.1"), ("AIGov", "MAP.1"), ("AIGov", "MEASURE.1"), ("AIGov", "MANAGE.1")],
        },
        {
            "name": "ISO 42001 QMS Documentation — Mission Support",
            "filename": "iso42001-qms-mission.pdf",
            "mime_type": "application/pdf",
            "content": "ISO 42001 QUALITY MANAGEMENT SYSTEM: Trident Mission Support Assistant\nDate: 2026-02-15\nContext (Clause 4): Mission planning domain.\nLeadership (Clause 5): AI governance policy approved.\nPlanning (Clause 6): Risks and opportunities identified.\nSupport (Clause 7): Competence and awareness program active.\nOperation (Clause 8): Operational controls documented.\nPerformance (Clause 9): Monitoring and measurement defined.\nImprovement (Clause 10): Nonconformity processes established.",
            "tags": ["qms", "iso-42001"],
            "evidence_type": "policy",
            "display_title": "ISO 42001 QMS Documentation — Mission Support Assistant",
            "evidence_version": "1.0",
            "mappings": [("AIGov", "A.5"), ("AIGov", "A.7"), ("AIGov", "A.9")],
        },
        {
            "name": "Bias Audit Report — Hiring Intelligence",
            "filename": "bias-audit-hiring.pdf",
            "mime_type": "application/pdf",
            "content": "BIAS AUDIT REPORT: Trident Hiring Intelligence\nDate: 2026-03-15\nMethodology: Disparate impact analysis across demographic groups\nResult: Statistical parity difference 0.03 — within threshold\nMitigations: Name-based filter identified, mitigated in v2.2.0\nNext audit: Quarterly",
            "tags": ["bias", "fairness"],
            "evidence_type": "audit_report",
            "display_title": "Bias Audit Report — Hiring Intelligence",
            "evidence_version": "1.0",
            "mappings": [("AIGov", "Art.10"), ("AIGov", "MEASURE.1")],
        },
        {
            "name": "Incident Response Log — Drift Detection",
            "filename": "incident-drift-log.pdf",
            "mime_type": "application/pdf",
            "content": "INCIDENT LOG: Runtime Drift — Trident Hiring Intelligence\nReported: 2026-06-28 by Alice\nType: Performance drift\nSeverity: Medium\nStatus: Investigating\nActions: Model input distribution shift detected. Root cause analysis in progress.",
            "tags": ["incident", "monitoring"],
            "evidence_type": "audit_report",
            "display_title": "Incident Response Log — Drift Detection",
            "evidence_version": "1.0",
            "mappings": [("AIGov", "Art.20"), ("AIGov", "Art.21"), ("AIGov", "A.10")],
        },
        {
            "name": "Technical Documentation — Financial Monitoring v3.2",
            "filename": "tech-docs-financial-v3.2.pdf",
            "mime_type": "application/pdf",
            "content": "TECHNICAL DOCUMENTATION: Trident Financial Monitoring v3.2\nArchitecture: Graph neural network on transaction graph\nTraining data: 2.1M DoD payment transactions\nFeatures: Amount, vendor, timestamp, payment method, fraud flags\nMetrics: AUC-ROC 0.94\nDeployment: Production — us-east-1\nMonitoring: Real-time dashboard + weekly drift reports",
            "tags": ["technical", "documentation"],
            "evidence_type": "diagram",
            "display_title": "Technical Documentation — Financial Monitoring v3.2",
            "evidence_version": "3.2",
            "mappings": [("AIGov", "Art.11"), ("AIGov", "A.8")],
        },
        {
            "name": "Training Data Governance Record — Resume Database",
            "filename": "data-governance-resume.pdf",
            "mime_type": "application/pdf",
            "content": "DATA GOVERNANCE: Resume Database — Trident Hiring Intelligence\nVolume: 85,000 records\nSources: ATS, clearance DB\nPII: Masked at ingestion\nConsent: Explicit — collected during application\nQuality: Deduplication, normalization, missing field tagging\nBias mitigation: Stratified sampling by clearance level\nRetention: 3 years after last interaction",
            "tags": ["data-governance", "training-data"],
            "evidence_type": "policy",
            "display_title": "Training Data Governance Record — Resume Database",
            "evidence_version": "1.0",
            "mappings": [("AIGov", "Art.10"), ("AIGov", "Art.13"), ("AIGov", "MEASURE.2")],
        },
    ]

    for item in seed_evidence:
        data = item["content"].encode("utf-8")
        ev = upload_evidence_file(
            name=item["name"],
            file_data=data,
            filename=item["filename"],
            tags=item["tags"],
            uploaded_by="demo@khestra.dev",
            mime_type=item["mime_type"],
            evidence_type=item.get("evidence_type", ""),
            display_title=item.get("display_title", ""),
            evidence_version=item.get("evidence_version", ""),
        )
        eid = ev.get("id", "")
        if eid:
            for fw_id, ctrl_id in item["mappings"]:
                map_evidence(eid, fw_id, ctrl_id, mapped_by="demo@khestra.dev")

    _audit_log("created", "seed", "all", {"count": len(samples)})
    return {"ok": True, "count": len(samples), "existing_before": existing_count}

@app.post("/api/clear")
def clear_data(confirm: bool = False):
    _require_edit_controls()
    if not confirm:
        raise HTTPException(status_code=400, detail="Pass ?confirm=true to delete all data")
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    for fname in files:
        os.remove(os.path.join(DATA_DIR, fname))
    _audit_log("deleted", "all_data", "", {"files": len(files)})
    return {"ok": True, "files_deleted": len(files)}

app.include_router(ccf_router)
app.include_router(remediation_router)
app.include_router(policy_router)
app.include_router(orgs_router)
app.include_router(raci_router)
app.include_router(audit_router)
app.include_router(testing_router)
app.include_router(findings_router)
app.include_router(audit_center_router)
# ── Shared entity routers (framework lens) ─────────────────────────────
# These mount the SHARED global data (policies/risks/assets/vendors/incidents/
# evidence/collectors) under this framework's prefix. The data lives in the
# shared DBs owned by the Core service (/api/core); these mounts are the
# framework-scoped views on it (framework_id-filtered reads + scoped writes).
# Global pages call /api/core directly. See ARCHITECTURE.md "Core tier".
app.include_router(conformity_router)
app.include_router(fria_router)
app.include_router(tabletop_router)

# ─── Evaluations ──────────────────────────────────────

EVALUATION_TYPES = ["accuracy", "robustness", "bias", "cybersecurity", "fairness", "performance", "red_team", "hallucination", "human_review", "conformity", "internal_audit"]

@app.get("/api/evaluations")
def list_evaluations(system_id: str | None = Query(None), evaluation_type: str | None = Query(None), status: str | None = Query(None)):
    db = _load("evaluations")
    items = list(db.values())
    if system_id:
        items = [e for e in items if e.get("system_id") == system_id]
    if evaluation_type:
        items = [e for e in items if e.get("evaluation_type") == evaluation_type]
    if status:
        items = [e for e in items if e.get("status") == status]
    items.sort(key=lambda x: x.get("test_date", x.get("created_at", "")), reverse=True)
    return {"evaluations": items, "total": len(items)}

@app.post("/api/evaluations")
def create_evaluation(data: EvaluationCreate):
    _require_edit_controls()
    db = _load("evaluations")
    eid = _id()
    now = _now()
    record = data.model_dump()
    record["id"] = eid
    record["created_at"] = now
    record["updated_at"] = now
    db[eid] = record
    _save("evaluations", db)
    _audit_log("created", "evaluation", eid, {"name": data.name})
    return {"id": eid}

@app.get("/api/evaluations/{eid}")
def get_evaluation(eid: str):
    db = _load("evaluations")
    if eid not in db:
        raise HTTPException(404, "Evaluation not found")
    return {"evaluation": db[eid]}

@app.patch("/api/evaluations/{eid}")
def update_evaluation(eid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("evaluations")
    if eid not in db:
        raise HTTPException(404, "Evaluation not found")
    record = db[eid]
    old = {"status": record.get("status"), "score": record.get("score")}
    for k, v in data.items():
        if v is not None and k not in ("id", "created_at"):
            record[k] = v
    record["updated_at"] = _now()
    db[eid] = record
    _save("evaluations", db)
    field_diffs = {}
    for field in ("status", "score"):
        if field in data and old[field] != record.get(field):
            field_diffs[field] = {"old": old[field], "new": record.get(field)}
    details = {"status": record.get("status")}
    if field_diffs:
        details["field_diffs"] = field_diffs
    _audit_log("updated", "evaluation", eid, details)
    return {"evaluation": record}

@app.delete("/api/evaluations/{eid}")
def delete_evaluation(eid: str):
    _require_edit_controls()
    db = _load("evaluations")
    if eid not in db:
        raise HTTPException(404, "Evaluation not found")
    name = db[eid].get("name", "")
    del db[eid]
    _save("evaluations", db)
    _audit_log("deleted", "evaluation", eid, {"name": name})
    return {"ok": True}

# ─── Training Data Provenance ──────────────────────────

CONSENT_STATUSES = ["not_applicable", "explicit", "implicit", "opt_out", "legitimate_interest", "contractual_necessity"]
GOVERNANCE_STATUSES = ["draft", "under_review", "approved", "rejected", "needs_update"]

@app.get("/api/training-datasets")
def list_training_datasets(system_id: str | None = Query(None), governance_status: str | None = Query(None), contains_pii: bool | None = Query(None)):
    db = _load("training_datasets")
    items = list(db.values())
    if system_id:
        items = [d for d in items if d.get("system_id") == system_id]
    if governance_status:
        items = [d for d in items if d.get("governance_status") == governance_status]
    if contains_pii is not None:
        items = [d for d in items if d.get("contains_pii") == contains_pii]
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"datasets": items, "total": len(items)}

@app.post("/api/training-datasets")
def create_training_dataset(data: TrainingDatasetCreate):
    _require_edit_controls()
    db = _load("training_datasets")
    did = _id()
    now = _now()
    record = data.model_dump()
    record["id"] = did
    record["created_at"] = now
    record["updated_at"] = now
    db[did] = record
    _save("training_datasets", db)
    _audit_log("created", "training_dataset", did, {"name": data.name})
    return {"id": did}

@app.get("/api/training-datasets/{did}")
def get_training_dataset(did: str):
    db = _load("training_datasets")
    if did not in db:
        raise HTTPException(404, "Training dataset not found")
    return {"dataset": db[did]}

@app.patch("/api/training-datasets/{did}")
def update_training_dataset(did: str, data: dict = {}):
    _require_edit_controls()
    db = _load("training_datasets")
    if did not in db:
        raise HTTPException(404, "Training dataset not found")
    record = db[did]
    for k, v in data.items():
        if v is not None and k not in ("id", "created_at"):
            record[k] = v
    record["updated_at"] = _now()
    db[did] = record
    _save("training_datasets", db)
    _audit_log("updated", "training_dataset", did, {"name": record.get("name")})
    return {"dataset": record}

@app.delete("/api/training-datasets/{did}")
def delete_training_dataset(did: str):
    _require_edit_controls()
    db = _load("training_datasets")
    if did not in db:
        raise HTTPException(404, "Training dataset not found")
    name = db[did].get("name", "")
    del db[did]
    _save("training_datasets", db)
    _audit_log("deleted", "training_dataset", did, {"name": name})
    return {"ok": True}

# ─── Plans ─────────────────────────────────────────────

PLAN_STATUSES = ["draft", "under_review", "approved", "archived"]

@app.get("/api/plans")
def list_plans(framework: str | None = Query(None), status: str | None = Query(None), plan_type: str | None = Query(None)):
    db = _load("plans")
    items = list(db.values())
    if framework:
        items = [p for p in items if p.get("framework") == framework]
    if status:
        items = [p for p in items if p.get("status") == status]
    if plan_type:
        items = [p for p in items if p.get("plan_type") == plan_type]
    items.sort(key=lambda x: x.get("due_date", x.get("created_at", "")), reverse=True)
    from plan_templates import PLAN_TEMPLATES
    plan_defs = {t: PLAN_TEMPLATES.get(fw, {}).get(t, {}) for fw in PLAN_TEMPLATES for t in PLAN_TEMPLATES[fw]}
    return {"plans": items, "total": len(items), "plan_types": plan_defs}

@app.get("/api/plans/types")
def list_plan_types():
    from plan_templates import PLAN_TEMPLATES
    return {"plan_types": PLAN_TEMPLATES}

@app.post("/api/plans")
def create_plan(data: PlanCreate):
    _require_edit_controls()
    db = _load("plans")
    pid = _id()
    now = _now()
    record = data.model_dump()
    record["id"] = pid
    record["created_at"] = now
    record["updated_at"] = now
    db[pid] = record
    _save("plans", db)
    _audit_log("created", "plan", pid, {"name": data.name})
    return {"id": pid, "plan": record}

@app.get("/api/plans/{pid}")
def get_plan(pid: str):
    db = _load("plans")
    if pid not in db:
        raise HTTPException(404, "Plan not found")
    return {"plan": db[pid]}

@app.patch("/api/plans/{pid}")
def update_plan(pid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("plans")
    if pid not in db:
        raise HTTPException(404, "Plan not found")
    record = db[pid]
    old_status = record.get("status")
    for k, v in data.items():
        if v is not None and k not in ("id", "created_at"):
            record[k] = v
    record["updated_at"] = _now()
    db[pid] = record
    _save("plans", db)
    details = {"name": record.get("name")}
    if "status" in data and old_status != record.get("status"):
        details["field_diffs"] = {"status": {"old": old_status, "new": record.get("status")}}
    _audit_log("updated", "plan", pid, details)
    return {"plan": record}

@app.delete("/api/plans/{pid}")
def delete_plan(pid: str):
    _require_edit_controls()
    db = _load("plans")
    if pid not in db:
        raise HTTPException(404, "Plan not found")
    name = db[pid].get("name", "")
    del db[pid]
    _save("plans", db)
    _audit_log("deleted", "plan", pid, {"name": name})
    return {"ok": True}

@app.post("/api/plans/seed")
def seed_plans():
    _require_edit_controls()
    db = _load("plans")
    from plan_templates import PLAN_TEMPLATES
    count = 0
    for fw, types in PLAN_TEMPLATES.items():
        for pt, tmpl in types.items():
            pid = _id()
            now = _now()
            db[pid] = {
                "id": pid,
                "name": tmpl["name"],
                "plan_type": pt,
                "framework": fw,
                "description": tmpl.get("description", ""),
                "systems": [],
                "owner": "",
                "status": "draft",
                "due_date": "",
                "content": tmpl.get("content", ""),
                "notes": "",
                "evidence_ids": [],
                "created_at": now,
                "updated_at": now,
            }
            count += 1
    _save("plans", db)
    _audit_log("created", "plans_seed", "all", {"count": count})
    return {"ok": True, "count": count}

# ─── Contracts ─────────────────────────────────────────

CONTRACT_STATUSES = ["not_started", "in_progress", "signed", "expired"]

@app.get("/api/contracts")
def list_contracts(framework: str | None = Query(None), status: str | None = Query(None), contract_type: str | None = Query(None)):
    db = _load("contracts")
    items = list(db.values())
    if framework:
        items = [c for c in items if c.get("framework") == framework]
    if status:
        items = [c for c in items if c.get("status") == status]
    if contract_type:
        items = [c for c in items if c.get("contract_type") == contract_type]
    items.sort(key=lambda x: x.get("expiry_date", x.get("created_at", "")))
    return {"contracts": items, "total": len(items)}

@app.get("/api/contracts/types")
def list_contract_types():
    from contract_templates import CONTRACT_TEMPLATES
    return {"contract_types": CONTRACT_TEMPLATES}

@app.post("/api/contracts")
def create_contract(data: ContractCreate):
    _require_edit_controls()
    db = _load("contracts")
    cid = _id()
    now = _now()
    record = data.model_dump()
    record["id"] = cid
    record["created_at"] = now
    record["updated_at"] = now
    db[cid] = record
    _save("contracts", db)
    _audit_log("created", "contract", cid, {"name": data.name})
    return {"id": cid, "contract": record}

@app.get("/api/contracts/{cid}")
def get_contract(cid: str):
    db = _load("contracts")
    if cid not in db:
        raise HTTPException(404, "Contract not found")
    return {"contract": db[cid]}

@app.patch("/api/contracts/{cid}")
def update_contract(cid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("contracts")
    if cid not in db:
        raise HTTPException(404, "Contract not found")
    record = db[cid]
    for k, v in data.items():
        if v is not None and k not in ("id", "created_at"):
            record[k] = v
    record["updated_at"] = _now()
    db[cid] = record
    _save("contracts", db)
    _audit_log("updated", "contract", cid, {"name": record.get("name")})
    return {"contract": record}

@app.delete("/api/contracts/{cid}")
def delete_contract(cid: str):
    _require_edit_controls()
    db = _load("contracts")
    if cid not in db:
        raise HTTPException(404, "Contract not found")
    name = db[cid].get("name", "")
    del db[cid]
    _save("contracts", db)
    _audit_log("deleted", "contract", cid, {"name": name})
    return {"ok": True}

@app.post("/api/contracts/seed")
def seed_contracts():
    _require_edit_controls()
    db = _load("contracts")
    from contract_templates import CONTRACT_TEMPLATES
    count = 0
    for fw, types in CONTRACT_TEMPLATES.items():
        for ct, tmpl in types.items():
            cid = _id()
            now = _now()
            db[cid] = {
                "id": cid,
                "name": tmpl["name"],
                "contract_type": ct,
                "framework": fw,
                "counterparty": "",
                "description": tmpl.get("description", ""),
                "guidance": tmpl.get("guidance", ""),
                "status": "not_started",
                "expiry_date": "",
                "notes": "",
                "evidence_ids": [],
                "created_at": now,
                "updated_at": now,
            }
            count += 1
    _save("contracts", db)
    _audit_log("created", "contracts_seed", "all", {"count": count})
    return {"ok": True, "count": count}


# ─── Contract File Attachments ──────────────────────────


@app.post("/api/contracts/{cid}/upload")
async def upload_contract_file(cid: str, file: UploadFile = File(...), label: str = Form("")):
    _require_edit_controls()
    db = _load("contracts")
    if cid not in db:
        raise HTTPException(404, "Contract not found")
    ext = os.path.splitext(file.filename or "file")[1].lower()
    if ext not in {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".xlsx", ".txt", ".csv", ".md"}:
        raise HTTPException(400, f"Extension '{ext}' not allowed")
    data = await file.read()
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(400, "File exceeds 25 MB limit")
    fid = uuid4().hex[:12]
    fname = f"{cid}_{fid}{ext}"
    dest = os.path.join(CONTRACT_FILES_DIR, fname)
    with open(dest, "wb") as f:
        f.write(data)
    entry = {
        "id": fid,
        "filename": file.filename or fname,
        "label": label or file.filename or fname,
        "size": len(data),
        "uploaded_at": _now(),
    }
    record = db[cid]
    record.setdefault("attachments", []).append(entry)
    record["updated_at"] = _now()
    db[cid] = record
    _save("contracts", db)
    _audit_log("created", "contract_file", cid, {"fid": fid, "filename": file.filename})
    return {"attachment": entry}


@app.get("/api/contracts/{cid}/files/{fid}")
def download_contract_file(cid: str, fid: str):
    db = _load("contracts")
    if cid not in db:
        raise HTTPException(404, "Contract not found")
    record = db[cid]
    for att in record.get("attachments", []):
        if att["id"] == fid:
            fname = f"{cid}_{fid}{os.path.splitext(att['filename'])[1]}"
            path = os.path.join(CONTRACT_FILES_DIR, fname)
            if not os.path.exists(path):
                raise HTTPException(404, "File not found on disk")
            with open(path, "rb") as f:
                return Response(
                    f.read(),
                    media_type="application/octet-stream",
                    headers={"Content-Disposition": f'attachment; filename="{att["filename"]}"'},
                )
    raise HTTPException(404, "Attachment not found")


@app.delete("/api/contracts/{cid}/files/{fid}")
def delete_contract_file(cid: str, fid: str):
    _require_edit_controls()
    db = _load("contracts")
    if cid not in db:
        raise HTTPException(404, "Contract not found")
    record = db[cid]
    for i, att in enumerate(record.get("attachments", [])):
        if att["id"] == fid:
            fname = f"{cid}_{fid}{os.path.splitext(att['filename'])[1]}"
            path = os.path.join(CONTRACT_FILES_DIR, fname)
            if os.path.exists(path):
                os.remove(path)
            record["attachments"].pop(i)
            record["updated_at"] = _now()
            db[cid] = record
            _save("contracts", db)
            _audit_log("deleted", "contract_file", cid, {"fid": fid})
            return {"status": "deleted"}
    raise HTTPException(404, "Attachment not found")


# ─── Competence / Certification Tracking ─────────────────────────────────

@app.get("/api/competence")
def list_competence(role: Optional[str] = Query(None)):
    db = _load("competence")
    records = list(db.values())
    if role:
        records = [r for r in records if r.get("role") == role]
    return {"competence": sorted(records, key=lambda r: r.get("person_name", "")), "total": len(records)}

@app.get("/api/competence/roles")
def get_competence_roles():
    from competence_requirements import REQUIRED_COMPETENCIES
    from refs.format import display_clause

    return {"roles": {
        role: [{**r, "ref": display_clause(r["framework"], r["ref"])} for r in requirements]
        for role, requirements in REQUIRED_COMPETENCIES.items()
    }}

@app.get("/api/competence/gaps")
def get_competence_gaps():
    from competence_requirements import REQUIRED_COMPETENCIES
    from refs.format import display_clause

    db = _load("competence")
    records = list(db.values())
    gaps = []
    for role, requirements in REQUIRED_COMPETENCIES.items():
        people = [r for r in records if r.get("role") == role]
        for req in requirements:
            has = [p for p in people if p.get("qualification") == req["qualification"] and p.get("status") in ("current", "expiring")]
            if not has:
                gaps.append({
                    "role": role,
                    "qualification": req["qualification"],
                    "framework": req["framework"],
                    "ref": display_clause(req["framework"], req["ref"]),
                    "description": req["description"],
                })
    return {"gaps": sorted(gaps, key=lambda g: (g["role"], g["qualification"]))}

@app.post("/api/competence")
def create_competence(data: dict = {}):
    _require_edit_controls()
    db = _load("competence")
    cid = _id()
    now = _now()
    rec = {
        "id": cid,
        "person_name": data.get("person_name", ""),
        "role": data.get("role", ""),
        "qualification": data.get("qualification", ""),
        "provider": data.get("provider", ""),
        "date_completed": data.get("date_completed", ""),
        "expiry_date": data.get("expiry_date", ""),
        "status": data.get("status", "current"),
        "notes": data.get("notes", ""),
        "created_at": now,
        "updated_at": now,
    }
    db[cid] = rec
    _save("competence", db)
    _audit_log("created", "competence", cid, {"person": data.get("person_name"), "qualification": data.get("qualification")})
    return {"competence": rec}

@app.patch("/api/competence/{cid}")
def update_competence(cid: str, data: dict = {}):
    _require_edit_controls()
    db = _load("competence")
    if cid not in db:
        raise HTTPException(404, "Competence record not found")
    rec = db[cid]
    for k, v in data.items():
        if v is not None and k not in ("id", "created_at"):
            rec[k] = v
    rec["updated_at"] = _now()
    db[cid] = rec
    _save("competence", db)
    _audit_log("updated", "competence", cid, {"status": rec.get("status")})
    return {"competence": rec}

@app.delete("/api/competence/{cid}")
def delete_competence(cid: str):
    _require_edit_controls()
    db = _load("competence")
    if cid not in db:
        raise HTTPException(404, "Competence record not found")
    del db[cid]
    _save("competence", db)
    _audit_log("deleted", "competence", cid)
    return {"ok": True}

# ─── Collector endpoints ──────────────────────────────────


@app.get("/api/collectors")
def get_collectors():
    return {
        "connectors": list_connectors(),
        "monitoring": {"connectors": [], "due_connectors": [], "recent_runs": recent_runs()},
        "drift_events": get_events(limit=25),
        "freshness": {"stale_check_count": 0, "stale_control_count": 0, "checks": [], "controls": [], "stale_checks": [], "stale_controls": []},
        "recent_runs": recent_runs(),
    }


@app.put("/api/collectors/{connector_id}/credentials")
def save_collector_credentials(connector_id: str, body: dict = {}):
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    _require_edit_controls()
    meta = CONNECTOR_CATALOG[connector_id]
    creds = body.get("credentials", {})
    missing = [f for f in meta["required_fields"] if not creds.get(f)]
    if missing:
        raise HTTPException(400, f"Missing required fields: {', '.join(missing)}")
    save_credentials(connector_id, creds)
    _audit_log("saved", "collector_credentials", connector_id, {"fields": list(creds.keys()), "security": True})
    return credentials_status(connector_id, meta["required_fields"])


@app.patch("/api/collectors/{connector_id}/schedule")
def patch_collector_schedule(connector_id: str, body: dict = {}):
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    _require_edit_controls()
    state = patch_monitor_schedule(
        connector_id,
        enabled=body.get("enabled", False),
        interval=body.get("interval", "manual"),
        attach_on_run=body.get("attach_on_run", True),
    )
    _audit_log("updated", "collector_schedule", connector_id)
    return state.to_dict() if hasattr(state, 'to_dict') else {"connector_id": connector_id, "enabled": state.enabled, "interval": state.interval}


@app.post("/api/collectors/{connector_id}/run")
def run_collector(connector_id: str, body: dict = {}):
    if connector_id not in CONNECTOR_CATALOG:
        raise HTTPException(404, "Connector not found")
    _require_edit_controls()
    _audit_log("run", "collector", connector_id)
    if body.get("attach", False):
        try:
            result = run_and_attach_ai(connector_id, use_fixture=body.get("use_fixture", False))
            return {"run": result.run.to_dict() if hasattr(result.run, 'to_dict') else {"status": result.run.status}, "attached": result.attached, "drift_events": result.drift_events}
        except Exception as exc:
            raise HTTPException(400, f"Collector run failed: {exc}")
    run = run_collector_engine(connector_id, use_fixture=body.get("use_fixture", False))
    return {"run": run.to_dict() if hasattr(run, 'to_dict') else {"status": run.status}, "attached": [], "drift_events": []}


@app.post("/api/collectors/monitoring/run-due")
def run_due_collectors(body: dict = {}):
    _require_edit_controls()
    _audit_log("run_due", "scheduler", "")
    try:
        from soc2_collectors.scheduler import run_due_connectors
        result = run_due_connectors(client_id=DEFAULT_CLIENT_ID, use_fixture_if_unconfigured=body.get("use_fixture_if_unconfigured", False))
        return {"ran_count": result.get("ran_count", 0), "due_count": result.get("due_count", 0), "results": result.get("results", [])}
    except Exception as exc:
        return {"ran_count": 0, "due_count": 0, "results": [], "error": str(exc)}

@app.get("/api/help")
def get_help():
    return {"views": {}, "faq": []}

@app.get("/api/webhooks")
def get_webhooks():
    return {"collectors": [], "env_token_configured": False, "ingest_url": ""}

@app.post("/api/webhooks")
def create_webhook(body: dict = {}):
    _require_edit_controls()
    _audit_log("created", "webhook", "", {"name": body.get("name"), "security": True})
    return {"collector": {"id": "", "name": "", "webhook_token": None, "configured": False}, "usage": ""}

@app.delete("/api/webhooks/{collector_id}")
def delete_webhook(collector_id: str):
    _require_edit_controls()
    _audit_log("deleted", "webhook", collector_id, {"security": True})
    return {"ok": True}
