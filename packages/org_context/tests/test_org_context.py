"""Tests for the shared org_context store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from org_context.store import (
    init_store,
    list_records,
    get_record,
    create_record,
    update_record,
    delete_record,
    stats,
)


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"orgctx_{uid}.db"
    os.environ["ORG_CONTEXT_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("ORG_CONTEXT_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


class TestRecordCRUD:
    def test_create_record(self):
        r = create_record(label="ISMS Scope 1", scope_statement="Cloud SaaS")
        assert r["id"]
        assert r["label"] == "ISMS Scope 1"
        assert r["scope_statement"] == "Cloud SaaS"

    def test_get_record(self):
        r = create_record(label="Lookup")
        got = get_record(r["id"])
        assert got["label"] == "Lookup"

    def test_get_missing(self):
        assert get_record("nope") is None

    def test_list_records(self):
        create_record(label="A")
        create_record(label="B")
        assert len(list_records()) == 2

    def test_update_record(self):
        r = create_record(label="Old")
        updated = update_record(r["id"], label="New")
        assert updated["label"] == "New"

    def test_delete_record(self):
        r = create_record(label="Doomed")
        assert delete_record(r["id"]) is True
        assert get_record(r["id"]) is None


class TestClimateAutoDetection:
    def test_auto_climate_relevant(self):
        r = create_record(label="Climate", internal_issues=["Climate change impacts"])
        assert r["climate_relevant"] is True
        assert r["climate_status"] == "relevant"

    def test_no_auto_climate(self):
        r = create_record(label="Normal", internal_issues=["Budget constraints"])
        assert r["climate_relevant"] is False
        assert r["climate_status"] == "not_assessed"

    def test_manual_climate_flag(self):
        r = create_record(label="Manual", climate_relevant=True, climate_note="Per ISO 14001")
        assert r["climate_relevant"] is True
        assert r["climate_status"] == "relevant"


class TestClimateStatusDetermination:
    """Amd 1:2024 requires an explicit determination; `not_assessed` must be
    distinguishable from a deliberate 'not relevant' conclusion."""

    def test_default_is_not_assessed(self):
        r = create_record(label="Fresh")
        assert r["climate_status"] == "not_assessed"
        assert r["climate_relevant"] is False

    def test_explicit_relevant(self):
        r = create_record(label="Relevant", climate_status="relevant")
        assert r["climate_status"] == "relevant"
        assert r["climate_relevant"] is True

    def test_explicit_not_relevant_does_not_auto_trigger(self):
        r = create_record(
            label="Not relevant",
            climate_status="not_relevant",
            internal_issues=["Budget constraints"],
        )
        assert r["climate_status"] == "not_relevant"
        assert r["climate_relevant"] is False

    def test_update_status_transitions_bool(self):
        r = create_record(label="Trans")
        u = update_record(r["id"], climate_status="relevant", climate_note="Assessed via 4.1")
        assert u["climate_status"] == "relevant"
        assert u["climate_relevant"] is True
        u2 = update_record(r["id"], climate_status="not_relevant")
        assert u2["climate_status"] == "not_relevant"
        assert u2["climate_relevant"] is False

    def test_invalid_status_ignored(self):
        r = create_record(label="Bad")
        u = update_record(r["id"], climate_status="banana")
        assert u["climate_status"] == "not_assessed"

    def test_legacy_bool_backwards_compatible(self):
        r = create_record(label="Legacy", climate_relevant=True)
        assert r["climate_status"] == "relevant"
        u = update_record(r["id"], climate_relevant=False)
        assert u["climate_relevant"] is False
        assert u["climate_status"] in ("not_assessed", "not_relevant")


class TestStats:
    def test_stats_empty(self):
        s = stats()
        assert s["total"] == 0
        assert s["climate_relevant"] == 0

    def test_stats_with_data(self):
        create_record(label="A", climate_relevant=True)
        create_record(label="B", climate_relevant=False)
        s = stats()
        assert s["total"] == 2
        assert s["climate_relevant"] == 1
