"""Tests for the shared incidents store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from incidents.store import (
    init_store,
    list_incidents,
    get_incident,
    create_incident,
    update_incident,
    transition_incident,
    delete_incident,
    add_corrective_action,
    update_corrective_action,
    save_telemetry,
    get_stats,
    auto_classify,
    seed_incidents,
    STATUSES,
    REGULATORY_DEADLINES,
)


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"incidents_{uid}.db"
    os.environ["INCIDENTS_DB_PATH"] = str(db)
    os.environ["EVIDENCE_FILES_DIR"] = str(tmp_path / "evidence")
    init_store(str(tmp_path))
    yield
    for k in ("INCIDENTS_DB_PATH", "EVIDENCE_FILES_DIR"):
        os.environ.pop(k, None)
    try:
        os.remove(str(db))
    except OSError:
        pass


def _create(**kw):
    return create_incident(
        title=kw.get("title", f"I-{uuid.uuid4().hex[:6]}"),
        **{k: v for k, v in kw.items() if k != "title"},
    )


class TestCreateAndGetIncident:
    def test_create_returns_id(self):
        inc = _create(title="Breach")
        assert inc["id"]
        assert inc["title"] == "Breach"
        assert inc["status"] == "triage"

    def test_create_with_severity(self):
        inc = _create(title="Critical", severity="critical")
        clock = inc["regulatory_clock"]
        assert clock["days"] == REGULATORY_DEADLINES["critical"]
        assert "deadline" in clock

    def test_get_incident(self):
        inc = _create(title="Lookup")
        got = get_incident(inc["id"])
        assert got["title"] == "Lookup"

    def test_get_missing(self):
        assert get_incident("nope") is None


class TestListIncidents:
    def test_list_empty(self):
        items, total = list_incidents()
        assert items == []
        assert total == 0

    def test_list_by_severity(self):
        _create(title="A", severity="medium")
        _create(title="B", severity="critical")
        items, total = list_incidents(severity="critical")
        assert total == 1

    def test_list_pagination(self):
        for i in range(5):
            _create(title=f"I{i}")
        items, total = list_incidents(limit=2, offset=0)
        assert len(items) == 2
        assert total == 5


class TestTransitionIncident:
    def test_valid_transition(self):
        inc = _create(title="T")
        updated = transition_incident(inc["id"], "investigation", detail="Starting")
        assert updated["status"] == "investigation"
        assert "investigation_at" in updated["timeline"]

    def test_full_lifecycle(self):
        inc = _create(title="LC")
        for status in STATUSES[1:]:
            inc = transition_incident(inc["id"], status)
        assert inc["status"] == "closed"

    def test_invalid_status_rejected(self):
        inc = _create(title="T")
        result = transition_incident(inc["id"], "bogus_status")
        assert result is None


class TestUpdateIncident:
    def test_update_title(self):
        inc = _create(title="Old")
        updated = update_incident(inc["id"], {"title": "New"})
        assert updated["title"] == "New"


class TestDeleteIncident:
    def test_delete(self):
        inc = _create(title="Doomed")
        assert delete_incident(inc["id"]) is True
        assert get_incident(inc["id"]) is None


class TestCorrectiveActions:
    def test_add_and_update(self):
        inc = _create(title="CA")
        ca = add_corrective_action(inc["id"], description="Fix it", assigned_to="alice")
        assert ca["id"]
        assert ca["description"] == "Fix it"
        updated = update_corrective_action(inc["id"], ca["id"], {"status": "completed"})
        assert updated["status"] == "completed"


class TestTelemetry:
    def test_save_telemetry(self):
        inc = _create(title="Telem")
        result = save_telemetry(inc["id"], {
            "prompt": "test prompt",
            "response": "test response",
            "model_parameters": {"temp": 0.7},
        })
        assert result is not None
        telem = result["telemetry"]
        assert isinstance(telem, dict)
        assert telem.get("prompt") == "test prompt"
        assert telem.get("response") == "test response"


class TestAutoClassify:
    def test_classify(self):
        inc = _create(title="Classify", severity="low")
        result = auto_classify(inc["id"])
        assert result is not None


class TestStats:
    def test_stats_empty(self):
        s = get_stats()
        assert s["total"] == 0


class TestSeedIncidents:
    def test_seed_populates(self):
        seeded = seed_incidents()
        assert len(seeded) > 0
        items, total = list_incidents()
        assert total == len(seeded)

    def test_seed_idempotent(self):
        seed_incidents()
        items1, total1 = list_incidents()
        seed_incidents()
        items2, total2 = list_incidents()
        assert total1 == total2
