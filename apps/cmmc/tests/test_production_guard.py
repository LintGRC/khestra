"""Tests for the production auth-posture guard and production_config gates.

Run from repo root:
    apps/cmmc/.venv/bin/python -m pytest apps/cmmc/tests/test_production_guard.py -q
"""

from __future__ import annotations

import os

import pytest

from auth.deploy_guard import assert_safe_auth_posture, production_enabled


class TestDeployGuard:
    def test_noop_outside_production(self, monkeypatch):
        monkeypatch.delenv("KHESTRA_ENV", raising=False)
        assert_safe_auth_posture()  # no raise

    def test_blocks_local_auth_in_production(self, monkeypatch):
        monkeypatch.setenv("KHESTRA_ENV", "production")
        monkeypatch.delenv("KHESTRA_TRUSTED_NETWORK", raising=False)
        monkeypatch.setenv("CMMC_AUTH_MODE", "local")
        with pytest.raises(RuntimeError, match="Refusing to start"):
            assert_safe_auth_posture()

    def test_blocks_empty_auth_mode(self, monkeypatch):
        monkeypatch.setenv("KHESTRA_ENV", "production")
        monkeypatch.delenv("KHESTRA_TRUSTED_NETWORK", raising=False)
        monkeypatch.setenv("CMMC_AUTH_MODE", "")
        with pytest.raises(RuntimeError, match="Refusing to start"):
            assert_safe_auth_posture()

    def test_allows_with_trusted_network(self, monkeypatch):
        monkeypatch.setenv("KHESTRA_ENV", "production")
        monkeypatch.setenv("KHESTRA_TRUSTED_NETWORK", "1")
        monkeypatch.setenv("CMMC_AUTH_MODE", "local")
        assert_safe_auth_posture()  # no raise

    def test_allows_entra_in_production(self, monkeypatch):
        monkeypatch.setenv("KHESTRA_ENV", "production")
        monkeypatch.delenv("KHESTRA_TRUSTED_NETWORK", raising=False)
        monkeypatch.setenv("CMMC_AUTH_MODE", "entra")
        assert_safe_auth_posture()  # no raise


class TestProductionConfig:
    def test_demo_api_disabled_by_default(self, monkeypatch):
        monkeypatch.delenv("DEMO_MODE", raising=False)
        monkeypatch.setenv("CMMC_SANDBOX_MODE", "0")
        from production_config import demo_api_enabled
        assert demo_api_enabled() is False

    def test_demo_api_enabled_with_flag(self, monkeypatch):
        monkeypatch.setenv("DEMO_MODE", "1")
        from production_config import demo_api_enabled
        assert demo_api_enabled() is True

    def test_cors_defaults_localhost(self, monkeypatch):
        monkeypatch.delenv("CMMC_ALLOWED_ORIGINS", raising=False)
        from production_config import allowed_cors_origins
        origins = allowed_cors_origins()
        assert all("localhost" in o or "127.0.0.1" in o for o in origins)

    def test_cors_honors_allowlist(self, monkeypatch):
        monkeypatch.setenv("CMMC_ALLOWED_ORIGINS", "https://app.khestra.com,https://staging.khestra.com")
        from production_config import allowed_cors_origins
        origins = allowed_cors_origins()
        assert "https://app.khestra.com" in origins
        assert "https://staging.khestra.com" in origins
