"""Tests for the shared risk register store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from risks.store import (
    init_store,
    list_risks,
    get_risk,
    create_risk,
    update_risk,
    delete_risk,
    add_comment,
    get_stats,
    seed_risks,
    get_risks_by_control,
)

# The store auto-seeds 14 sample risks on init_store.
SEED_COUNT = 14


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"risks_{uid}.db"
    os.environ["RISKS_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("RISKS_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


# ------------------------------------------------------------------


class TestCreateAndGetRisk:
    def test_create_returns_id_and_defaults(self):
        r = create_risk(title="Test Risk")
        assert r["id"]
        assert r["title"] == "Test Risk"
        assert r["status"] == "identified"
        assert r["likelihood"] == 0
        assert r["impact"] == 0
        assert r["inherent_score"] == 0

    def test_create_with_scores(self):
        r = create_risk(title="Scored", likelihood=4, impact=5)
        assert r["inherent_score"] == 20

    def test_get_risk(self):
        r = create_risk(title="Lookup")
        got = get_risk(r["id"])
        assert got is not None
        assert got["title"] == "Lookup"

    def test_get_risk_missing(self):
        assert get_risk("nonexistent") is None


class TestListRisks:
    def test_list_includes_seeded(self):
        rows = list_risks()
        assert len(rows) == SEED_COUNT

    def test_list_by_framework(self):
        # Seeded risks may include various frameworks; add our own
        create_risk(title="A", framework="CMMC")
        cmmc = list_risks(framework="CMMC")
        assert len(cmmc) >= 1
        assert any(r["title"] == "A" for r in cmmc)

    def test_list_by_status(self):
        create_risk(title="Closed", status="closed")
        closed = list_risks(status="closed")
        assert len(closed) >= 1
        assert any(r["title"] == "Closed" for r in closed)

    def test_list_by_owner(self):
        create_risk(title="Mine", owner="alice")
        mine = list_risks(owner="alice")
        assert len(mine) == 1
        assert mine[0]["title"] == "Mine"

    def test_list_by_control_id_column(self):
        create_risk(title="Direct", control_id="AC.L2-3.1.1")
        res = list_risks(control_id="AC.L2-3.1.1")
        assert len(res) >= 1
        assert any(r["title"] == "Direct" for r in res)

    def test_list_by_control_ids_json(self):
        create_risk(title="Array", control_ids=["AC.L2-3.1.1", "AC.L2-3.1.2"])
        res = list_risks(control_id="AC.L2-3.1.2")
        assert len(res) >= 1
        assert any(r["title"] == "Array" for r in res)


class TestUpdateRisk:
    def test_update_title(self):
        r = create_risk(title="Old")
        updated = update_risk(r["id"], title="New")
        assert updated is not None
        assert updated["title"] == "New"

    def test_update_recomputes_inherent_score(self):
        r = create_risk(title="X", likelihood=2, impact=3)
        assert r["inherent_score"] == 6
        updated = update_risk(r["id"], likelihood=5, impact=5)
        assert updated["inherent_score"] == 25

    def test_update_recomputes_residual_score(self):
        r = create_risk(title="X", residual_likelihood=2, residual_impact=3)
        updated = update_risk(r["id"], residual_likelihood=4, residual_impact=4)
        assert updated["residual_score"] == 16

    def test_update_missing(self):
        assert update_risk("nope", title="X") is None


class TestDeleteRisk:
    def test_delete(self):
        r = create_risk(title="Doomed")
        assert delete_risk(r["id"]) is True
        assert get_risk(r["id"]) is None

    def test_delete_missing(self):
        assert delete_risk("nope") is False


class TestComments:
    def test_add_comment(self):
        r = create_risk(title="With Comment")
        c = add_comment(r["id"], author="alice", body="looks good")
        assert c["author"] == "alice"
        assert c["body"] == "looks good"
        got = get_risk(r["id"])
        assert len(got["comments"]) == 1

    def test_add_multiple_comments(self):
        r = create_risk(title="Multi")
        add_comment(r["id"], author="a", body="1")
        add_comment(r["id"], author="b", body="2")
        got = get_risk(r["id"])
        assert len(got["comments"]) == 2


class TestStats:
    def test_stats_reflects_seeded(self):
        s = get_stats()
        assert s["total"] == SEED_COUNT

    def test_stats_with_new_data(self):
        create_risk(title="R1", status="identified", framework="CMMC")
        s = get_stats()
        assert s["total"] == SEED_COUNT + 1


class TestSeedRisks:
    def test_seed_returns_empty_when_populated(self):
        # seed_risks is already called during init_store; calling again returns []
        result = seed_risks()
        assert result == []

    def test_seed_idempotent(self):
        seed_risks()
        all_risks = list_risks()
        assert len(all_risks) == SEED_COUNT


class TestGetRisksByControl:
    def test_by_control_id(self):
        create_risk(title="R1", control_id="AC.L2-3.1.1")
        res = get_risks_by_control("AC.L2-3.1.1")
        assert len(res) >= 1
        assert any(r["title"] == "R1" for r in res)

    def test_by_control_ids_array(self):
        create_risk(title="R2", control_ids=["AC.L2-3.1.1", "AU.L2-3.3.1"])
        res = get_risks_by_control("AU.L2-3.3.1")
        assert len(res) >= 1
        assert any(r["title"] == "R2" for r in res)
