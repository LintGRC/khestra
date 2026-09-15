"""Tests for the shared auth store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from auth.store import (
    init_store,
    create_user,
    authenticate,
    get_user,
    get_user_by_email,
    list_users,
    update_user_role,
    update_user_password,
    delete_user,
    user_count,
    create_org,
    get_org,
    create_invitation,
    accept_invitation,
    generate_reset_token,
    validate_reset_token,
    reset_password_with_token,
    is_user_active,
    is_user_role,
    has_admin_privilege,
)

ADMIN_EMAIL = "admin@test.local"
ADMIN_PASSWORD = "AdminPass123"


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"auth_{uid}.db"
    os.environ["AUTH_DB_PATH"] = str(db)
    os.environ["CMMC_ADMIN_EMAIL"] = ADMIN_EMAIL
    os.environ["CMMC_ADMIN_PASSWORD"] = ADMIN_PASSWORD
    init_store(str(tmp_path))
    yield
    for k in ("AUTH_DB_PATH", "CMMC_ADMIN_EMAIL", "CMMC_ADMIN_PASSWORD"):
        os.environ.pop(k, None)
    try:
        os.remove(str(db))
    except OSError:
        pass


class TestUserCRUD:
    def test_seed_admin_created(self):
        u = get_user_by_email(ADMIN_EMAIL)
        assert u is not None
        assert u["role"] == "Organization Admin"

    def test_create_user(self):
        u = create_user(email="alice@example.com", name="Alice", password="SecurePass123", role="Engineer")
        assert u["id"]
        assert u["email"] == "alice@example.com"
        assert u["role"] == "Engineer"

    def test_create_duplicate_email(self):
        create_user(email="dup@example.com", name="A", password="SecurePass123")
        with pytest.raises(ValueError, match="already"):
            create_user(email="dup@example.com", name="B", password="SecurePass123")

    def test_create_bad_email(self):
        with pytest.raises(ValueError, match="email"):
            create_user(email="not-an-email", name="X", password="SecurePass123")

    def test_create_short_password(self):
        with pytest.raises(ValueError, match="8 characters"):
            create_user(email="x@x.com", name="X", password="short")

    def test_authenticate_success(self):
        create_user(email="auth@example.com", name="A", password="SecurePass123")
        result = authenticate("auth@example.com", "SecurePass123")
        assert result is not None
        assert result["email"] == "auth@example.com"

    def test_authenticate_wrong_password(self):
        create_user(email="fail@example.com", name="A", password="SecurePass123")
        result = authenticate("fail@example.com", "WrongPassword999")
        assert result is None

    def test_authenticate_nonexistent(self):
        assert authenticate("ghost@example.com", "whatever") is None

    def test_get_user(self):
        u = create_user(email="get@example.com", name="G", password="SecurePass123")
        got = get_user(u["id"])
        assert got["name"] == "G"

    def test_get_user_by_email(self):
        create_user(email="find@example.com", name="F", password="SecurePass123")
        got = get_user_by_email("find@example.com")
        assert got["name"] == "F"

    def test_list_users_includes_seed_admin(self):
        users = list_users()
        assert len(users) >= 1
        assert any(u["email"] == ADMIN_EMAIL for u in users)

    def test_update_role(self):
        u = create_user(email="role@example.com", name="R", password="SecurePass123", role="Engineer")
        updated = update_user_role(u["id"], "Compliance Manager")
        assert updated["role"] == "Compliance Manager"

    def test_update_password(self):
        u = create_user(email="pw@example.com", name="P", password="SecurePass123")
        result = update_user_password(u["id"], "NewSecurePass456")
        assert result is True
        # Verify new password works
        authenticated = authenticate("pw@example.com", "NewSecurePass456")
        assert authenticated is not None
        # Verify old password no longer works
        old_auth = authenticate("pw@example.com", "SecurePass123")
        assert old_auth is None

    def test_delete_user_soft(self):
        u = create_user(email="del@example.com", name="D", password="SecurePass123")
        assert delete_user(u["id"]) is True
        assert is_user_active(u["id"]) is False

    def test_user_count_includes_seed(self):
        assert user_count() >= 1


class TestRoleChecks:
    def test_is_user_role(self):
        u = create_user(email="role@example.com", name="R", password="SecurePass123", role="Engineer")
        assert is_user_role(u["id"], "Engineer") is True
        assert is_user_role(u["id"], "Auditor") is False

    def test_has_admin_privilege(self):
        u = create_user(email="admin@example.com", name="A", password="SecurePass123", role="Organization Admin")
        assert has_admin_privilege(u["id"]) is True

    def test_seed_admin_has_privilege(self):
        u = get_user_by_email(ADMIN_EMAIL)
        assert has_admin_privilege(u["id"]) is True


class TestOrgs:
    def test_create_org(self):
        o = create_org(name="Acme Corp")
        assert o["id"]
        assert o["name"] == "Acme Corp"
        assert o["status"] == "active"

    def test_get_org(self):
        o = create_org(name="Lookup")
        got = get_org(o["id"])
        assert got["name"] == "Lookup"


class TestInvitations:
    def test_create_and_accept(self):
        o = create_org(name="InvOrg")
        inv = create_invitation(o["id"], "newbie@example.com", "Engineer")
        assert inv["token"]
        result = accept_invitation(inv["token"], name="Newbie", password="SecurePass123")
        assert result["email"] == "newbie@example.com"
        assert result["org_id"] == o["id"]

    def test_accept_existing_user(self):
        u = create_user(email="exist@example.com", name="Exist", password="SecurePass123", role="Engineer")
        o = create_org(name="JoinOrg")
        inv = create_invitation(o["id"], "exist@example.com", "Compliance Manager")
        result = accept_invitation(inv["token"], name="Exist", password="SecurePass123")
        assert result["org_id"] == o["id"]


class TestPasswordReset:
    def test_generate_and_validate_token(self):
        u = create_user(email="reset@example.com", name="R", password="SecurePass123")
        token = generate_reset_token("reset@example.com")
        assert token is not None
        validated = validate_reset_token(token)
        assert validated["email"] == "reset@example.com"

    def test_reset_password_with_token(self):
        create_user(email="rpw@example.com", name="R", password="SecurePass123")
        token = generate_reset_token("rpw@example.com")
        assert reset_password_with_token(token, "NewStrongPassword123!") is True
        result = authenticate("rpw@example.com", "NewStrongPassword123!")
        assert result is not None

    def test_invalid_token(self):
        assert validate_reset_token("bad-token") is None
