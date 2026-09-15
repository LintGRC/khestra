"""Tests for the shared effectiveness aggregation module."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))


class TestCollectEffectiveness:
    """Test collect_effectiveness with mocked upstream stores."""

    def test_returns_all_panels(self):
        from effectiveness.collect import collect_effectiveness

        with patch("effectiveness.collect._risks_panel", return_value={"available": False}), \
             patch("effectiveness.collect._findings_panel", return_value={"available": False}), \
             patch("effectiveness.collect._exceptions_panel", return_value={"available": False}), \
             patch("effectiveness.collect._maturity_panel", return_value={"available": False}):
            result = collect_effectiveness()
            assert "maturity_distribution" in result
            assert "findings_recurrence" in result
            assert "exception_trend" in result
            assert "decision_velocity" in result

    def test_framework_aliases_exact(self):
        from effectiveness.collect import _framework_variants

        assert "CMMC" in _framework_variants("CMMC")
        assert "SOC 2" in _framework_variants("SOC 2")
        assert "AI Gov" in _framework_variants("AI Gov")
        assert "ISO 27001" in _framework_variants("ISO 27001")

    def test_framework_aliases_extended(self):
        from effectiveness.collect import _framework_variants

        # "CMMC Rev 2" maps to CMMC
        assert "CMMC" in _framework_variants("CMMC Rev 2")
        # "AIGov" (no space) maps to AI Gov
        assert "AI Gov" in _framework_variants("AIGov")
        # "SOC2" (no space) maps to SOC 2
        assert "SOC 2" in _framework_variants("SOC2")

    def test_framework_aliases_passthrough(self):
        from effectiveness.collect import _framework_variants

        # Unknown aliases return the input as-is
        assert _framework_variants("ISO") == ["ISO"]
        assert _framework_variants("unknown") == ["unknown"]

    def test_maturity_levels(self):
        from effectiveness.collect import MATURITY_LEVELS

        assert len(MATURITY_LEVELS) == 5
        assert "Ad Hoc" in MATURITY_LEVELS
        assert "Optimized" in MATURITY_LEVELS

    def test_risks_panel_no_store(self):
        from effectiveness.collect import _risks_panel

        result = _risks_panel("")
        assert "available" in result

    def test_findings_panel_no_store(self):
        from effectiveness.collect import _findings_panel

        result = _findings_panel("", 12)
        assert "available" in result

    def test_exceptions_panel_no_store(self):
        from effectiveness.collect import _exceptions_panel

        result = _exceptions_panel("", 12)
        assert "available" in result

    def test_maturity_panel_no_store(self):
        from effectiveness.collect import _maturity_panel

        result = _maturity_panel("")
        assert "available" in result
