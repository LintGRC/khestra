"""Auth API routes — login, me, register, org management, admin user management."""

from __future__ import annotations

import secrets
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from pydantic import BaseModel, field_validator
from typing import Optional

from .jwt import create_token
from . import store as _store
from .store import (
    authenticate as _authenticate,
    create_user,
    has_admin_privilege,
    is_org_admin,
    get_user,
    list_users,
    list_users_by_org,
    count_users_by_org,
    update_user_role,
    update_user_password,
    delete_user as _delete_user,
    create_org,
    get_org,
    create_invitation,
    accept_invitation as _accept_invitation,
    user_count,
)
from entra_auth.context import get_auth_user as _get_current_user
from entra_auth.config import auth_enabled, auth_mode

router = APIRouter()


class LoginBody(BaseModel):
    email: str = ""
    password: str = ""


class RegisterBody(BaseModel):
    email: str = ""
    name: str = ""
    password: str = ""
    org_name: str = ""


class InviteBody(BaseModel):
    email: str = ""
    role: str = "Assessor"


class AcceptInviteBody(BaseModel):
    token: str = ""
    name: str = ""
    password: str = ""


class UserCreateBody(BaseModel):
    email: str = ""
    name: str = ""
    password: str = ""
    role: str = "Executive"

    @field_validator("password")
    @classmethod
    def _password_min_length(cls, v: str) -> str:
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserPatchBody(BaseModel):
    role: Optional[str] = None
    password: Optional[str] = None


# ── Helpers ──────────────────────────────────────────────────────────────


def _require_admin():
    if not auth_enabled():
        return
    user = _get_current_user()
    if not user:
        raise HTTPException(401, "Not authenticated")
    if not has_admin_privilege(user.oid):
        raise HTTPException(403, "Admin access required")


def _require_org_admin():
    if not auth_enabled():
        return
    user = _get_current_user()
    if not user:
        raise HTTPException(401, "Not authenticated")
    if not is_org_admin(user.oid):
        raise HTTPException(403, "Organization Admin access required")


def _require_authenticated():
    if not auth_enabled():
        return
    user = _get_current_user()
    if not user:
        raise HTTPException(401, "Not authenticated")


def _current_org_id() -> str:
    user = _get_current_user()
    if not user:
        return ""
    if user.org_id:
        return user.org_id
    return ""


# ── Auth ─────────────────────────────────────────────────────────────────


@router.post("/api/auth/login")
def login(body: LoginBody):
    if not auth_enabled():
        raise HTTPException(400, "Auth is disabled")
    if not body.email or not body.password:
        raise HTTPException(400, "Email and password required")
    user = _authenticate(body.email, body.password)
    if not user:
        raise HTTPException(401, "Invalid email or password")
    token = create_token(
        user["id"], user["email"], user["name"], user["role"],
        org_id=user.get("org_id", ""),
        is_org_owner=bool(user.get("is_org_owner", 0)),
        is_msp=bool(user.get("is_msp", 0)),
        token_version=user.get("token_version", 0),
    )
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "org_id": user.get("org_id", ""),
            "is_org_owner": bool(user.get("is_org_owner", 0)),
            "is_msp": bool(user.get("is_msp", 0)),
        },
    }


@router.get("/api/auth/me")
def me():
    user = _get_current_user()
    if not user:
        raise HTTPException(401, "Not authenticated")
    return {
        "id": user.oid,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "org_id": user.org_id,
        "is_org_owner": user.is_org_owner,
        "is_msp": user.is_msp,
    }


@router.post("/api/auth/register")
def register(body: RegisterBody):
    if not auth_enabled():
        raise HTTPException(400, "Auth is disabled")
    if not body.email or not body.password:
        raise HTTPException(400, "Email and password required")
    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    if not body.org_name:
        raise HTTPException(400, "Organization name required")

    org = create_org(name=body.org_name)
    try:
        user = create_user(
            email=body.email,
            name=body.name or body.email,
            password=body.password,
            role="Organization Admin",
            org_id=org["id"],
            is_org_owner=True,
        )
    except ValueError as exc:
        raise HTTPException(409, str(exc))

    token = create_token(
        user["id"], user["email"], user["name"], user["role"],
        org_id=user.get("org_id", ""),
        is_org_owner=True,
        token_version=user.get("token_version", 0),
    )
    return {"token": token, "user": user, "org": org}


@router.post("/api/auth/reset-admin-password")
def reset_admin_password():
    """Reset the admin password. Only works in local mode and for org admins.
    Finds the first Admin user, generates a new password, and records it in
    the auth_admin_credentials.txt file. The password is never returned in
    the response."""
    if auth_mode() != "local":
        raise HTTPException(400, "Only available in local auth mode")

    _require_org_admin()

    from .store import (
        find_admin_user as _find_admin,
    )

    admin = _find_admin()
    if not admin:
        raise HTTPException(404, "No admin user found")

    new_password = secrets.token_urlsafe(12)
    ok = update_user_password(admin["id"], new_password)
    if not ok:
        raise HTTPException(500, "Failed to update password")

    data_dir = Path(_store.DB_PATH).parent if _store.DB_PATH else Path("data")
    log_path = data_dir / "auth_admin_credentials.txt"
    log_path.write_text(f"Email: {admin['email']}\nPassword: {new_password}\n")

    return {"ok": True, "email": admin["email"]}


class ForgotPasswordBody(BaseModel):
    email: str = ""


class ResetPasswordBody(BaseModel):
    token: str = ""
    password: str = ""

    @field_validator("password")
    @classmethod
    def _password_min_length(cls, v: str) -> str:
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


@router.post("/api/auth/forgot-password")
def forgot_password(body: ForgotPasswordBody):
    if not auth_enabled():
        raise HTTPException(400, "Auth is disabled")
    if not body.email:
        raise HTTPException(400, "Email required")

    user = _get_current_user()
    if not user:
        raise HTTPException(401, "Not authenticated")
    if user.email.lower() != body.email.lower():
        raise HTTPException(403, "You can only request a reset for your own account")

    from .store import generate_reset_token as _generate_reset_token

    token = _generate_reset_token(body.email)
    if not token:
        return {"ok": True, "message": "If that email exists, a reset link has been sent."}

    if auth_mode() == "local":
        return {"ok": True, "reset_token": token}
    return {"ok": True, "message": "If that email exists, a reset link has been sent."}


@router.post("/api/auth/reset-password")
def reset_password(body: ResetPasswordBody):
    if not auth_enabled():
        raise HTTPException(400, "Auth is disabled")
    if not body.token or not body.password:
        raise HTTPException(400, "Token and password required")

    from .store import reset_password_with_token as _reset_password_with_token

    ok = _reset_password_with_token(body.token, body.password)
    if not ok:
        raise HTTPException(400, "Invalid or expired reset token")
    return {"ok": True}


# ── Invitations ──────────────────────────────────────────────────────────


@router.post("/api/auth/invite")
def invite_user(body: InviteBody):
    if body.role == "Organization Admin":
        _require_org_admin()
    else:
        _require_admin()
    if not body.email:
        raise HTTPException(400, "Email required")
    org_id = _current_org_id()
    if not org_id:
        raise HTTPException(400, "No org assigned")

    org = get_org(org_id)
    if org and org.get("plan") == "trial":
        current = count_users_by_org(org_id)
        if current >= 5:
            raise HTTPException(402, "User limit reached for trial plan. Upgrade to add more users.")

    try:
        invitation = create_invitation(org_id=org_id, email=body.email, role=body.role)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    return {"invitation": invitation}


@router.post("/api/auth/accept-invite")
def accept_invite(body: AcceptInviteBody):
    if not auth_enabled():
        raise HTTPException(400, "Auth is disabled")
    if not body.token or not body.password:
        raise HTTPException(400, "Token and password required")
    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")

    try:
        user = _accept_invitation(token=body.token, name=body.name or body.email, password=body.password)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    token = create_token(
        user["id"], user["email"], user["name"], user["role"],
        org_id=user.get("org_id", ""),
        is_org_owner=bool(user.get("is_org_owner", 0)),
        is_msp=bool(user.get("is_msp", 0)),
        token_version=user.get("token_version", 0),
    )
    return {"token": token, "user": user}


# ── Org management ───────────────────────────────────────────────────────


@router.get("/api/auth/org")
def get_current_org():
    _require_authenticated()
    org_id = _current_org_id()
    if not org_id:
        raise HTTPException(400, "No org assigned")
    org = get_org(org_id)
    if not org:
        raise HTTPException(404, "Organization not found")
    return {"org": org}


@router.get("/api/auth/org/users")
def list_org_users():
    _require_admin()
    org_id = _current_org_id()
    if not org_id:
        raise HTTPException(400, "No org assigned")
    users = list_users_by_org(org_id)
    return {"users": [{k: v for k, v in u.items() if k != "password_hash"} for u in users]}


@router.patch("/api/auth/org/users/{user_id}")
def patch_org_user_role(user_id: str, body: UserPatchBody):
    if body.role == "Organization Admin":
        _require_org_admin()
    else:
        _require_admin()
    if not body.role and not body.password:
        raise HTTPException(400, "Nothing to update")
    current = _get_current_user()
    if current and current.oid == user_id:
        raise HTTPException(400, "Cannot change your own role")
    org_id = _current_org_id()
    target = get_user(user_id)
    if not target or target.get("org_id") != org_id:
        raise HTTPException(404, "User not found in your org")
    updated = {}
    if body.role:
        user = update_user_role(user_id, body.role)
        updated["role"] = user["role"]
    if body.password and isinstance(body.password, str) and body.password.strip():
        ok = update_user_password(user_id, body.password)
        if ok:
            updated["password"] = "changed"
    if not updated:
        raise HTTPException(400, "Nothing to update")
    return {"user": {k: v for k, v in (user or {}).items() if k != "password_hash"}, "updated": updated}


@router.delete("/api/auth/org/users/{user_id}")
def remove_org_user(user_id: str):
    org_id = _current_org_id()
    target = get_user(user_id)
    if not target or target.get("org_id") != org_id:
        raise HTTPException(404, "User not found in your org")
    if target.get("role") == "Organization Admin":
        _require_org_admin()
    else:
        _require_admin()
    current = _get_current_user()
    if current and current.oid == user_id:
        raise HTTPException(400, "Cannot remove yourself")
    if not _delete_user(user_id):
        raise HTTPException(404, "User not found")
    return {"status": "deactivated"}


# ── Global admin (MSP / super-admin) ─────────────────────────────────────


@router.get("/api/auth/users")
def list_all_users():
    _require_admin()
    return {"users": [{k: v for k, v in u.items() if k != "password_hash"} for u in list_users()]}


@router.post("/api/auth/users")
def admin_create_user(body: UserCreateBody):
    if body.role == "Organization Admin":
        _require_org_admin()
    else:
        _require_admin()
    if not body.email:
        raise HTTPException(400, "Email required")
    org_id = _current_org_id()
    try:
        user = create_user(email=body.email, name=body.name or body.email, password=body.password, role=body.role, org_id=org_id)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    return {"user": user}


@router.patch("/api/auth/users/{user_id}")
def admin_patch_user(user_id: str, body: UserPatchBody):
    user = get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if body.role == "Organization Admin" or user.get("role") == "Organization Admin":
        _require_org_admin()
    else:
        _require_admin()
    if not body.role and not body.password:
        raise HTTPException(400, "Nothing to update")
    updated = {}
    if body.role:
        user = update_user_role(user_id, body.role)
        updated["role"] = user["role"]
    if body.password and isinstance(body.password, str) and body.password.strip():
        ok = update_user_password(user_id, body.password)
        if ok:
            updated["password"] = "changed"
    if not updated:
        raise HTTPException(400, "Nothing to update")
    return {"user": {k: v for k, v in (user or {}).items() if k != "password_hash"}, "updated": updated}


@router.delete("/api/auth/users/{user_id}")
def admin_delete_user(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user.get("role") == "Organization Admin":
        _require_org_admin()
    else:
        _require_admin()
    current = _get_current_user()
    if current and current.oid == user_id:
        raise HTTPException(400, "Cannot deactivate yourself")
    if not _delete_user(user_id):
        raise HTTPException(404, "User not found")
    return {"status": "deactivated"}
