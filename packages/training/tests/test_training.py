"""Tests for the shared training store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from training.store import (
    init_store,
    list_modules,
    get_module,
    create_module,
    update_module,
    delete_module,
    list_assignments,
    get_assignment,
    create_assignment,
    create_bulk_assignments,
    update_assignment,
    bulk_complete_assignments,
    delete_assignment,
    get_stats,
    auto_assign_for_person,
)


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"training_{uid}.db"
    os.environ["TRAINING_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("TRAINING_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


class TestModuleCRUD:
    def test_create_module(self):
        m = create_module(title="Security 101", category="security")
        assert m["id"]
        assert m["title"] == "Security 101"
        assert m["is_required"] == 1

    def test_list_modules(self):
        create_module(title="A")
        create_module(title="B")
        assert len(list_modules()) == 2

    def test_get_module(self):
        m = create_module(title="Lookup")
        got = get_module(m["id"])
        assert got["title"] == "Lookup"

    def test_delete_module(self):
        m = create_module(title="Doomed")
        assert delete_module(m["id"]) is True
        assert get_module(m["id"]) is None

    def test_delete_module_cascades_assignments(self):
        m = create_module(title="Cascade")
        create_assignment(m["id"], person_id="p1")
        delete_module(m["id"])
        assert len(list_assignments(module_id=m["id"])) == 0


class TestAssignmentCRUD:
    def test_create_assignment(self):
        m = create_module(title="Mod")
        a = create_assignment(m["id"], person_id="person-1")
        assert a["id"]
        assert a["status"] == "assigned"

    def test_bulk_assignments(self):
        m = create_module(title="Bulk")
        created = create_bulk_assignments(m["id"], ["p1", "p2", "p3"])
        assert len(created) == 3

    def test_list_assignments(self):
        m = create_module(title="List")
        create_assignment(m["id"], person_id="p1")
        create_assignment(m["id"], person_id="p2")
        assert len(list_assignments()) == 2

    def test_list_by_status(self):
        m = create_module(title="Status")
        a = create_assignment(m["id"], person_id="p1")
        update_assignment(a["id"], status="completed")
        assert len(list_assignments(status="completed")) == 1

    def test_get_assignment(self):
        m = create_module(title="Get")
        a = create_assignment(m["id"], person_id="p1")
        got = get_assignment(a["id"])
        assert got is not None

    def test_delete_assignment(self):
        m = create_module(title="Del")
        a = create_assignment(m["id"], person_id="p1")
        assert delete_assignment(a["id"]) is True


class TestBulkComplete:
    def test_bulk_complete(self):
        m = create_module(title="Complete", renewal_period_days=90)
        a1 = create_assignment(m["id"], person_id="p1")
        a2 = create_assignment(m["id"], person_id="p2")
        count = bulk_complete_assignments([a1["id"], a2["id"]], "2025-01-15")
        assert count == 2
        refreshed = get_assignment(a1["id"])
        assert refreshed["status"] == "completed"
        assert refreshed["expiry_date"]  # auto-calculated


class TestAutoAssign:
    def test_auto_assign_for_person(self):
        m = create_module(title="Required", is_required=True)
        count = auto_assign_for_person("new-person")
        assert count == 1
        assignments = list_assignments(person_id="new-person")
        assert len(assignments) == 1

    def test_auto_assign_skips_existing(self):
        m = create_module(title="Skip", is_required=True)
        create_assignment(m["id"], person_id="existing")
        count = auto_assign_for_person("existing")
        assert count == 0


class TestStats:
    def test_stats_empty(self):
        s = get_stats()
        assert s["total_modules"] == 0
