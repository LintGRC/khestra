"""Tests for the shared findings store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from findings.store import (
    init_store,
    list_findings,
    get_finding,
    create_finding,
    update_finding,
    delete_finding,
    list_actions,
    get_action,
    create_action,
    update_action,
    delete_action,
    by_severity,
    by_status,
    by_framework,
    by_source,
)


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"findings_{uid}.db"
    os.environ["FINDINGS_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("FINDINGS_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


class TestFindingCRUD:
    def test_create_finding(self):
        f = create_finding(title="SQL Injection", severity="critical")
        assert f["id"]
        assert f["title"] == "SQL Injection"
        assert f["severity"] == "critical"
        assert f["status"] == "open"

    def test_get_finding(self):
        f = create_finding(title="XSS")
        got = get_finding(f["id"])
        assert got["title"] == "XSS"

    def test_get_missing(self):
        assert get_finding("nope") is None

    def test_list_findings(self):
        create_finding(title="A")
        create_finding(title="B")
        assert len(list_findings()) == 2

    def test_list_by_severity(self):
        create_finding(title="C", severity="critical")
        create_finding(title="L", severity="low")
        assert len(list_findings(severity="critical")) == 1

    def test_list_by_framework(self):
        create_finding(title="C", framework="CMMC")
        create_finding(title="S", framework="SOC 2")
        assert len(list_findings(framework="CMMC")) == 1

    def test_list_by_control_id(self):
        create_finding(title="AC", control_ids=["AC.L2-3.1.1"])
        assert len(list_findings(control_id="AC.L2-3.1.1")) == 1

    def test_update_finding(self):
        f = create_finding(title="Old")
        updated = update_finding(f["id"], title="New")
        assert updated["title"] == "New"

    def test_delete_finding(self):
        f = create_finding(title="Doomed")
        assert delete_finding(f["id"]) is True
        assert get_finding(f["id"]) is None


class TestActions:
    def test_create_action(self):
        f = create_finding(title="Parent")
        a = create_action(f["id"], title="Fix it")
        assert a["id"]
        assert a["title"] == "Fix it"
        assert a["status"] == "open"

    def test_create_action_invalid_finding(self):
        result = create_action("nonexistent", title="Orphan")
        assert result is None

    def test_list_actions(self):
        f = create_finding(title="Parent")
        create_action(f["id"], title="A")
        create_action(f["id"], title="B")
        assert len(list_actions(f["id"])) == 2

    def test_get_action(self):
        f = create_finding(title="P")
        a = create_action(f["id"], title="X")
        got = get_action(a["id"])
        assert got["title"] == "X"

    def test_update_action(self):
        f = create_finding(title="P")
        a = create_action(f["id"], title="Old")
        updated = update_action(a["id"], title="New")
        assert updated["title"] == "New"

    def test_delete_action(self):
        f = create_finding(title="P")
        a = create_action(f["id"], title="Del")
        assert delete_action(a["id"]) is True

    def test_delete_finding_cascades_actions(self):
        f = create_finding(title="Cascade")
        create_action(f["id"], title="A1")
        delete_finding(f["id"])
        assert len(list_actions(f["id"])) == 0


class TestAggregations:
    def test_by_severity(self):
        create_finding(title="C", severity="critical")
        create_finding(title="L", severity="low")
        s = by_severity()
        assert s["critical"] == 1
        assert s["low"] == 1

    def test_by_status(self):
        create_finding(title="O", status="open")
        create_finding(title="C", status="closed")
        s = by_status()
        assert s["open"] == 1

    def test_by_framework(self):
        create_finding(title="C", framework="CMMC")
        s = by_framework()
        assert s["CMMC"] == 1

    def test_by_source(self):
        create_finding(title="A", source="audit")
        s = by_source()
        assert s["audit"] == 1
