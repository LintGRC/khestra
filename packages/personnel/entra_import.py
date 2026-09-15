import json
import os
import sqlite3
import urllib.request
import urllib.parse
import urllib.error


def get_credentials() -> tuple[str, str, str]:
    tid = cid = secret = ""
    try:
        from .settings_store import get_setting
        tid = get_setting("entra_tenant_id") or ""
        cid = get_setting("entra_client_id") or ""
        secret = get_setting("entra_client_secret") or ""
    except (ImportError, sqlite3.Error) as e:
        import logging
        logging.getLogger("personnel.entra").warning("Failed to read Entra settings from DB: %s", e)
    if not tid:
        tid = os.environ.get("CMMC_ENTRA_TENANT_ID") or os.environ.get("AZURE_TENANT_ID") or ""
    if not cid:
        cid = os.environ.get("CMMC_ENTRA_CLIENT_ID") or os.environ.get("AZURE_CLIENT_ID") or ""
    if not secret:
        secret = os.environ.get("CMMC_ENTRA_CLIENT_SECRET") or os.environ.get("AZURE_CLIENT_SECRET") or ""
    return tid, cid, secret


def _get_token() -> tuple[str | None, str | None]:
    """Returns (access_token, error_message)."""
    tid, cid, secret = get_credentials()
    if not tid or not cid or not secret:
        return None, "Entra ID not configured."

    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": secret,
        "scope": "https://graph.microsoft.com/.default",
    }).encode()
    url = f"https://login.microsoftonline.com/{tid}/oauth2/v2.0/token"
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
            token = body.get("access_token")
            if not token:
                return None, "Token response missing access_token."
            return token, None
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        return None, f"HTTP {e.code}: {detail}"
    except (urllib.error.URLError, OSError) as e:
        return None, f"Network error: {e.reason if hasattr(e, 'reason') else e}"
    except json.JSONDecodeError as e:
        return None, f"Invalid token response: {e}"


def _graph_get(token: str, path: str) -> tuple[dict | None, str | None]:
    """Returns (response_dict, error_string)."""
    url = f"https://graph.microsoft.com/v1.0/{path.lstrip('/')}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read()), None
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        return None, f"Graph API HTTP {e.code}: {detail}"
    except (urllib.error.URLError, OSError) as e:
        return None, f"Network error: {e.reason if hasattr(e, 'reason') else e}"
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON response: {e}"


def _fetch_all_users(token: str) -> tuple[list[dict], bool, str | None]:
    users: list[dict] = []
    url = "users?$select=id,displayName,mail,userPrincipalName,jobTitle,department,mobilePhone,officeLocation,employeeId,accountEnabled&$top=999"
    fetch_complete = True
    while url:
        result, err = _graph_get(token, url)
        if err:
            return users, False, err
        if not result:
            fetch_complete = False
            break
        users.extend(result.get("value", []))
        url = (result.get("@odata.nextLink") or "").replace("https://graph.microsoft.com/v1.0/", "")
    return users, fetch_complete, None


def _fetch_mfa_statuses(token: str, user_ids: list[str]) -> dict[str, bool]:
    """Returns {user_id: has_mfa_registered} via Microsoft Graph batch."""
    if not user_ids:
        return {}
    statuses: dict[str, bool] = {}
    for i in range(0, len(user_ids), 20):
        batch = user_ids[i:i + 20]
        requests = [
            {"id": uid, "method": "GET", "url": f"/users/{uid}/authentication/methods"}
            for uid in batch
        ]
        body = json.dumps({"requests": requests}).encode()
        req = urllib.request.Request("https://graph.microsoft.com/v1.0/$batch", data=body, method="POST")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                batch_result = json.loads(resp.read())
                for resp_item in batch_result.get("responses", []):
                    uid = resp_item.get("id", "")
                    if resp_item.get("status") == 200:
                        methods = resp_item.get("body", {}).get("value", [])
                        statuses[uid] = len(methods) > 0
                    else:
                        statuses[uid] = False
        except Exception:
            pass
    return statuses


def import_users(org_id: str = "", workspace_id: str = "") -> dict:
    token, err = _get_token()
    if not token:
        return {"ok": False, "count": 0, "error": err or "Entra ID not configured. Configure it in Team → settings."}

    users, fetch_complete, graph_err = _fetch_all_users(token)
    if graph_err:
        return {"ok": False, "count": 0, "error": graph_err}
    if not users:
        return {"ok": False, "count": 0, "error": "No users returned from Entra ID."}

    user_ids = [str(u.get("id") or "") for u in users if u.get("id")]
    mfa_statuses = _fetch_mfa_statuses(token, user_ids)

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
        name = (u.get("displayName") or "").strip()
        email = (u.get("mail") or u.get("userPrincipalName") or "").strip()
        if not name:
            continue
        ext_id = (u.get("id") or "").strip()
        if ext_id:
            seen_external_ids.add(ext_id)
        try:
            raw = dict(u)
            account_enabled = u.get("accountEnabled")
            signin = u.get("signInActivity")
            last_login = ""
            if isinstance(signin, dict):
                last_login = (signin.get("lastSignInDateTime") or "").strip()
            payload = dict(
                name=name,
                email=email,
                role=(u.get("jobTitle") or "").strip(),
                department=(u.get("department") or "").strip(),
                status="active" if account_enabled is not False else "inactive",
                org_id=org_id,
                workspace_id=workspace_id,
                frameworks=[],
                external_id=ext_id,
                phone=(u.get("mobilePhone") or "").strip(),
                location=(u.get("officeLocation") or "").strip(),
                employee_id=(u.get("employeeId") or "").strip(),
                provider="entra",
                raw_attributes=raw,
                last_login=last_login,
                mfa_status="enabled" if mfa_statuses.get(ext_id) else "",
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
        deactivated = mark_missing_as_inactive("entra", org_id, seen_external_ids)

    return {"ok": True, "count": imported, "updated": updated, "deactivated": deactivated, "errors": errors}
