"""Tests for CMMC Phase 4: scope record (§170.19), contract flowdown (§170.23),
and the Level 1 track (§170.15/170.22).

Run from repo root:
    apps/cmmc/.venv/bin/python -m pytest apps/cmmc/tests/test_cmmc_phase4.py -q
"""

from __future__ import annotations

import pytest

from cmmc_scope import apply_scope, merge_scope
from contract_tracking import add_contract, contracts_with_status, delete_contract, update_contract
from level1 import (
    L1_CONTROLS,
    apply_l1_status,
    build_l1_entry_text,
    build_l1_status,
    save_l1_assessment,
)


def _ws(assessment_type=""):
    return {
        "client_id": "test",
        "org_profile": {"org_name": "Test Org", "cage_code": "CAGE1", "uei": "UEI1"},
        "cmmc_assessment": {"assessment_type": assessment_type, "status": "final", "status_date": "2026-08-01"},
        "cmmc_scope": {},
        "contracts": [],
        "answers_l1": {},
        "l1_assessment": {},
    }


class TestScopeRecord:
    def test_defaults(self):
        assert merge_scope(None)["esp"] == ""

    def test_apply_scope_round_trip(self):
        ws = _ws()
        scope = apply_scope(ws, {"esp": "no", "facilities": "Austin TX", "scope_statement": "CUI enclave"})
        assert scope["esp"] == "no"
        assert ws["cmmc_scope"]["facilities"] == "Austin TX"

    def test_esp_requires_name(self):
        ws = _ws()
        with pytest.raises(ValueError, match="ESP name is required"):
            apply_scope(ws, {"esp": "yes", "esp_name": ""})

    def test_esp_with_name_ok(self):
        ws = _ws()
        scope = apply_scope(ws, {"esp": "yes", "esp_name": "CloudCo LLC"})
        assert scope["esp_name"] == "CloudCo LLC"


class TestContractFlowdown:
    def test_add_and_list(self):
        ws = _ws()
        c = add_contract(ws, {"name": "DoD Prime", "clause": "252.204-7021", "required_status": "level2_self"})
        assert c["id"]
        assert len(ws["contracts"]) == 1

    def test_add_requires_name(self):
        ws = _ws()
        with pytest.raises(ValueError, match="name is required"):
            add_contract(ws, {"name": ""})

    def test_add_rejects_bad_clause(self):
        ws = _ws()
        with pytest.raises(ValueError, match="Clause must be"):
            add_contract(ws, {"name": "X", "clause": "252.204-9999"})

    def test_update_and_delete(self):
        ws = _ws()
        c = add_contract(ws, {"name": "DoD Prime", "clause": "252.204-7021", "required_status": "level2_self"})
        updated = update_contract(ws, c["id"], {"required_status": "level2_c3pao"})
        assert updated["required_status"] == "level2_c3pao"
        assert delete_contract(ws, c["id"]) is True
        assert delete_contract(ws, c["id"]) is False

    def test_mismatch_flag(self):
        ws = _ws(assessment_type="level2_self")
        add_contract(ws, {"name": "L2 contract", "clause": "252.204-7021", "required_status": "level2_self"})
        add_contract(ws, {"name": "C3PAO contract", "clause": "252.204-7021", "required_status": "level2_c3pao"})
        rows = contracts_with_status(ws)
        by_name = {r["name"]: r for r in rows}
        assert by_name["L2 contract"]["mismatch"] is False
        assert by_name["C3PAO contract"]["mismatch"] is True
        assert by_name["C3PAO contract"]["held_status"] == "Level 2 (Self)"


class TestLevel1Track:
    def test_catalog_has_15(self):
        assert len(L1_CONTROLS) == 15

    def test_status_scoring(self):
        ws = _ws()
        apply_l1_status(ws, "AC.L1-b.1.i", "MET")
        apply_l1_status(ws, "IA.L1-b.1.v", "MET")
        status = build_l1_status(ws)
        assert status["score"] == 2
        assert status["total"] == 15
        assert status["all_met"] is False

    def test_rejects_unknown_practice(self):
        ws = _ws()
        with pytest.raises(ValueError, match="Unknown Level 1 practice"):
            apply_l1_status(ws, "AC.L2-3.1.1", "MET")

    def test_rejects_bad_status(self):
        ws = _ws()
        with pytest.raises(ValueError, match="MET or NOT MET"):
            apply_l1_status(ws, "AC.L1-b.1.i", "PARTIALLY MET")

    def test_all_met(self):
        ws = _ws()
        for c in L1_CONTROLS:
            apply_l1_status(ws, c["id"], "MET")
        assert build_l1_status(ws)["all_met"] is True

    def test_entry_text(self):
        ws = _ws()
        apply_l1_status(ws, "AC.L1-b.1.i", "MET")
        save_l1_assessment(ws, {"status_date": "2026-08-07", "affirming_official": "Jane Doe"})
        text = build_l1_entry_text(ws, ws["org_profile"])
        assert "CMMC LEVEL 1 (SELF)" in text
        assert "Level 1 (Self)" in text
        assert "1 of 15 safeguards MET" in text
        assert "Jane Doe" in text
