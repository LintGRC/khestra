"""Unit tests for the CMMC assessment status lifecycle (32 CFR 170.16-17, 170.22).

Run from repo root:
    apps/cmmc/.venv/bin/python -m pytest apps/cmmc/tests/test_assessment_status.py -q
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from assessment_status import (
    apply_assessment_status,
    build_assessment_status,
    complete_closeout,
    merge_assessment,
)


def _ws(status="", assessment_type="", status_date="", gaps=0):
    answers = {}
    scoped = []
    if gaps:
        for i in range(gaps):
            cid = f"AC.L2-3.1.{10 + i}"
            answers[cid] = {"status": "NOT MET"}
            scoped.append(cid)
    return {
        "client_id": "test-client",
        "answers": answers,
        "scoped_controls": scoped,
        "cmmc_assessment": {
            "assessment_type": assessment_type,
            "status": status,
            "status_date": status_date,
            "affirming_official": "Jane Doe, VP Security",
            "affirmed_at": "",
        },
    }


class TestMergeAssessment:
    def test_defaults(self):
        out = merge_assessment(None)
        assert out["assessment_type"] == ""
        assert out["status"] == ""
        assert out["affirming_official"] == ""

    def test_normalizes_legacy(self):
        out = merge_assessment({"status": "final", "bogus": 1})
        assert out["status"] == "final"
        assert "bogus" not in out


class TestBuildAssessmentStatus:
    def test_no_status(self):
        out = build_assessment_status(_ws())
        assert out["status"] == ""
        assert out["closeout_due"] == ""
        assert out["reassessment_due"] == ""

    def test_conditional_clocks(self):
        today = date.today()
        out = build_assessment_status(_ws("conditional", "level2_self", today.isoformat(), gaps=2))
        assert out["closeout_due"] == (today + timedelta(days=180)).isoformat()
        assert out["closeout_days_left"] == 180
        assert out["reassessment_due"] == (today + timedelta(days=365 * 3)).isoformat()
        assert out["affirmation_due"] == (today + timedelta(days=365)).isoformat()
        assert out["closeout_expired"] is False
        assert out["gap_count"] == 2

    def test_closeout_expired(self):
        past = (date.today() - timedelta(days=200)).isoformat()
        out = build_assessment_status(_ws("conditional", "level2_self", past))
        assert out["closeout_expired"] is True

    def test_final_clocks(self):
        today = date.today()
        out = build_assessment_status(_ws("final", "level2_c3pao", today.isoformat()))
        assert out["closeout_due"] == ""
        assert out["reassessment_days_left"] == 365 * 3


class TestApplyAssessmentStatus:
    def test_requires_type_and_date(self):
        with pytest.raises(ValueError, match="Assessment type is required"):
            apply_assessment_status(_ws(), assessment_type="", status="final", status_date="2026-01-01")
        with pytest.raises(ValueError, match="Status Date is required"):
            apply_assessment_status(_ws(), assessment_type="level2_self", status="final", status_date="")

    def test_rejects_unknown_values(self):
        with pytest.raises(ValueError, match="Unknown assessment type"):
            apply_assessment_status(_ws(), assessment_type="level9", status="final", status_date="2026-01-01")
        with pytest.raises(ValueError, match="Unknown status"):
            apply_assessment_status(_ws(), assessment_type="level2_self", status="partial", status_date="2026-01-01")

    def test_final_requires_no_gaps(self):
        with pytest.raises(ValueError, match="Final status requires all 2 NOT MET"):
            apply_assessment_status(
                _ws(gaps=2), assessment_type="level2_self", status="final", status_date="2026-01-01"
            )

    def test_final_ok_when_clean(self):
        out = apply_assessment_status(
            _ws(), assessment_type="level2_self", status="final", status_date="2026-01-01"
        )
        assert out["status"] == "final"
        assert out["assessment_type_label"] == "Level 2 (Self)"

    def test_conditional_requires_eligibility(self):
        ws = _ws(gaps=0)
        ws["scoped_controls"] = ["SC.L2-3.13.11"]
        ws["answers"]["SC.L2-3.13.11"] = {"status": "NOT MET"}
        with pytest.raises(ValueError, match="Conditional status not available"):
            apply_assessment_status(
                ws, assessment_type="level2_self", status="conditional", status_date="2026-01-01"
            )

    def test_clears_status(self):
        out = apply_assessment_status(_ws(), assessment_type="", status="", status_date="")
        assert out["status"] == ""


class TestCompleteCloseout:
    def test_requires_conditional(self):
        with pytest.raises(ValueError, match="only available for Conditional"):
            complete_closeout(_ws(status="final", assessment_type="level2_self", status_date="2026-01-01"))

    def test_blocked_with_open_gaps(self):
        with pytest.raises(ValueError, match="2 still open"):
            complete_closeout(_ws(status="conditional", assessment_type="level2_self", status_date="2026-01-01", gaps=2))

    def test_promotes_to_final(self):
        ws = _ws(status="conditional", assessment_type="level2_self", status_date="2026-01-01")
        out = complete_closeout(ws)
        assert out["status"] == "final"
        assert out["gap_count"] == 0
        assert ws["cmmc_assessment"]["affirmed_at"]
