"""Tests for the shared control_tests store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from datetime import date, timedelta

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from control_tests.store import (
    init_store,
    list_tests,
    get_test,
    create_test,
    update_test,
    delete_test,
    list_runs,
    add_run,
    next_due,
    FREQUENCY_MONTHS,
)


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"ctrl_tests_{uid}.db"
    os.environ["CONTROL_TESTS_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("CONTROL_TESTS_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


class TestTestCRUD:
    def test_create_test(self):
        t = create_test(title="Access Review", control_id="AC.L2-3.1.1", framework="CMMC")
        assert t["id"]
        assert t["title"] == "Access Review"
        assert t["active"] == 1

    def test_list_tests(self):
        create_test(title="A")
        create_test(title="B")
        assert len(list_tests()) == 2

    def test_get_test(self):
        t = create_test(title="Lookup")
        got = get_test(t["id"])
        assert got["title"] == "Lookup"

    def test_update_test(self):
        t = create_test(title="Old")
        updated = update_test(t["id"], {"title": "New"})
        assert updated["title"] == "New"

    def test_delete_test(self):
        t = create_test(title="Doomed")
        assert delete_test(t["id"]) is True
        assert get_test(t["id"]) is None

    def test_delete_cascades_runs(self):
        t = create_test(title="Cascade")
        add_run(t["id"])
        delete_test(t["id"])
        assert len(list_runs(t["id"])) == 0


class TestRuns:
    def test_add_run(self):
        t = create_test(title="Mod")
        r = add_run(t["id"], result="passed", run_by="alice")
        assert r["id"]
        assert r["result"] == "passed"

    def test_add_run_auto_date(self):
        t = create_test(title="AutoDate")
        r = add_run(t["id"])
        assert r["run_date"]  # auto-set to today

    def test_list_runs(self):
        t = create_test(title="Runs")
        add_run(t["id"], result="passed")
        add_run(t["id"], result="failed")
        runs = list_runs(t["id"])
        assert len(runs) == 2

    def test_rpo_rto_tracking(self):
        t = create_test(title="RPO", target_rpo_minutes=60, target_rto_minutes=240)
        r = add_run(t["id"], actual_rpo_minutes=55, actual_rto_minutes=200)
        assert r["actual_rpo_minutes"] == 55
        assert r["actual_rto_minutes"] == 200


class TestNextDue:
    def test_next_due_quarterly(self):
        t = create_test(title="Q", frequency="quarterly")
        result = next_due(t, last_run_date="2025-01-15")
        expected = date(2025, 1, 15) + timedelta(days=90)
        assert result == expected

    def test_next_due_monthly(self):
        t = create_test(title="M", frequency="monthly")
        result = next_due(t, last_run_date="2025-06-01")
        expected = date(2025, 6, 1) + timedelta(days=30)
        assert result == expected

    def test_next_due_no_date_uses_created(self):
        """When no last_run_date is provided, next_due falls back to created_at."""
        t = create_test(title="NoDate")
        result = next_due(t)
        # next_due uses created_at as fallback, so it returns a date (not None)
        assert result is not None


class TestFrequencyConstants:
    def test_frequency_months(self):
        assert FREQUENCY_MONTHS["monthly"] == 1
        assert FREQUENCY_MONTHS["quarterly"] == 3
        assert FREQUENCY_MONTHS["semi_annual"] == 6
        assert FREQUENCY_MONTHS["annual"] == 12
