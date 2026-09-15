"""Tests for the shared vendor manager store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from vendors.store import (
    init_store,
    list_vendors,
    get_vendor,
    create_vendor,
    update_vendor,
    delete_vendor,
    save_draft_response,
    submit_response,
    get_response_by_vendor,
    create_assessment,
    get_assessment_by_vendor,
    create_remediation,
    list_remediations,
    link_framework,
    unlink_framework,
    export_vendors_csv,
    list_activities,
)

# Store auto-seeds demo vendors on init.
SEED_COUNT = 3


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"vendors_{uid}.db"
    os.environ["VENDOR_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("VENDOR_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


def _create(**kw):
    return create_vendor(name=kw.get("name", f"V-{uuid.uuid4().hex[:6]}"), **{k: v for k, v in kw.items() if k != "name"})


class TestVendorCRUD:
    def test_create_returns_id(self):
        v = _create(name="Acme")
        assert v["id"]
        assert v["name"] == "Acme"
        assert v["status"] == "pending"

    def test_access_token_hidden(self):
        v = _create(name="Secret")
        fetched = get_vendor(v["id"])
        assert "access_token" not in fetched
        assert fetched.get("has_access_token") is True

    def test_get_vendor(self):
        v = _create(name="Lookup")
        got = get_vendor(v["id"])
        assert got["name"] == "Lookup"

    def test_get_missing(self):
        assert get_vendor("nope") is None

    def test_list_includes_seeded(self):
        assert len(list_vendors()) >= SEED_COUNT

    def test_list_by_framework(self):
        v1 = _create(name="C1")
        link_framework(v1["id"], "CMMC")
        cmmc = list_vendors(framework_id="CMMC")
        assert len(cmmc) >= 1
        assert any(v["name"] == "C1" for v in cmmc)

    def test_delete_vendor(self):
        v = _create(name="Doomed")
        assert delete_vendor(v["id"]) is True
        assert get_vendor(v["id"]) is None


class TestFrameworkLinking:
    def test_link_and_list(self):
        v = _create(name="Linked")
        link_framework(v["id"], "SOC 2")
        linked = list_vendors(framework_id="SOC 2")
        assert any(v["name"] == "Linked" for v in linked)

    def test_unlink(self):
        v = _create(name="Unlink")
        link_framework(v["id"], "CMMC")
        unlink_framework(v["id"], "CMMC")
        linked = list_vendors(framework_id="CMMC")
        assert not any(v["name"] == "Unlink" for v in linked)


class TestResponses:
    def test_draft_response(self):
        v = _create(name="Resp")
        r = save_draft_response(v["id"], answers=[{"q": "Q1", "a": "A1"}])
        assert r["id"]
        assert r["status"] == "draft"

    def test_submit_response(self):
        v = _create(name="Submit")
        r = submit_response(v["id"], answers=[{"q": "Q1", "a": "A1"}])
        assert r["status"] == "submitted"
        fetched = get_response_by_vendor(v["id"])
        assert fetched["status"] == "submitted"


class TestRemediations:
    def test_create_and_list(self):
        v = _create(name="Remed")
        rem = create_remediation(v["id"], assessment_id="a1", description="fix this")
        assert rem["id"]
        items = list_remediations(vendor_id=v["id"])
        assert len(items) == 1


class TestActivities:
    def test_activities_logged(self):
        v = _create(name="Acts")
        acts = list_activities(v["id"])
        # create_vendor logs an activity
        assert len(acts) >= 1


class TestCSVExport:
    def test_export_csv(self):
        v = _create(name="Export")
        csv = export_vendors_csv([v])
        assert "Export" in csv
        assert "name" in csv
