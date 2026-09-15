import json
import os
import sqlite3
import urllib.request
import urllib.parse
import urllib.error


def get_credentials() -> tuple[str, str]:
    endpoint = token = ""
    try:
        from .settings_store import get_setting
        endpoint = get_setting("scim_endpoint") or ""
        token = get_setting("scim_token") or ""
    except (ImportError, sqlite3.Error) as e:
        import logging
        logging.getLogger("personnel.scim").warning("Failed to read SCIM settings from DB: %s", e)
    if not endpoint:
        endpoint = os.environ.get("SCIM_ENDPOINT") or ""
    if not token:
        token = os.environ.get("SCIM_TOKEN") or ""
    return endpoint, token


def _scim_get(endpoint: str, token: str) -> tuple[list[dict], bool, str | None]:
    all_results = []
    url: str | None = endpoint
    fetch_complete = True
    last_error = None
    while url:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/scim+json, application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read())
                resources = body.get("Resources", [])
                all_results.extend(resources)
                total = body.get("totalResults", 0)
                start = body.get("startIndex", 1)
                per_page = body.get("itemsPerPage", len(resources))
                if per_page and per_page > 0 and start + per_page - 1 < total:
                    parsed = urllib.parse.urlparse(endpoint)
                    params = urllib.parse.parse_qs(parsed.query)
                    params["startIndex"] = [str(start + per_page)]
                    params["count"] = [str(per_page)]
                    url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urllib.parse.urlencode(params, doseq=True)}"
                else:
                    url = None
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}: {e.read().decode(errors='replace')[:500]}"
            fetch_complete = False
            break
        except (urllib.error.URLError, OSError) as e:
            last_error = f"Network error: {e.reason if hasattr(e, 'reason') else e}"
            fetch_complete = False
            break
        except json.JSONDecodeError as e:
            last_error = f"Invalid response: {e}"
            fetch_complete = False
            break
    return all_results, fetch_complete, last_error


def _scim_get_name(resource: dict) -> str:
    name = resource.get("name", {}) or {}
    formatted = (name.get("formatted") or "").strip()
    if formatted:
        return formatted
    given = (name.get("givenName") or "").strip()
    family = (name.get("familyName") or "").strip()
    if given or family:
        return f"{given} {family}".strip()
    return (resource.get("userName") or "").strip()


def _scim_get_email(resource: dict) -> str:
    emails = resource.get("emails") or []
    for e in emails:
        if e.get("primary"):
            return (e.get("value") or "").strip()
    if emails:
        return (emails[0].get("value") or "").strip()
    return ""


def _scim_get_phone(resource: dict) -> str:
    phones = resource.get("phoneNumbers") or []
    if phones:
        return (phones[0].get("value") or "").strip()
    return ""


def _scim_get_location(resource: dict) -> str:
    addrs = resource.get("addresses") or []
    if addrs:
        return (addrs[0].get("locality") or "").strip()
    return ""


def _scim_get_manager(resource: dict) -> str:
    ext = resource.get("urn:ietf:params:scim:schemas:extension:enterprise:2.0:User", {}) or {}
    mgr = ext.get("manager", {}) or {}
    return (mgr.get("displayName") or "").strip()


def import_users(org_id: str = "", workspace_id: str = "") -> dict:
    endpoint, token = get_credentials()
    if not endpoint or not token:
        return {"ok": False, "count": 0, "error": "SCIM not configured. Configure it in Team \u2192 settings."}

    users, fetch_complete, err = _scim_get(endpoint, token)
    if not users:
        return {"ok": False, "count": 0, "error": err or "No users returned from SCIM endpoint."}

    from .store import create_person, update_person, list_personnel, mark_missing_as_inactive
    imported = 0
    updated = 0
    deactivated = 0
    errors = []
    seen_external_ids: set[str] = set()

    existing = list_personnel(org_id=org_id) if org_id else list_personnel()
    by_ext_id: dict[str, dict] = {}
    by_email: dict[str, dict] = {}
    for p in existing:
        eid = p.get("external_id", "") or ""
        if eid:
            by_ext_id[eid] = p
        em = (p.get("email") or "").lower().strip()
        if em:
            by_email[em] = p

    for u in users:
        name = _scim_get_name(u)
        if not name:
            continue
        email = _scim_get_email(u)
        ext_id = (u.get("id") or "").strip()
        if ext_id:
            seen_external_ids.add(ext_id)
        try:
            raw = dict(u)
            scim_active = u.get("active")
            payload = dict(
                name=name,
                email=email,
                role=(u.get("title") or "").strip(),
                department=(u.get("department") or "").strip(),
                status="active" if scim_active is not False else "inactive",
                org_id=org_id,
                workspace_id=workspace_id,
                frameworks=[],
                external_id=ext_id,
                phone=_scim_get_phone(u),
                location=_scim_get_location(u),
                manager=_scim_get_manager(u),
                employee_id=(u.get("employeeNumber") or "").strip(),
                provider="scim",
                raw_attributes=raw,
            )
            if ext_id and ext_id in by_ext_id:
                update_person(by_ext_id[ext_id]["id"], **payload)
                updated += 1
            elif email and email.lower() in by_email:
                update_person(by_email[email.lower()]["id"], **payload)
                updated += 1
            else:
                create_person(**payload)
                imported += 1
        except Exception as e:
            errors.append(f"{name}: {e}")

    if fetch_complete and org_id:
        deactivated = mark_missing_as_inactive("scim", org_id, seen_external_ids)

    return {"ok": True, "count": imported, "updated": updated, "deactivated": deactivated, "errors": errors}
