"""Baseline rate limiting for sensitive endpoints (e.g. login).

Dependency-free fixed-window limiter keyed by client IP. It protects the
self-hosted baseline (online password guessing against /api/auth/login); for
public internet exposure, pair it with proxy-level limits (see README).

Configuration (env):
  AUTH_RATE_LIMIT_MAX     requests allowed per window (default 10)
  AUTH_RATE_LIMIT_WINDOW  window size in seconds (default 300)
  AUTH_RATE_LIMIT_PATHS   comma-separated path suffixes (default /auth/login)
"""

from __future__ import annotations

import os
import time
from threading import Lock
from typing import Dict, Iterable, Tuple

DEFAULT_PATHS = ("/auth/login",)


def _client_ip(scope) -> str:
    """Best-effort client identity: first X-Forwarded-For hop, else socket peer."""
    for name, value in scope.get("headers") or []:
        if name == b"x-forwarded-for":
            first = value.decode("latin-1").split(",")[0].strip()
            if first:
                return first
    client = scope.get("client")
    if client:
        return str(client[0])
    return "unknown"


class RateLimitMiddleware:
    """Fixed-window per-IP limiter for matching path suffixes."""

    def __init__(self, app, *, paths: Iterable[str] = DEFAULT_PATHS,
                 max_requests: int = 10, window_seconds: int = 300):
        self.app = app
        self.paths = tuple(p for p in paths if p)
        self.max_requests = max(1, int(max_requests))
        self.window_seconds = max(1, int(window_seconds))
        self._hits: Dict[str, Tuple[float, int]] = {}
        self._lock = Lock()

    def _matches(self, path: str) -> bool:
        return any(path == p or path.endswith(p) for p in self.paths)

    def _exceeded(self, ip: str, now: float) -> Tuple[bool, int]:
        with self._lock:
            start, count = self._hits.get(ip, (now, 0))
            if now - start >= self.window_seconds:
                start, count = now, 0
            count += 1
            self._hits[ip] = (start, count)
            # Opportunistic cleanup so the map cannot grow unbounded.
            if len(self._hits) > 10_000:
                cutoff = now - self.window_seconds
                self._hits = {k: v for k, v in self._hits.items() if v[0] >= cutoff}
            retry_after = max(1, int(self.window_seconds - (now - start)))
            return count > self.max_requests, retry_after

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or not self._matches(scope.get("path", "")):
            await self.app(scope, receive, send)
            return

        exceeded, retry_after = self._exceeded(_client_ip(scope), time.monotonic())
        if exceeded:
            body = b'{"detail":"Too many requests. Try again shortly."}'
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"retry-after", str(retry_after).encode()),
                ],
            })
            await send({"type": "http.response.body", "body": body})
            return

        await self.app(scope, receive, send)


def add_rate_limiting(app, *, paths: Iterable[str] | None = None) -> None:
    """Attach the login limiter using env configuration (no-op if disabled)."""
    if os.environ.get("AUTH_RATE_LIMIT_DISABLE", "").strip() in ("1", "true", "yes"):
        return
    raw_paths = os.environ.get("AUTH_RATE_LIMIT_PATHS", "").strip()
    if paths is None:
        paths = tuple(p.strip() for p in raw_paths.split(",") if p.strip()) or DEFAULT_PATHS
    try:
        max_requests = int(os.environ.get("AUTH_RATE_LIMIT_MAX", "10"))
    except ValueError:
        max_requests = 10
    try:
        window_seconds = int(os.environ.get("AUTH_RATE_LIMIT_WINDOW", "300"))
    except ValueError:
        window_seconds = 300
    app.add_middleware(
        RateLimitMiddleware,
        paths=paths,
        max_requests=max_requests,
        window_seconds=window_seconds,
    )
