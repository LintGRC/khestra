"""Tests for compliance calendar milestones (cross-service program clocks).

Run from repo root:
    apps/cmmc/.venv/bin/python -m pytest packages/compliance_calendar/tests/test_store.py -q
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
if str(PACKAGES) not in sys.path:
    sys.path.insert(0, str(PACKAGES))

from compliance_calendar.store import (  # noqa: E402
    clear_milestones,
    init_store,
    list_milestones,
    upsert_milestone,
)


@pytest.fixture(autouse=True)
def _env(tmp_path):
    os.environ["COMPLIANCE_CALENDAR_DB_PATH"] = str(tmp_path / "milestones.db")
    init_store(str(tmp_path))
    yield


class TestMilestones:
    def test_upsert_and_list(self):
        upsert_milestone("cmmc", "poam_closeout", "2026-08-01", "CMMC POA&M closeout due",
                         details="180-day clock", link="poam", client_id="client-a")
        rows = list_milestones("2026-08-15")
        assert len(rows) == 1
        row = rows[0]
        assert row["milestone_type"] == "poam_closeout"
        assert row["framework_id"] == "cmmc"
        assert row["client_id"] == "client-a"

    def test_upsert_replaces_same_type(self):
        upsert_milestone("cmmc", "reassessment", "2028-01-01", "old", client_id="c1")
        upsert_milestone("cmmc", "reassessment", "2028-06-01", "new", client_id="c1")
        rows = list_milestones("2030-01-01")
        assert len(rows) == 1
        assert rows[0]["title"] == "new"
        assert rows[0]["due_date"] == "2028-06-01"

    def test_list_respects_due_window(self):
        upsert_milestone("cmmc", "affirmation", "2027-01-01", "annual", client_id="c1")
        assert list_milestones("2026-12-31") == []
        assert len(list_milestones("2027-01-01")) == 1

    def test_clear_milestones(self):
        upsert_milestone("cmmc", "poam_closeout", "2026-08-01", "closeout", client_id="c1")
        clear_milestones("cmmc", "c1")
        assert list_milestones("2026-12-31") == []

    def test_per_client_isolation(self):
        upsert_milestone("cmmc", "reassessment", "2028-01-01", "a", client_id="client-a")
        upsert_milestone("cmmc", "reassessment", "2028-02-01", "b", client_id="client-b")
        rows = list_milestones("2028-12-31")
        assert {r["client_id"] for r in rows} == {"client-a", "client-b"}


class TestFrameworkMilestones:
    def test_soc2_sync_writes_report_target(self):
        from compliance_calendar.framework_milestones import sync_soc2_milestones

        ws = {
            "client_id": "c-soc2",
            "audit_periods": [{"id": "p1", "name": "H1", "frozen": True, "end_date": "2026-06-30"}],
            "soc2_engagement": {},
        }
        sync_soc2_milestones(ws)
        rows = list_milestones("2030-01-01")
        types = {(r["framework_id"], r["milestone_type"]) for r in rows}
        assert ("soc2", "period_frozen") in types
        assert ("soc2", "report_target") in types

    def test_iso_sync_management_review(self):
        from compliance_calendar.framework_milestones import sync_iso_milestones

        sync_iso_milestones({}, "iso27001")
        rows = [r for r in list_milestones("2030-01-01") if r["framework_id"] == "iso27001"]
        assert rows == []  # no review record → no milestone, no crash

    def test_aigov_sync_fria_review(self):
        from compliance_calendar.framework_milestones import sync_aigov_milestones

        sync_aigov_milestones({"id": "sys-1", "name": "Classifier", "review_date": "2026-08-07"})
        rows = [r for r in list_milestones("2030-01-01") if r["framework_id"] == "aigov"]
        assert any(r["milestone_type"] == "fria_review" and r["due_date"] == "2027-08-07" for r in rows)
