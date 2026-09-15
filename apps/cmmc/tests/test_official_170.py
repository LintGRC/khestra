"""Parity tests: apps/cmmc/core/official_170.py lock vs the 32 CFR 170 implementation.

The lock module (official_170.py) extracts the six sections of 32 CFR Part 170
that the CMMC program-mechanics code implements. These tests assert the app's
constants, hard-block lists and flowdown rules match the regulatory text —
so invented wording or a drifted constant cannot merge silently.

Run from repo root:
    apps/cmmc/.venv/bin/python -m pytest apps/cmmc/tests/test_official_170.py -q
"""

from __future__ import annotations

import re

import pytest

from assessment_status import AFFIRMATION_YEARS, REASSESSMENT_YEARS
from cmmc_scope import EMPTY_SCOPE
from contract_tracking import REQUIRED_STATUSES, STATUS_LABELS
from level1 import L1_CONTROLS, build_l1_status
from official_170 import (
    ARTIFACT_RETENTION_YEARS,
    CONDITIONAL_SCORE,
    FIPS_DEDUCTION_NONE,
    FIPS_DEDUCTION_PARTIAL,
    FLOWDOWN_RULES,
    FLOWDOWN_STATUS_KEYS,
    LEVEL1_POAM_ALLOWED,
    LEVEL1_SCOPE_TRIGGER,
    LEVEL2_MAX_SCORE,
    LEVEL2_SCOPE_CATEGORIES,
    MFA_DEDUCTION_NONE,
    MFA_DEDUCTION_PARTIAL,
    POAM_CLOSEOUT_DAYS,
    POAM_FORBIDDEN_LEVEL2,
    POAM_FORBIDDEN_LEVEL3,
    REASSESSMENT_YEARS as LOCK_REASSESSMENT_YEARS,
    SECTION_TEXT,
    SSP_REQUIREMENT,
)
from poam_eligibility import (
    FIPS_POAM_EXCEPTION,
    POAM_CLOSEOUT_DAYS as IMPL_POAM_CLOSEOUT_DAYS,
    poam_eligibility,
)
from sprs_engine import BASE_SCORE, VARIABLE_WEIGHT_CONTROLS, variable_deduction


def _all_met_answers(scoped, overrides=None):
    answers = {c: {"status": "MET"} for c in scoped}
    for cid, ans in (overrides or {}).items():
        answers[cid] = ans
    return answers


# ── Lock self-integrity: verbatim sections present ───────────────────────────


def test_lock_has_all_locked_sections():
    assert set(SECTION_TEXT) == {
        "170.15", "170.16", "170.17", "170.18", "170.19",
        "170.21", "170.22", "170.23", "170.24",
    }


def test_lock_sections_open_with_official_titles():
    assert SECTION_TEXT["170.15"].startswith("§170.15 CMMC Level 1 self-assessment")
    assert SECTION_TEXT["170.21"].startswith("§170.21 Plan of Action and Milestones")
    assert SECTION_TEXT["170.23"].startswith("§170.23 Application to subcontractors")


def test_lock_contains_regulatory_key_sentences():
    # 170.16(a)(1) reassessment cadence
    assert "every three years" in SECTION_TEXT["170.16"]
    assert "within 180 days" in SECTION_TEXT["170.16"]
    # 170.21 conditional ratio
    assert "greater than or equal to 0.8" in SECTION_TEXT["170.21"]
    # 170.22 annual affirmation
    assert "annually thereafter" in SECTION_TEXT["170.22"]
    # 170.23 flowdown statuses
    assert "Level 1 (Self)" in SECTION_TEXT["170.23"]
    assert "Level 2 (C3PAO)" in SECTION_TEXT["170.23"]
    # 170.15 Level 1 has no POA&M
    assert "No POA&Ms are permitted" in SECTION_TEXT["170.15"]
    # 170.17 Level 2 certification assessment
    assert "Level 2 certification assessment and affirmation requirements" in SECTION_TEXT["170.17"]
    assert "Conditional Level 2 (C3PAO)" in SECTION_TEXT["170.17"]
    assert "Final Level 2 (C3PAO)" in SECTION_TEXT["170.17"]
    # 170.18 Level 3 certification assessment
    assert "Level 3 certification assessment and affirmation requirements" in SECTION_TEXT["170.18"]
    assert "Conditional Level 3 (DIBCAC)" in SECTION_TEXT["170.18"]
    assert "Final Level 3 (DIBCAC)" in SECTION_TEXT["170.18"]


# ── Constants: implementation matches the regulation ────────────────────────


def test_reassessment_years_match():
    assert REASSESSMENT_YEARS == LOCK_REASSESSMENT_YEARS == 3


def test_poam_closeout_days_match():
    assert IMPL_POAM_CLOSEOUT_DAYS == POAM_CLOSEOUT_DAYS == 180


def test_affirmation_interval_match():
    assert AFFIRMATION_YEARS == 1


def test_conditional_score_is_88():
    assert CONDITIONAL_SCORE == 88  # 0.8 x 110


def test_fips_exception_control_matches():
    assert FIPS_POAM_EXCEPTION == "SC.L2-3.13.11"
    # regulation text uses en-dash in the control id: SC.L2–3.13.11
    assert "SC.L2\u20133.13.11" in SECTION_TEXT["170.21"]


def test_artifact_retention_years():
    assert ARTIFACT_RETENTION_YEARS == 6


def test_level1_has_no_poam():
    assert LEVEL1_POAM_ALLOWED is False


# ── POA&M forbidden lists (170.21(a)(2)(iii) / (a)(3)(ii)) ───────────────────


def test_forbidden_level2_list_is_exactly_six():
    assert POAM_FORBIDDEN_LEVEL2 == {
        "AC.L2-3.1.20",
        "AC.L2-3.1.22",
        "CA.L2-3.12.4",
        "PE.L2-3.10.3",
        "PE.L2-3.10.4",
        "PE.L2-3.10.5",
    }
    assert len(POAM_FORBIDDEN_LEVEL2) == 6


def test_forbidden_level3_list_is_exactly_seven():
    assert len(POAM_FORBIDDEN_LEVEL3) == 7


def test_each_forbidden_level2_control_is_named_in_the_regulation():
    # every control in the lock must appear verbatim in §170.21 (en-dash form)
    body = SECTION_TEXT["170.21"]
    for cid in POAM_FORBIDDEN_LEVEL2:
        base = cid.split("-", 1)[1]
        assert base in body.replace("\u2013", "-"), cid


@pytest.mark.parametrize("cid", sorted(POAM_FORBIDDEN_LEVEL2))
def test_forbidden_level2_gap_blocks_conditional_status(cid):
    # Behavioural: a gap on any §170.21(a)(2)(iii) control must NEVER be
    # POA&M-eligible, regardless of its (low) point value.
    scoped = [
        "AC.L2-3.1.1", "AC.L2-3.1.20", "AC.L2-3.1.22", "CA.L2-3.12.4",
        "PE.L2-3.10.3", "PE.L2-3.10.4", "PE.L2-3.10.5",
    ]
    answers = _all_met_answers(scoped, {cid: {"status": "NOT MET"}})
    e = poam_eligibility(answers, scoped)
    assert e["eligible"] is False
    assert cid in e["blocking_ids"]
    assert cid not in e["eligible_ids"]


def test_one_point_gap_still_eligible():
    # sanity: a genuinely POA&M-able 1-point gap is unaffected by the hard-block
    scoped = ["AC.L2-3.1.1", "AC.L2-3.1.3"]
    answers = _all_met_answers(scoped, {"AC.L2-3.1.3": {"status": "NOT MET"}})
    e = poam_eligibility(answers, scoped)
    assert e["eligible"] is True
    assert "AC.L2-3.1.3" in e["eligible_ids"]


# ── Flowdown (170.23) ────────────────────────────────────────────────────────


def test_flowdown_rules_match_regulation_statuses():
    assert FLOWDOWN_RULES == {
        "fci_only": "level1_self",
        "cui_default": "level2_self",
        "cui_prime_level2_c3pao": "level2_c3pao",
        "cui_prime_level3_dibac": "level2_c3pao",
    }


def test_contract_tracking_statuses_aligned_with_flowdown():
    # contract_tracking.py REQUIRED_STATUSES / STATUS_LABELS must cover the
    # exact status keys the regulation flows down to subcontractors.
    assert set(REQUIRED_STATUSES) - {""} == FLOWDOWN_STATUS_KEYS
    assert set(STATUS_LABELS) == FLOWDOWN_STATUS_KEYS
    assert FLOWDOWN_RULES["cui_prime_level3_dibac"] == "level2_c3pao"


# ── Scope (170.19) ───────────────────────────────────────────────────────────


def test_level1_scope_trigger_phrasing_matches_regulation():
    assert "process, store, or transmit FCI" in LEVEL1_SCOPE_TRIGGER
    assert LEVEL1_SCOPE_TRIGGER in SECTION_TEXT["170.19"]


def test_level2_scope_categories_from_table3():
    # §170.19(c)(1) Table 3 asset categories — the in-scope set.
    assert LEVEL2_SCOPE_CATEGORIES == {
        "CUI Assets",
        "Security Protection Assets",
        "Contractor Risk Managed Assets",
        "Specialized Assets",
    }
    for cat in LEVEL2_SCOPE_CATEGORIES:
        assert cat in SECTION_TEXT["170.19"], cat


def test_scope_record_has_esp_fields_per_17019():
    # cmmc_scope.py persists ESP + facility fields used for the 170.19(c)
    # External Service Provider scoping narrative.
    assert "esp" in EMPTY_SCOPE
    assert "esp_name" in EMPTY_SCOPE
    assert "scope_statement" in EMPTY_SCOPE


# ── Level 1 (170.15 / 170.22) ────────────────────────────────────────────────


def test_level1_controls_count_is_15():
    # §170.15(c)(1)(ii) Table 2 maps the 15 FAR 52.204-21 safeguards.
    assert len(L1_CONTROLS) == 15


def test_level1_has_no_poam_in_line_with_17021():
    ws = {
        "answers_l1": {c["id"]: {"status": "NOT MET"} for c in L1_CONTROLS},
        "l1_assessment": {},
    }
    status = build_l1_status(ws)
    # Level 1 is scored MET/NOT MET with no POA&M; a NOT MET is a gap, not a
    # POA&M item — consistent with §170.21(a)(1).
    assert status["total"] == 15
    assert status["all_met"] is False


# ── Scoring method (170.24) parity with sprs_engine / annex_weights ──────────


def test_level2_max_score_matches_sprs_base():
    assert LEVEL2_MAX_SCORE == BASE_SCORE == 110


def test_mfa_fips_variable_deductions_match_17024():
    assert variable_deduction("IA.L2-3.5.3", "PARTIALLY MET") == MFA_DEDUCTION_PARTIAL == 3
    assert variable_deduction("SC.L2-3.13.11", "PARTIALLY MET") == FIPS_DEDUCTION_PARTIAL == 3
    assert variable_deduction("IA.L2-3.5.3", "NOT MET") == MFA_DEDUCTION_NONE == 5
    assert variable_deduction("SC.L2-3.13.11", "NOT MET") == FIPS_DEDUCTION_NONE == 5


def test_variable_weight_controls_match_17024_exceptions():
    # §170.24(c)(2)(4): MFA IOA.L2-3.5.3 and FIPS SC.L2-3.13.11 are the only
    # requirements with adjustable partial deductions.
    assert set(VARIABLE_WEIGHT_CONTROLS) == {"IA.L2-3.5.3", "SC.L2-3.13.11"}


def test_ssp_requirement_is_non_scorable():
    # §170.24(c)(2)(5): an up-to-date SSP (CA.L2-3.12.4) is a program precondition,
    # not a scored requirement — matching annex_weights.NON_SCORABLE.
    assert SSP_REQUIREMENT == "CA.L2-3.12.4"
    from annex_weights import NON_SCORABLE
    assert "3.12.4" in NON_SCORABLE


def test_scoring_method_text_present():
    body = SECTION_TEXT["170.24"]
    assert "CMMC Level 2 Scoring Methodology" in body
    assert "five (5) points" in body
    assert "three (3) points" in body
    assert "Not Applicable" in body


# ── Lock-text integrity (guards against extraction artifacts) ────────────────


def test_17024_text_ends_at_scoring_met_finding():
    # §170.24 ends with the Level 3 scoring sentence; anything after that in the
    # PDF (Appendix A guidance list, Part 173) is NOT part of the section.
    body = SECTION_TEXT["170.24"]
    assert body.endswith("assessed as MET.")
    assert "APPENDIX A TO PART 170" not in body
    assert "PART 173" not in body
    assert "VerDate" not in body
    assert "Guidance documents" not in body


def test_no_page_number_artifacts_in_locked_text():
    # PDF page-footers/running-heads (835/836/837 page numbers, VerDate stamps)
    # must never leak into locked text.
    for k, text in SECTION_TEXT.items():
        assert "VerDate" not in text, k
        assert "jspears" not in text, k
        for num in (" 835 ", " 836 ", " 837"):
            assert num not in text, (k, num)


def test_no_hyphen_space_wrap_artifacts():
    # Extraction must rejoin hyphenated line wraps ("self-assess-\nment") without
    # leaving "self- assessment" artifacts.
    for k, text in SECTION_TEXT.items():
        assert not re.search(r"\w- \w", text), k


def test_no_double_spaces_in_locked_text():
    for k, text in SECTION_TEXT.items():
        assert "  " not in text, k


def test_17024_contains_scoring_table_and_deductions():
    body = SECTION_TEXT["170.24"]
    assert "TABLE 7 TO §170.24(c)(2)(ii)" in body
    assert "IA.L2-3.5.3" in body  # MFA deduction paragraph
    assert "SC.L2-3.13.11" in body  # FIPS deduction paragraph
