import json
import logging
import os
import sqlite3
import urllib.request
import urllib.error

_log = logging.getLogger("personnel.okta")


def get_credentials() -> tuple[str, str]:
    domain = api_token = ""
    try:
        from .settings_store import get_setting
        domain = get_setting("okta_domain") or ""
        api_token = get_setting("okta_api_token") or ""
    except (ImportError, sqlite3.Error) as e:
        _log.warning("Failed to read Okta settings from DB: %s", e)
    if not domain:
        domain = os.environ.get("OKTA_DOMAIN") or ""
    if not api_token:
        api_token = os.environ.get("OKTA_API_TOKEN") or ""
    return domain, api_token


def _okta_get(domain: str, api_token: str, path: str) -> tuple[list[dict], bool, str | None]:
    base = f"https://{domain}/api/v1/{path.lstrip('/')}"
    all_results = []
    url: str | None = base
    fetch_complete = True
    last_error = None
    while url:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"SSWS {api_token}")
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                if isinstance(data, list):
                    all_results.extend(data)
                else:
                    all_results.append(data)
                link_header = resp.headers.get("Link", "")
                url = None
                for part in link_header.split(","):
                    if 'rel="next"' in part:
                        parts = part.split(";")
                        if parts:
                            url = parts[0].strip().strip("<>")
                        break
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


def _okta_get_single(domain: str, api_token: str, path: str) -> tuple[dict | list | None, str | None]:
    url = f"https://{domain}/api/v1/{path.lstrip('/')}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"SSWS {api_token}")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read()), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode(errors='replace')[:500]}"
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        return None, f"Error: {e}"


def _check_okta_mfa_policy(domain: str, api_token: str) -> tuple[bool, list[str], str]:
    """Check if any active MFA-enforcing policy exists.
    Returns (mfa_enforced, debug, raw_json_of_first_policy)."""
    debug: list[str] = []
    raw_sample = ""
    for policy_type in ("OKTA_SIGN_ON", "ACCESS_POLICY"):
        data, err = _okta_get_single(domain, api_token, f"policies?type={policy_type}")
        if err:
            debug.append(f"mfa-policy[{policy_type}]: {err}")
            continue
        if not isinstance(data, list):
            debug.append(f"mfa-policy[{policy_type}]: unexpected type {type(data).__name__}")
            continue
        for policy in data:
            if policy.get("status") != "ACTIVE":
                continue
            raw_str = json.dumps(policy)
            if not raw_sample:
                raw_sample = raw_str
            mfa_keywords = ["MFA", "mfa", "factor", "authenticator", "okta_verify",
                            "REQUIRED", "passwordless", "MFA_ENROLL", "challenge",
                            "deviceKnown", "device_enrollment", "appSignOn"]
            if any(kw in raw_str for kw in mfa_keywords):
                debug.append(f"mfa-policy[{policy_type}/{policy.get('name','')}]: MFA-enforcing policy found")
                return True, debug, raw_sample
    debug.append(f"mfa-policy: no MFA-enforcing policy found across checked types")
    return False, debug, raw_sample


def _fetch_okta_mfa_statuses(domain: str, api_token: str, user_ids: list[str], uid_to_email: dict[str, str] | None = None) -> tuple[dict[str, bool], list[str]]:
    """Returns {user_id: has_mfa_registered} and debug lines."""
    statuses: dict[str, bool] = {}
    debug: list[str] = []
    for uid in user_ids:
        label = (uid_to_email or {}).get(uid) or uid
        data, err = _okta_get_single(domain, api_token, f"users/{uid}/factors")
        if err:
            detail = f"factors:{label}: {err}"
            _log.warning(detail)
            debug.append(detail)
            statuses[uid] = False
        elif isinstance(data, list):
            if len(data) > 0:
                debug.append(f"factors:{label}: {len(data)} enrolled (OK)")
            else:
                debug.append(f"factors:{label}: 0 enrolled")
            statuses[uid] = len(data) > 0
        else:
            debug.append(f"factors:{label}: unexpected type {type(data).__name__}")
            statuses[uid] = False
    return statuses, debug


def _fetch_okta_privileged(domain: str, api_token: str, user_ids: list[str], uid_to_email: dict[str, str] | None = None) -> tuple[dict[str, bool], list[str]]:
    """Returns {user_id: has_admin_role} and debug lines."""
    statuses: dict[str, bool] = {}
    debug: list[str] = []
    for uid in user_ids:
        label = (uid_to_email or {}).get(uid) or uid
        data, err = _okta_get_single(domain, api_token, f"users/{uid}/roles")
        if err:
            detail = f"roles:{label}: {err}"
            _log.warning(detail)
            debug.append(detail)
            statuses[uid] = False
        elif isinstance(data, list):
            active = any(r.get("status") == "ACTIVE" for r in data)
            if active:
                debug.append(f"roles:{label}: active admin role")
            else:
                debug.append(f"roles:{label}: {len(data)} role(s), none active")
            statuses[uid] = active
        else:
            debug.append(f"roles:{label}: unexpected type {type(data).__name__}")
            statuses[uid] = False
    return statuses, debug


def import_users(org_id: str = "", workspace_id: str = "") -> dict:
    domain, api_token = get_credentials()
    if not domain or not api_token:
        return {"ok": False, "count": 0, "error": "Okta not configured. Configure it in Team \u2192 settings."}

    users, fetch_complete, err = _okta_get(domain, api_token, "users?limit=200")
    if not users:
        return {"ok": False, "count": 0, "error": err or "No users returned from Okta."}

    user_ids = [str(u.get("id") or "") for u in users if u.get("id")]
    uid_to_email = {
        str(u.get("id") or ""): (u.get("profile", {}).get("email") or "").strip()
        for u in users if u.get("id")
    }

    mfa_policy_enforced, policy_debug, policy_raw = _check_okta_mfa_policy(domain, api_token)
    if policy_raw:
        _log.info("Okta MFA policy raw: %s", policy_raw)
    mfa_statuses, mfa_debug = _fetch_okta_mfa_statuses(domain, api_token, user_ids, uid_to_email)
    priv_statuses, priv_debug = _fetch_okta_privileged(domain, api_token, user_ids, uid_to_email)

    if mfa_policy_enforced:
        mfa_statuses = {uid: True for uid in mfa_statuses}
        mfa_debug.append("mfa-policy: marking all users as MFA-registered based on active policy")

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
        profile = u.get("profile", {}) or {}
        name = (profile.get("displayName") or "").strip()
        if not name:
            first = (profile.get("firstName") or "").strip()
            last = (profile.get("lastName") or "").strip()
            name = f"{first} {last}".strip()
        if not name:
            name = (profile.get("email") or "").strip()
        email = (profile.get("email") or "").strip()
        if not name:
            continue
        ext_id = (u.get("id") or "").strip()
        if ext_id:
            seen_external_ids.add(ext_id)
        try:
            raw = dict(u)
            okta_status = (u.get("status") or "").strip()
            last_login = (u.get("lastLogin") or "").strip()
            payload = dict(
                name=name,
                email=email,
                role=(profile.get("title") or "").strip(),
                department=(profile.get("department") or "").strip(),
                status="active" if okta_status == "ACTIVE" else "inactive",
                org_id=org_id,
                workspace_id=workspace_id,
                frameworks=[],
                external_id=ext_id,
                phone=(profile.get("mobilePhone") or "").strip(),
                location=(profile.get("locale") or "").strip(),
                employee_id=(profile.get("employeeNumber") or "").strip(),
                provider="okta",
                raw_attributes=raw,
                last_login=last_login,
                mfa_status="enabled" if mfa_statuses.get(ext_id) else "",
                is_privileged=priv_statuses.get(ext_id, False),
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
        deactivated = mark_missing_as_inactive("okta", org_id, seen_external_ids)

    mfa_summary = ""
    if policy_debug:
        mfa_summary = "; ".join(policy_debug[:1])
    mfa_enrolled = sum(1 for v in mfa_statuses.values() if v)
    mfa_total = len(mfa_statuses)
    mfa_summary += f"; users with MFA: {mfa_enrolled}/{mfa_total}"

    return {
        "ok": True,
        "count": imported,
        "updated": updated,
        "deactivated": deactivated,
        "errors": errors + ([mfa_summary] if mfa_summary else []),
        "mfa_policy_debug": policy_debug,
        "mfa_policy_raw": policy_raw,
        "mfa_debug": mfa_debug,
        "roles_debug": priv_debug,
    }
