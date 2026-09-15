"""Request-scoped authenticated user (set by API middleware)."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

from entra_auth.user import AuthUser

_auth_user: ContextVar[Optional[AuthUser]] = ContextVar("auth_user", default=None)


def set_auth_user(user: Optional[AuthUser]) -> None:
    _auth_user.set(user)


def get_auth_user() -> Optional[AuthUser]:
    return _auth_user.get()
