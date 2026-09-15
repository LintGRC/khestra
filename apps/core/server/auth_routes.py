"""Platform auth routes — login/config against the shared auth store."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth.jwt import create_token
from auth.store import authenticate

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginBody(BaseModel):
    email: str = ""
    password: str = ""


@router.get("/config")
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


@router.post("/login")
def login(body: LoginBody):
    user = authenticate(body.email.strip().lower(), body.password)
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
