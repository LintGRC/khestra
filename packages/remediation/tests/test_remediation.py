"""Tests for the shared remediation store."""
from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from remediation.store import RemediationStore
from remediation.models import RemediationItem, REMEDIATION_TYPES


@pytest.fixture
def store(tmp_path):
    return RemediationStore(tmp_path)


def _item(**kw):
    defaults = {
        "id": f"rem-{__import__('uuid').uuid4().hex[:8]}",
        "title": "Fix issue",
        "type": "gap",
        "framework": "CMMC",
        "status": "open",
        "priority": "medium",
    }
    defaults.update(kw)
    return RemediationItem(**defaults)


class TestCRUD:
    def test_upsert_and_get(self, store):
        item = _item(id="rem-1")
        store.upsert(item)
        got = store.get("rem-1")
        assert got is not None
        assert got.title == "Fix issue"

    def test_list_empty(self, store):
        assert store.list() == []

    def test_list_with_data(self, store):
        store.upsert(_item(id="rem-a", title="A"))
        store.upsert(_item(id="rem-b", title="B"))
        assert len(store.list()) == 2

    def test_upsert_updates(self, store):
        store.upsert(_item(id="rem-1", title="Old"))
        store.upsert(_item(id="rem-1", title="New"))
        got = store.get("rem-1")
        assert got.title == "New"

    def test_delete(self, store):
        store.upsert(_item(id="rem-1"))
        assert store.delete("rem-1") is True
        assert store.get("rem-1") is None

    def test_delete_missing(self, store):
        assert store.delete("nope") is False


class TestFiltering:
    def test_filter_by_framework(self, store):
        store.upsert(_item(id="r1", framework="CMMC"))
        store.upsert(_item(id="r2", framework="SOC 2"))
        cmmc = store.list(framework="CMMC")
        assert len(cmmc) == 1
        assert cmmc[0].framework == "CMMC"

    def test_filter_by_status(self, store):
        store.upsert(_item(id="r1", status="open"))
        store.upsert(_item(id="r2", status="completed"))
        assert len(store.list(status="open")) == 1

    def test_filter_by_type(self, store):
        store.upsert(_item(id="r1", type="gap"))
        store.upsert(_item(id="r2", type="finding"))
        assert len(store.list(type_filter="gap")) == 1


class TestCount:
    def test_count_empty(self, store):
        assert store.count() == 0

    def test_count_filtered(self, store):
        store.upsert(_item(id="r1", framework="CMMC"))
        store.upsert(_item(id="r2", framework="SOC 2"))
        assert store.count(framework="CMMC") == 1


class TestStats:
    def test_stats_empty(self, store):
        s = store.stats()
        assert s["total"] == 0
        assert s["by_status"] == {}

    def test_stats_with_data(self, store):
        store.upsert(_item(id="r1", status="open", priority="high"))
        store.upsert(_item(id="r2", status="completed", priority="low"))
        s = store.stats()
        assert s["total"] == 2
        assert s["by_status"]["open"] == 1
        assert s["open"] == 1


class TestTypes:
    def test_all_types_valid(self):
        for t in REMEDIATION_TYPES:
            item = _item(type=t)
            assert item.type == t
