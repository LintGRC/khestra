"""Shared TestClient fixture for AI Gov parity tests.

The aigov app authenticates every /api/* request via `aigov_auth_middleware`
against the shared auth store. Login with the seeded admin whose password is
recorded in `data/auth_admin_credentials.txt` (written by auth.store's seed
on first startup); fall back to a deterministic env-seeded admin otherwise.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _admin_password() -> str:
    creds_file = DATA_DIR / "auth_admin_credentials.txt"
    if creds_file.is_file():
        for line in creds_file.read_text().splitlines():
            if line.lower().startswith("password:"):
                return line.split(":", 1)[1].strip()
    os.environ.setdefault("CMMC_ADMIN_PASSWORD", "StrongPassword123!")
    return "StrongPassword123!"


@pytest.fixture
def client():
    from server.main import app

    with TestClient(app) as test_client:
        resp = test_client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": _admin_password()},
        )
        token = resp.json()["token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client
