"""Tests for the baseline auth rate limiter."""

import asyncio

from security_headers.ratelimit import RateLimitMiddleware


def _call(mw, path, ip="1.2.3.4"):
    sent = []

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        if message["type"] == "http.response.start":
            sent.append(message)

    scope = {"type": "http", "path": path, "headers": [], "client": (ip, 1234)}
    asyncio.new_event_loop().run_until_complete(mw(scope, receive, send))
    return sent


def _app(calls):
    async def app(scope, receive, send):
        calls.append(scope["path"])
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    return app


def test_blocks_after_max_requests():
    calls = []
    mw = RateLimitMiddleware(_app(calls), paths=("/auth/login",), max_requests=2, window_seconds=60)
    assert _call(mw, "/api/auth/login")[0]["status"] == 200
    assert _call(mw, "/api/auth/login")[0]["status"] == 200
    blocked = _call(mw, "/api/auth/login")
    assert blocked[0]["status"] == 429
    assert any(h[0] == b"retry-after" for h in blocked[0]["headers"])
    assert len(calls) == 2


def test_non_matching_path_passes_through():
    calls = []
    mw = RateLimitMiddleware(_app(calls), paths=("/auth/login",), max_requests=1, window_seconds=60)
    for _ in range(5):
        assert _call(mw, "/api/policies")[0]["status"] == 200
    assert len(calls) == 5


def test_separate_buckets_per_ip():
    calls = []
    mw = RateLimitMiddleware(_app(calls), paths=("/auth/login",), max_requests=1, window_seconds=60)
    assert _call(mw, "/api/auth/login", ip="10.0.0.1")[0]["status"] == 200
    assert _call(mw, "/api/auth/login", ip="10.0.0.2")[0]["status"] == 200
    assert _call(mw, "/api/auth/login", ip="10.0.0.1")[0]["status"] == 429


def test_forwarded_for_is_used():
    calls = []
    mw = RateLimitMiddleware(_app(calls), paths=("/auth/login",), max_requests=1, window_seconds=60)
    sent = []
    scope = {
        "type": "http",
        "path": "/api/auth/login",
        "headers": [(b"x-forwarded-for", b"203.0.113.9, 10.0.0.1")],
        "client": ("127.0.0.1", 1),
    }

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        if message["type"] == "http.response.start":
            sent.append(message)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(mw(scope, receive, send))
    loop.run_until_complete(mw(scope, receive, send))
    assert sent[0]["status"] == 200
    assert sent[1]["status"] == 429
