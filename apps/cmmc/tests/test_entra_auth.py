"""Tests for Entra ID role mapping (no live tokens)."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

CORE = Path(__file__).resolve().parents[1] / "core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from entra_auth.config import auth_enabled, load_group_map
from entra_auth.user import resolve_role_from_claims


class EntraAuthTests(unittest.TestCase):
    def test_auth_disabled_without_tenant(self) -> None:
        from unittest.mock import patch

        for key in (
            "CMMC_ENTRA_TENANT_ID",
            "CMMC_ENTRA_CLIENT_ID",
            "CMMC_ENTRA_AUTH_ENABLED",
            "CMMC_AUTH_SECRET",
            "CMMC_AUTH_MODE",
        ):
            os.environ.pop(key, None)
        # No tenant config, no auth secret file, no explicit mode → disabled.
        with patch("entra_auth.config._auth_secret_file", return_value="/nonexistent/auth_secret"):
            self.assertFalse(auth_enabled())

    def test_auth_local_fallback_with_secret_file(self) -> None:
        import tempfile

        from unittest.mock import patch

        for key in (
            "CMMC_ENTRA_TENANT_ID",
            "CMMC_ENTRA_CLIENT_ID",
            "CMMC_ENTRA_AUTH_ENABLED",
            "CMMC_AUTH_SECRET",
            "CMMC_AUTH_MODE",
        ):
            os.environ.pop(key, None)
        # Without tenant config, an existing local auth_secret file enables local auth.
        with tempfile.TemporaryDirectory() as tmp:
            secret = Path(tmp) / "auth_secret"
            secret.write_text("test-secret")
            with patch("entra_auth.config._auth_secret_file", return_value=str(secret)):
                self.assertTrue(auth_enabled())

    def test_auth_secret_file_prefers_shared_auth_db_dir(self) -> None:
        import os as _os

        from unittest.mock import patch

        from entra_auth import config as entra_config

        with patch.dict(_os.environ, {"AUTH_DB_PATH": "/shared/auth/auth.db"}):
            self.assertEqual(
                entra_config._auth_secret_file(),
                "/shared/auth/auth_secret",
            )

    def test_group_map_from_env(self) -> None:
        os.environ["CMMC_ENTRA_GROUP_ASSESSOR"] = "aaa-bbb-ccc"
        os.environ["CMMC_ENTRA_GROUP_ENGINEER"] = "ddd-eee-fff"
        try:
            mapping = load_group_map()
            self.assertEqual(mapping["aaa-bbb-ccc"], "Assessor")
            self.assertEqual(mapping["ddd-eee-fff"], "Engineer")
        finally:
            os.environ.pop("CMMC_ENTRA_GROUP_ASSESSOR", None)
            os.environ.pop("CMMC_ENTRA_GROUP_ENGINEER", None)

    def test_resolve_role_priority(self) -> None:
        os.environ["CMMC_ENTRA_GROUP_MAP"] = (
            '{"g1": "Engineer", "g2": "Compliance Manager", "g3": "Assessor"}'
        )
        os.environ["CMMC_ENTRA_REQUIRE_GROUP"] = "1"
        try:
            role = resolve_role_from_claims({"groups": ["g1", "g2", "g3"]})
            self.assertEqual(role, "Compliance Manager")
        finally:
            os.environ.pop("CMMC_ENTRA_GROUP_MAP", None)
            os.environ.pop("CMMC_ENTRA_REQUIRE_GROUP", None)

    def test_app_roles_claim(self) -> None:
        os.environ["CMMC_ENTRA_REQUIRE_GROUP"] = "1"
        os.environ.pop("CMMC_ENTRA_GROUP_MAP", None)
        for key in list(os.environ):
            if key.startswith("CMMC_ENTRA_GROUP_"):
                os.environ.pop(key, None)
        try:
            role = resolve_role_from_claims({"roles": ["Executive"]})
            self.assertEqual(role, "Executive")
        finally:
            os.environ.pop("CMMC_ENTRA_REQUIRE_GROUP", None)

    def test_no_group_denied_when_required(self) -> None:
        os.environ["CMMC_ENTRA_REQUIRE_GROUP"] = "1"
        os.environ["CMMC_ENTRA_GROUP_MAP"] = "{}"
        try:
            self.assertIsNone(resolve_role_from_claims({"groups": []}))
        finally:
            os.environ.pop("CMMC_ENTRA_REQUIRE_GROUP", None)
            os.environ.pop("CMMC_ENTRA_GROUP_MAP", None)


if __name__ == "__main__":
    unittest.main()
