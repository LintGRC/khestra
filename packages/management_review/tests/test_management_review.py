"""Tests for the shared management_review store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from management_review.store import (
    init_store,
    list_reviews,
    get_review,
    create_review,
    update_review,
    delete_review,
    stats,
    REVIEW_STATUSES,
    DEFAULT_INPUTS,
)


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"mgmt_review_{uid}.db"
    os.environ["MANAGEMENT_REVIEW_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("MANAGEMENT_REVIEW_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


class TestReviewCRUD:
    def test_create_review(self):
        r = create_review(title="Q1 2025 Review", date="2025-03-31")
        assert r["id"]
        assert r["title"] == "Q1 2025 Review"
        assert r["status"] == "scheduled"

    def test_create_with_invalid_status(self):
        r = create_review(title="Bad", status="invalid_status")
        assert r["status"] == "scheduled"  # falls back to default

    def test_get_review(self):
        r = create_review(title="Lookup")
        got = get_review(r["id"])
        assert got["title"] == "Lookup"

    def test_get_missing(self):
        assert get_review("nope") is None

    def test_list_reviews(self):
        create_review(title="A")
        create_review(title="B")
        assert len(list_reviews()) == 2

    def test_list_by_status(self):
        create_review(title="S", status="scheduled")
        create_review(title="C", status="completed")
        assert len(list_reviews(status="completed")) == 1

    def test_update_review(self):
        r = create_review(title="Old")
        updated = update_review(r["id"], title="New")
        assert updated["title"] == "New"

    def test_delete_review(self):
        r = create_review(title="Doomed")
        assert delete_review(r["id"]) is True
        assert get_review(r["id"]) is None


class TestReviewContent:
    def test_attendees(self):
        r = create_review(title="Att", attendees=[{"name": "Alice", "role": "CISO"}])
        got = get_review(r["id"])
        assert len(got["attendees"]) == 1
        assert got["attendees"][0]["name"] == "Alice"

    def test_inputs_and_outputs(self):
        r = create_review(
            title="IO",
            inputs=[{"item": "audit_results", "status": "complete"}],
            outputs=[{"category": "improvement", "description": "Update policy X"}],
        )
        got = get_review(r["id"])
        assert len(got["inputs"]) == 1
        assert len(got["outputs"]) == 1

    def test_action_items(self):
        r = create_review(
            title="Actions",
            action_items=[{"description": "Do thing", "owner": "Bob", "status": "open"}],
        )
        got = get_review(r["id"])
        assert len(got["action_items"]) == 1


class TestStats:
    def test_stats_empty(self):
        s = stats()
        assert s["total"] == 0

    def test_stats_with_data(self):
        create_review(title="S", status="scheduled")
        create_review(title="C", status="completed")
        s = stats()
        assert s["total"] == 2
        assert s["by_status"]["scheduled"] == 1


class TestDefaults:
    def test_default_inputs_defined(self):
        assert len(DEFAULT_INPUTS) == 8
        assert all(len(item) == 2 for item in DEFAULT_INPUTS)

    def test_valid_statuses(self):
        assert "scheduled" in REVIEW_STATUSES
        assert "completed" in REVIEW_STATUSES
