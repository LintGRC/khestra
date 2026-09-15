"""Tests for the shared personnel store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from personnel.store import (
    init_store,
    list_personnel,
    get_person,
    create_person,
    update_person,
    delete_person,
    mark_missing_as_inactive,
    seed_data,
)

# Store auto-seeds 8 sample personnel on init_store.
SEED_COUNT = 8


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"personnel_{uid}.db"
    os.environ["PERSONNEL_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("PERSONNEL_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


def _create(**kw):
    return create_person(name=kw.get("name", f"P-{uuid.uuid4().hex[:6]}"), **{k: v for k, v in kw.items() if k != "name"})


class TestPersonCRUD:
    def test_create_returns_id(self):
        p = _create(name="Alice", email="alice@example.com")
        assert p["id"]
        assert p["name"] == "Alice"
        assert p["status"] == "active"
        assert p["is_privileged"] is False

    def test_create_privileged(self):
        p = _create(name="Admin", is_privileged=True)
        assert p["is_privileged"] is True

    def test_get_person(self):
        p = _create(name="Bob")
        got = get_person(p["id"])
        assert got["name"] == "Bob"

    def test_get_missing(self):
        assert get_person("nope") is None

    def test_list_includes_seeded(self):
        assert len(list_personnel()) >= SEED_COUNT

    def test_list_by_framework(self):
        p1 = _create(name="C1", frameworks=["CMMC"])
        p2 = _create(name="C2", frameworks=["SOC 2"])
        cmmc = list_personnel(framework_id="CMMC")
        assert len(cmmc) >= 1
        assert any(p["name"] == "C1" for p in cmmc)

    def test_update_person(self):
        p = _create(name="Old")
        updated = update_person(p["id"], name="New")
        assert updated["name"] == "New"

    def test_delete_person(self):
        p = _create(name="Doomed")
        assert delete_person(p["id"]) is True
        assert get_person(p["id"]) is None

    def test_frameworks_json_roundtrip(self):
        p = _create(name="FW", frameworks=["CMMC", "SOC 2"])
        got = get_person(p["id"])
        assert set(got["frameworks"]) == {"CMMC", "SOC 2"}


class TestMarkMissingInactive:
    def test_marks_unseen_inactive(self):
        p1 = _create(name="Seen", external_id="ext-1", provider="entra", org_id="org-1")
        p2 = _create(name="Unseen", external_id="ext-2", provider="entra", org_id="org-1")
        count = mark_missing_as_inactive("entra", "org-1", {"ext-1"})
        assert count == 1
        refreshed = get_person(p2["id"])
        assert refreshed["status"] == "inactive"

    def test_seen_person_unchanged(self):
        p = _create(name="Visible", external_id="ext-1", provider="entra", org_id="org-1")
        mark_missing_as_inactive("entra", "org-1", {"ext-1"})
        refreshed = get_person(p["id"])
        assert refreshed["status"] == "active"


class TestSeedData:
    def test_seed_returns_zero_when_populated(self):
        result = seed_data()
        assert result == 0

    def test_seed_idempotent(self):
        seed_data()
        all_p = list_personnel()
        assert len(all_p) >= SEED_COUNT
