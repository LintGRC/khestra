"""Core service auth — JWT from the shared auth DB.

Every /api/* request (except public paths) must carry a valid JWT issued by
the shared auth store. The scheduler token is accepted for run-due.
"""

from __future__ import annotations

from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from auth.jwt import decode_token
from auth.store import get_user
from kevidence.scheduler import scheduler_token_matches

PUBLIC_PATHS = frozenset({
    "/api/health",
    "/api/auth/config",
    "/api/auth/login",
    "/api/collectors/health",
})


def _bearer_token(request: Request) -> str | None:
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


async def core_auth_middleware(request: Request, call_next: Callable) -> Response:
    path = request.url.path
    if not path.startswith("/api") or path in PUBLIC_PATHS:
        return await call_next(request)

    token = _bearer_token(request)
    if not token:
        return JSONResponse({"detail": "Authentication required"}, status_code=401)

    # Scheduler token is allowed for scheduled run triggers.
    if scheduler_token_matches(token):
        request.state.user = {"id": "scheduler", "email": "scheduler", "role": "scheduler"}
        return await call_next(request)

    payload = decode_token(token)
    if not payload:
        return JSONResponse({"detail": "Invalid or expired token"}, status_code=401)
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("uid") or ""
    user = get_user(user_id) if user_id else None
    if not user or user.get("deactivated"):
        return JSONResponse({"detail": "User not found or deactivated"}, status_code=401)
    request.state.user = user
    return await call_next(request)
