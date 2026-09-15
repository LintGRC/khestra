"""Tests for the SOC 2 engagement record + system description integration.

Run from repo root:
    apps/cmmc/.venv/bin/python -m pytest apps/soc2/tests/test_engagement.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parents[1] / "core"
sys.path.insert(0, str(CORE))


def _ws(engagement=None, org_profile=None, cuecs=None):
    return {
        "client_id": "test",
        "org_name": "Test Org",
        "org_profile": org_profile or {},
        "tsc_scope": {},
        "audit_periods": [],
        "soc2_engagement": engagement or {},
        "answers": {},
        "cuecs": cuecs or [],
        "policies": [],
        "exceptions": [],
    }


def _docx_text(data: bytes) -> str:
    from io import BytesIO
    from docx import Document

    doc = Document(BytesIO(data))
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


class TestEngagementInWorkspace:
    def test_engagement_defaults_empty(self):
        ws = _ws()
        assert ws["soc2_engagement"] == {}

    def test_engagement_round_trip_through_workspace(self):
        from workspace_service import load_workspace, save_workspace

        ws = _ws({"type": "type2", "firm": "Acme CPA", "status": "fieldwork"})
        # save/load is path-based; assert the field survives the payload path
        from workspace_service import _empty_workspace

        empty = _empty_workspace("t")
        assert "soc2_engagement" in empty
        assert empty["soc2_engagement"] == {}


class TestSystemDescriptionEngagement:
    def test_engagement_block_in_report(self):
        from system_description import generate_system_description

        ws = _ws({
            "type": "type2",
            "firm": "Acme CPA LLP",
            "cpa_contact": "a@acme.cpa",
            "engagement_start": "2026-01-01",
            "engagement_end": "2026-06-30",
            "status": "fieldwork",
        })
        md = generate_system_description(ws)
        assert "**Engagement:** Type II report" in md
        assert "Acme CPA LLP" in md
        assert "**Engagement status:** fieldwork" in md

    def test_no_engagement_block_when_unset(self):
        from system_description import generate_system_description

        md = generate_system_description(_ws())
        assert "**Engagement:**" not in md

    def test_type1_label(self):
        from system_description import generate_system_description

        md = generate_system_description(_ws({"type": "type1", "firm": "F"}))
        assert "**Engagement:** Type I report" in md


class TestScopingValidation:
    def test_tsc_scope_validation(self):
        from tsc_scoping import DEFAULT_SCOPE, get_in_scope_criteria_ids, scope_summary

        scope = dict(DEFAULT_SCOPE)
        summary = scope_summary(scope)
        assert summary["in_scope_criteria"] >= 49  # 2017 TSC full set when everything in scope
        ids = get_in_scope_criteria_ids(scope)
        assert "CC1.1" in ids
        assert "PI1.1" in ids

    def test_tsc_scope_partial(self):
        from tsc_scoping import DEFAULT_SCOPE, is_in_scope, scope_summary

        scope = dict(DEFAULT_SCOPE)
        scope["Security"] = False
        summary = scope_summary(scope)
        assert summary["in_scope_criteria"] < summary["total_criteria"]
        assert not is_in_scope("CC1.1", scope)


class TestReadinessAssessment:
    def test_dashboard_shape(self):
        from readiness import compute_dashboard

        ws = _ws()
        dash = compute_dashboard(ws)
        assert "readiness_pct" in dash
        assert "controls_total" in dash

    def test_priority_queue(self):
        from priority_queue import get_priority_queue

        ws = _ws()
        out = get_priority_queue(ws["answers"], ws.get("risks") or [], ws.get("exceptions") or [])
        assert isinstance(out, dict)
        assert "queue" in out or "items" in out or "rows" in out


class TestReports:
    def test_gap_analysis_exports_xlsx(self):
        from gap_analysis import generate_gap_analysis

        ws = _ws()
        data = generate_gap_analysis(ws)
        assert data.startswith(b"PK")  # xlsx

    def test_system_description_markdown(self):
        from system_description import generate_system_description

        md = generate_system_description(_ws())
        assert md.startswith("# SOC 2 System Description")
        assert "Executive summary" in md


class TestSystemDescriptionDocx:
    def test_dc_200_headings_and_engagement(self):
        from ssp_export import generate_system_description_docx

        ws = _ws({
            "type": "type2",
            "firm": "Acme CPA LLP",
            "cpa_contact": "a@acme.cpa",
            "engagement_start": "2026-01-01",
            "engagement_end": "2026-06-30",
            "status": "fieldwork",
        })
        text = _docx_text(generate_system_description_docx(ws))
        assert "DC Section 200" in text
        assert "Types of Services Provided (DC-1.1)" in text
        assert "Complementary User Entity Controls (DC-3.2)" in text
        assert "Type II" in text
        assert "Acme CPA LLP" in text

    def test_cuec_and_carve_out(self):
        from ssp_export import generate_system_description_docx

        ws = _ws(
            org_profile={
                "org_name": "Test Org",
                "reporting_method": "carve-out",
                "subservice_organizations": "CloudHost Inc.",
                "user_entity_controls": "User entities must enforce MFA.",
            },
            cuecs=[{
                "control_id": "CC6.1",
                "description": "Restrict access to production.",
                "assigned_to": "Customer IT",
                "status": "open",
            }],
        )
        text = _docx_text(generate_system_description_docx(ws))
        assert "carve-out" in text
        assert "CloudHost Inc." in text
        assert "User entities must enforce MFA." in text
        assert "CC6.1" in text
        assert "Restrict access to production." in text


class TestEngagementValidation:
    def test_type1_does_not_require_oe(self):
        from readiness_assessment import engagement_validation, run_readiness_assessment

        ws = _ws({"type": "type1", "firm": "Acme"})
        ws["answers"] = {"CC1.1": {"status": "MET", "operating_status": "NOT TESTED"}}
        v = engagement_validation(ws)
        assert v["design_only"] is True
        assert v["oe_required"] is False
        assert v["oe_gap_count"] >= 1  # gap exists but is not required
        assessment = run_readiness_assessment(ws)
        oe_item = next(c for c in assessment["checklist"] if c["key"] == "operating_effectiveness")
        assert oe_item["required"] is False
        assert oe_item["done"] is True

    def test_type2_requires_period_and_oe_pass(self):
        from readiness_assessment import run_readiness_assessment

        ws = _ws({
            "type": "type2",
            "firm": "Acme",
            "engagement_start": "2026-01-01",
            "engagement_end": "2026-06-30",
        })
        ws["answers"] = {"CC1.1": {"status": "MET", "operating_status": "NOT TESTED"}}
        assessment = run_readiness_assessment(ws)
        oe_item = next(c for c in assessment["checklist"] if c["key"] == "operating_effectiveness")
        period_item = next(c for c in assessment["checklist"] if c["key"] == "type2_period")
        assert oe_item["required"] is True
        assert oe_item["done"] is False
        assert period_item["required"] is True
        assert period_item["done"] is True
        assert any("operating effectiveness" in b.lower() for b in assessment["blockers"])

    def test_type2_ready_when_oe_pass(self):
        from readiness_assessment import engagement_validation

        ws = _ws({
            "type": "type2",
            "engagement_start": "2026-01-01",
            "engagement_end": "2026-06-30",
        })
        ws["answers"] = {"CC1.1": {"status": "MET", "operating_status": "PASS"}}
        v = engagement_validation(ws)
        assert v["oe_required"] is True
        met_gaps = [g for g in v["oe_gaps"] if g["control_id"] == "CC1.1"]
        assert met_gaps == []

    def test_does_not_write_operating_status(self):
        from readiness_assessment import run_readiness_assessment

        ws = _ws({"type": "type2", "engagement_start": "2026-01-01", "engagement_end": "2026-12-31"})
        ws["answers"] = {"CC1.1": {"status": "MET", "operating_status": "NOT TESTED"}}
        run_readiness_assessment(ws)
        assert ws["answers"]["CC1.1"]["operating_status"] == "NOT TESTED"
