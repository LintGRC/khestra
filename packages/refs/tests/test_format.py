"""Tests for the canonical framework-ref renderer (packages/refs/format.py)."""

import sys
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
if str(PACKAGES) not in sys.path:
    sys.path.insert(0, str(PACKAGES))

from refs.format import display_clause, render_control_ref  # noqa: E402


class TestDisplayClause:
    def test_eu_art_clause(self):
        assert display_clause("EU AI Act", "Art. 73") == "EU AI Act Art. 73"

    def test_eu_multi_art(self):
        assert display_clause("EU AI Act", "Art. 11, 18") == "EU AI Act Art. 11, 18"

    def test_iso_clause(self):
        assert display_clause("ISO 42001", "10.1, 10.2") == "ISO 42001 10.1, 10.2"

    def test_iso_annex_clause(self):
        assert display_clause("ISO 42001", "A.6") == "ISO 42001 Annex A.6"

    def test_iso27k_clause(self):
        assert display_clause("ISO 27001", "9.2, 9.3") == "ISO 27001 9.2, 9.3"

    def test_iso27k_annex_clause(self):
        assert display_clause("ISO 27001", "A.6") == "ISO 27001 Annex A.6"

    def test_iso27k_mixed(self):
        # single-level Annex refs wrap ("Annex A.6"); deeper A.x.y pass through,
        # matching the ISO 42001 renderer's behaviour.
        assert display_clause("ISO 27001", "6.1, A.6") == "ISO 27001 6.1, Annex A.6"
        assert display_clause("ISO 27001", "A.5.1") == "ISO 27001 A.5.1"

    def test_iso_annex_mixed(self):
        assert display_clause("ISO 42001", "8.1, A.6") == "ISO 42001 8.1, Annex A.6"

    def test_nist_clause(self):
        assert display_clause("NIST AI RMF", "GOVERN 1.1") == "NIST AI RMF GOVERN 1.1"

    def test_already_labeled_passes_through(self):
        assert display_clause("EU AI Act", "EU AI Act Art. 73") == "EU AI Act Art. 73"

    def test_empty(self):
        assert display_clause("ISO 42001", "") == ""
        assert display_clause("ISO 42001", "  ") == ""


class TestRenderControlRef:
    def test_eu_id(self):
        assert render_control_ref("EU-73") == "EU AI Act Art. 73"

    def test_nist_id(self):
        assert render_control_ref("NIST-GOVERN-1") == "NIST AI RMF GOVERN 1"

    def test_iso_clause_id(self):
        assert render_control_ref("ISO-4.1") == "ISO 42001 Clause 4.1"

    def test_iso_annex_id(self):
        assert render_control_ref("ISO-A.2") == "ISO 42001 Annex A.2"

    def test_iso27k_clause_id(self):
        assert render_control_ref("ISO27K-6.1.2") == "ISO 27001 6.1.2"
        assert render_control_ref("ISO27K-9.3.3") == "ISO 27001 9.3.3"

    def test_iso27k_annex_id(self):
        assert render_control_ref("ISO27K-A.5.1") == "ISO 27001 Annex A.5.1"

    def test_cmmc_id(self):
        assert render_control_ref("AC.L2-3.1.1") == "CMMC AC.L2-3.1.1"

    def test_owasp_id(self):
        assert render_control_ref("OWASP-1") == "OWASP ASI01"
        assert render_control_ref("OWASP-10") == "OWASP ASI10"

    def test_owasp_llm_id(self):
        assert render_control_ref("OWASP-LLM-1") == "OWASP LLM01:2025"
        assert render_control_ref("OWASP-LLM-10") == "OWASP LLM10:2025"

    def test_unknown_passthrough(self):
        assert render_control_ref("FOO.1") == "FOO.1"
