from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class PersonCreateBody(BaseModel):
    name: str = ""
    email: str = ""
    role: str = ""
    department: str = ""
    org_id: str = ""
    workspace_id: str = ""
    frameworks: list[str] = []
    external_id: str = ""
    phone: str = ""
    location: str = ""
    manager: str = ""
    employee_id: str = ""
    provider: str = ""
    raw_attributes: str = ""
    mfa_status: str = ""
    last_login: str = ""
    is_privileged: bool = False


class PersonUpdateBody(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    frameworks: Optional[list[str]] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    manager: Optional[str] = None
    employee_id: Optional[str] = None
    external_id: Optional[str] = None
    provider: Optional[str] = None
    mfa_status: Optional[str] = None
    last_login: Optional[str] = None
    is_privileged: Optional[bool] = None


@router.get("/api/personnel")
def list_personnel(org_id: Optional[str] = Query(None), framework_id: Optional[str] = Query(None)):
    from .store import list_personnel
    return {"personnel": list_personnel(org_id=org_id, framework_id=framework_id)}


@router.post("/api/personnel")
def create_person(body: PersonCreateBody):
    from .store import create_person
    person = create_person(
        name=body.name,
        email=body.email,
        role=body.role,
        department=body.department,
        org_id=body.org_id,
        workspace_id=body.workspace_id,
        frameworks=body.frameworks,
        external_id=body.external_id,
        phone=body.phone,
        location=body.location,
        manager=body.manager,
        employee_id=body.employee_id,
        provider=body.provider,
        raw_attributes=body.raw_attributes,
        mfa_status=body.mfa_status,
        last_login=body.last_login,
        is_privileged=body.is_privileged,
    )

    try:
        from training.store import auto_assign_for_person
        auto_assign_for_person(person["id"])
    except Exception:
        pass

    return {"person": person}


@router.get("/api/personnel/{pid}")
def get_person(pid: str):
    from .store import get_person
    p = get_person(pid)
    if not p:
        raise HTTPException(404, "Person not found")
    return {"person": p}


@router.patch("/api/personnel/{pid}")
def update_person(pid: str, body: PersonUpdateBody):
    from .store import update_person
    p = update_person(pid, **body.model_dump(exclude_none=True))
    if not p:
        raise HTTPException(404, "Person not found")
    return {"person": p}


@router.delete("/api/personnel/{pid}")
def delete_person(pid: str):
    from .store import delete_person
    if not delete_person(pid):
        raise HTTPException(404, "Person not found")
    return {"status": "deleted"}


PROVIDER_CONFIG: dict[str, dict] = {
    "entra": {
        "label": "Microsoft Entra ID",
        "fields": [
            {"key": "tenant_id", "label": "Tenant ID", "is_secret": False, "placeholder": "00000000-0000-0000-0000-000000000000"},
            {"key": "client_id", "label": "Client ID", "is_secret": False, "placeholder": "00000000-0000-0000-0000-000000000000"},
            {"key": "client_secret", "label": "Client Secret", "is_secret": True, "placeholder": "Enter secret"},
        ],
    },
    "okta": {
        "label": "Okta",
        "fields": [
            {"key": "domain", "label": "Okta Domain", "is_secret": False, "placeholder": "dev-123456.okta.com"},
            {"key": "api_token", "label": "API Token", "is_secret": True, "placeholder": "Enter API token"},
        ],
    },
    "scim": {
        "label": "SCIM 2.0",
        "fields": [
            {"key": "endpoint", "label": "Endpoint URL", "is_secret": False, "placeholder": "https://idp.example.com/scim/v2/Users"},
            {"key": "token", "label": "Bearer Token", "is_secret": True, "placeholder": "Enter bearer token"},
        ],
    },
}


@router.get("/api/settings/{provider}")
def get_provider_settings(provider: str):
    from .settings_store import get_setting
    config = PROVIDER_CONFIG.get(provider)
    if not config:
        return {"ok": False, "error": f"Unknown provider: {provider}"}
    result = {}
    for field in config["fields"]:
        key = f"{provider}_{field['key']}"
        val = get_setting(key) or ""
        if field["is_secret"]:
            result[f"has_{field['key']}"] = bool(val)
            result[field["key"]] = ""
        else:
            result[field["key"]] = val
    return {"ok": True, "config": result, "schema": config}


@router.put("/api/settings/{provider}")
def set_provider_settings(provider: str, body: dict = Body()):
    from .settings_store import set_setting, delete_setting
    config = PROVIDER_CONFIG.get(provider)
    if not config:
        return {"ok": False, "error": f"Unknown provider: {provider}"}
    for field in config["fields"]:
        key = f"{provider}_{field['key']}"
        val = (body.get(field["key"]) or "").strip()
        if val:
            set_setting(key, val)
        elif field.get("is_secret"):
            continue
        else:
            delete_setting(key)
    return {"ok": True}


@router.post("/api/settings/{provider}/test")
def test_provider_config(provider: str):
    config = PROVIDER_CONFIG.get(provider)
    if not config:
        return {"ok": False, "error": f"Unknown provider: {provider}"}

    if provider == "entra":
        from .entra_import import get_credentials as _get_creds
        from .entra_import import _get_token as _acquire_token
        tid, cid, secret = _get_creds()
        if not tid or not cid or not secret:
            return {"ok": False, "error": "Entra ID not configured."}
        token, err = _acquire_token()
        if not token:
            return {"ok": False, "error": err or "Connection failed \u2014 check your credentials."}
        return {"ok": True, "error": None}
    elif provider == "okta":
        from .okta_import import get_credentials as _get_creds
        domain, token = _get_creds()
        if not domain or not token:
            return {"ok": False, "error": "Okta not configured."}
        import urllib.request, urllib.error, json
        url = f"https://{domain}/api/v1/users?limit=1"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"SSWS {token}")
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                count = len(json.loads(resp.read()))
                return {"ok": True, "error": None, "users": count}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:500]
            return {"ok": False, "error": f"HTTP {e.code}: {detail}"}
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            return {"ok": False, "error": "Connection failed — check your endpoint URL."}
    elif provider == "scim":
        from .scim_import import get_credentials as _get_creds
        endpoint, token = _get_creds()
        if not endpoint or not token:
            return {"ok": False, "error": "SCIM not configured."}
        import urllib.request, urllib.error, json
        req = urllib.request.Request(endpoint)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/scim+json, application/json")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = json.loads(resp.read())
                count = len(body.get("Resources", []))
                return {"ok": True, "error": None, "users": count}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:500]
            return {"ok": False, "error": f"HTTP {e.code}: {detail}"}
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            return {"ok": False, "error": "Connection failed — check your endpoint URL."}
    else:
        return {"ok": False, "error": f"Unknown provider: {provider}"}


@router.post("/api/personnel/import/{provider}")
def import_from_provider(provider: str, org_id: str = "", workspace_id: str = ""):
    if provider == "entra":
        from .entra_import import import_users
    elif provider == "okta":
        from .okta_import import import_users
    elif provider == "scim":
        from .scim_import import import_users
    else:
        return {"ok": False, "count": 0, "error": f"Unknown provider: {provider}"}
    return import_users(org_id=org_id, workspace_id=workspace_id)
