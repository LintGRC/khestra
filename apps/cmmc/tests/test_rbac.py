"""Tests for RBAC permission functions."""

import sys
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parents[1] / "core"
PACKAGES = Path(__file__).resolve().parents[3] / "packages"
for p in (CORE, PACKAGES):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from permissions_api import (
    can_edit_controls,
    can_edit_org,
    can_export,
    can_validate_config,
    can_view_dashboard,
    can_manage_users,
    can_manage_billing,
    role_capabilities,
)

from app_config import ROLE_PERMISSIONS

ROLES = tuple(ROLE_PERMISSIONS.keys())

# Expected capability matrix — aligned with app_config.py ROLE_PERMISSIONS
EXPECTED = {
    "Organization Admin": {"edit_controls": True, "edit_org": True, "export": True, "validate_config": True, "view_dashboard": True, "manage_users": True, "manage_billing": True},
    "Compliance Manager": {"edit_controls": True, "edit_org": True, "export": True, "validate_config": True, "view_dashboard": True, "manage_users": True, "manage_billing": False},
    "Assessor":           {"edit_controls": True, "edit_org": True, "export": True, "validate_config": True, "view_dashboard": True, "manage_users": False, "manage_billing": False},
    "Engineer":           {"edit_controls": True, "edit_org": True, "export": False, "validate_config": True, "view_dashboard": False, "manage_users": False, "manage_billing": False},
    "Executive":          {"edit_controls": False, "edit_org": False, "export": True, "validate_config": False, "view_dashboard": True, "manage_users": False, "manage_billing": False},
    "Auditor":            {"edit_controls": False, "edit_org": False, "export": True, "validate_config": False, "view_dashboard": True, "manage_users": False, "manage_billing": False},
}


class TestRolePermissions:
    def test_all_roles_have_expected_perms(self):
        for role in ROLES:
            caps = role_capabilities(role)
            exp = EXPECTED[role]
            assert caps["edit_controls"] == exp["edit_controls"], f"{role}.edit_controls"
            assert caps["edit_org"] == exp["edit_org"], f"{role}.edit_org"
            assert caps["export_data"] == exp["export"], f"{role}.export_data"
            assert caps["validate_config"] == exp["validate_config"], f"{role}.validate_config"
            assert caps["view_dashboard"] == exp["view_dashboard"], f"{role}.view_dashboard"
            assert caps["manage_users"] == exp["manage_users"], f"{role}.manage_users"
            assert caps["manage_billing"] == exp["manage_billing"], f"{role}.manage_billing"

    def test_unknown_role(self):
        caps = role_capabilities("Spy")
        assert caps == {
            "edit_controls": False, "edit_org": False, "export_data": False,
            "validate_config": False, "view_dashboard": False,
            "manage_users": False, "manage_billing": False,
        }

    def test_can_export_auditor(self):
        assert can_export("Auditor") is True

    def test_can_export_engineer(self):
        assert can_export("Engineer") is False

    def test_can_edit_controls_admin(self):
        assert can_edit_controls("Organization Admin") is True

    def test_can_edit_controls_executive(self):
        assert can_edit_controls("Executive") is False

    def test_can_edit_controls_engineer(self):
        assert can_edit_controls("Engineer") is True

    def test_can_view_dashboard_admin(self):
        assert can_view_dashboard("Organization Admin") is True

    def test_can_view_dashboard_engineer(self):
        assert can_view_dashboard("Engineer") is False

    def test_can_edit_org_admin(self):
        assert can_edit_org("Organization Admin") is True

    def test_can_edit_org_engineer(self):
        assert can_edit_org("Engineer") is True  # has edit_controls

    def test_can_edit_org_executive(self):
        assert can_edit_org("Executive") is False

    def test_empty_role(self):
        assert can_export("") is False
        assert can_edit_controls("") is False


class TestRoleCapabilitiesStructure:
    def test_all_keys_present(self):
        caps = role_capabilities("Organization Admin")
        assert "edit_controls" in caps
        assert "edit_org" in caps
        assert "export_data" in caps
        assert "validate_config" in caps
        assert "view_dashboard" in caps
        assert "manage_users" in caps
        assert "manage_billing" in caps
        assert len(caps) == 7

    def test_all_roles_produce_dict(self):
        for role in ROLES:
            caps = role_capabilities(role)
            assert isinstance(caps, dict)

    def test_all_roles_have_expected_entry(self):
        for role in ROLES:
            assert role in EXPECTED, f"Missing EXPECTED entry for role '{role}'"
