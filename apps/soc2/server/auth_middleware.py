"""FastAPI middleware — Microsoft Entra ID bearer tokens (shared with CMMC via entra_auth)."""

from __future__ import annotations

from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from auth.jwt import decode_token as decode_local_token
from auth.store import get_user
from kevidence.scheduler import scheduler_token_matches
from entra_auth.config import auth_enabled, auth_mode, is_public_api_path
from entra_auth.context import set_auth_user
from entra_auth.jwt import validate_access_token
from entra_auth.user import AuthUser, user_from_claims
from sandbox_access import user_may_access_sandbox
from sandbox_config import sandbox_mode


def _bearer_token(request: Request) -> str | None:
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


async def entra_auth_middleware(request: Request, call_next: Callable) -> Response:
    # Strip framework prefix before any auth checks (must use scope to avoid URL cache)
    raw = request.scope.get("path", "")
    if raw.startswith("/api/soc2/"):
        request.scope["path"] = raw.replace("/api/soc2/", "/api/", 1)

    set_auth_user(None)

    if not auth_enabled():
        return await call_next(request)

    path = request.url.path
    if not path.startswith("/api") or is_public_api_path(path):
        return await call_next(request)

    token = _bearer_token(request)
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Authentication required"})

    if path == "/api/collectors/monitoring/run-due" and scheduler_token_matches(token):
        return await call_next(request)

    mode = auth_mode()
    if mode == "local":
        payload = decode_local_token(token)
        if not payload:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})
        user_id = payload.get("sub", "")
        if not user_id:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        user_record = get_user(user_id)
        if not user_record or user_record.get("deactivated", 0) == 1:
            return JSONResponse(status_code=401, content={"detail": "Account deactivated or invalid"})
        token_tv = payload.get("tv", 0)
        if token_tv != user_record.get("token_version", 0):
            return JSONResponse(status_code=401, content={"detail": "Session invalidated — please log in again"})
        user = AuthUser(
            oid=user_id,
            name=user_record.get("name", ""),
            email=user_record.get("email", ""),
            role=user_record.get("role", "Viewer"),
            org_id=user_record.get("org_id", ""),
            is_org_owner=bool(user_record.get("is_org_owner", 0)),
            is_msp=bool(user_record.get("is_msp", 0)),
            groups=[],
            app_roles=[],
        )
        set_auth_user(user)
        return await call_next(request)

    try:
        claims = validate_access_token(token)
        user = user_from_claims(claims)
        if sandbox_mode() and not user_may_access_sandbox(user):
            return JSONResponse(
                status_code=403,
                content={"detail": "You are not authorized for this sandbox environment"},
            )
        set_auth_user(user)
    except PermissionError as exc:
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=401, content={"detail": f"Invalid token: {exc}"})

    return await call_next(request)
