"""Tests for the shared audit_center store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from audit_center.store import (
    init_store,
    list_audits,
    get_audit,
    create_audit,
    update_audit,
    delete_audit,
    freeze_audit,
    list_requests,
    get_request,
    create_request,
    update_request,
    delete_request,
    get_stats,
)


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"audit_center_{uid}.db"
    os.environ["AUDIT_CENTER_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("AUDIT_CENTER_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


class TestAuditCRUD:
    def test_create_audit(self):
        a = create_audit(title="ISO 27001 Certification", framework="ISO 27001", audit_type="certification")
        assert a["id"]
        assert a["title"] == "ISO 27001 Certification"
        assert a["status"] == "planned"

    def test_get_audit(self):
        a = create_audit(title="Lookup")
        got = get_audit(a["id"])
        assert got["title"] == "Lookup"

    def test_get_missing(self):
        assert get_audit("nope") is None

    def test_list_audits(self):
        create_audit(title="A", framework="CMMC")
        create_audit(title="B", framework="SOC 2")
        assert len(list_audits()) == 2

    def test_list_by_framework(self):
        create_audit(title="C", framework="CMMC")
        create_audit(title="S", framework="SOC 2")
        assert len(list_audits(framework="CMMC")) == 1

    def test_update_audit(self):
        a = create_audit(title="Old")
        updated = update_audit(a["id"], title="New")
        assert updated["title"] == "New"

    def test_delete_audit(self):
        a = create_audit(title="Doomed")
        assert delete_audit(a["id"]) is True
        assert get_audit(a["id"]) is None


class TestFreezeAudit:
    def test_freeze(self):
        a = create_audit(title="Freeze Me")
        frozen = freeze_audit(a["id"])
        assert frozen["status"] == "frozen"


class TestEvidenceRequests:
    def test_create_request(self):
        a = create_audit(title="Parent")
        r = create_request(a["id"], title="Provide access logs", control_id="AC.L2-3.1.1")
        assert r["id"]
        assert r["status"] == "open"

    def test_list_requests(self):
        a = create_audit(title="Parent")
        create_request(a["id"], title="Req 1")
        create_request(a["id"], title="Req 2")
        assert len(list_requests(a["id"])) == 2

    def test_get_request(self):
        a = create_audit(title="P")
        r = create_request(a["id"], title="Lookup")
        got = get_request(r["id"])
        assert got["title"] == "Lookup"

    def test_update_request(self):
        a = create_audit(title="P")
        r = create_request(a["id"], title="Old")
        updated = update_request(r["id"], status="approved")
        assert updated["status"] == "approved"

    def test_delete_request(self):
        a = create_audit(title="P")
        r = create_request(a["id"], title="Del")
        assert delete_request(r["id"]) is True

    def test_delete_audit_cascades_requests(self):
        a = create_audit(title="Cascade")
        create_request(a["id"], title="R1")
        delete_audit(a["id"])
        assert len(list_requests(a["id"])) == 0


class TestStats:
    def test_stats_empty(self):
        s = get_stats()
        assert s["total_audits"] == 0
        assert s["total_evidence_requests"] == 0

    def test_stats_with_data(self):
        a = create_audit(title="A", framework="CMMC")
        create_request(a["id"], title="R1")
        s = get_stats()
        assert s["total_audits"] == 1
        assert s["total_evidence_requests"] == 1
