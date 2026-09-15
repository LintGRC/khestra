"""Defense-in-depth security headers applied to every app response.

Applied unconditionally so every response carries security headers
regardless of which optional middleware is installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from starlette.applications import Starlette

SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com"
    ),
}


class SecurityHeadersMiddleware:
    """ASGI middleware that stamps security headers onto every response."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                message = dict(message)
                headers = [
                    (name, value)
                    for name, value in headers
                    if name not in {b"x-frame-options", b"x-content-type-options", b"strict-transport-security", b"content-security-policy", b"referrer-policy"}
                ]
                for name, value in SECURITY_HEADERS.items():
                    headers.append((name.encode("latin-1"), value.encode("latin-1")))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)


def add_security_headers(app: "Starlette") -> None:
    """Attach the security-headers middleware to a FastAPI/Starlette app."""
    app.add_middleware(SecurityHeadersMiddleware)
