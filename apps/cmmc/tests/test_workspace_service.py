"""Verify workspace state fields are consistent across _empty_workspace, save, and load.

The bug pattern: adding a field to save_workspace / load_workspace without
adding it to _empty_workspace leads to KeyError on bracket access after save/load.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

APP = Path(__file__).resolve().parents[1]
CORE = APP / "core"

# Ensure core/ is on path (conftest may not run for direct test invocation)
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from workspace_service import _empty_workspace, load_workspace, save_workspace  # noqa: E402
# Fields that save_workspace includes in its write payload.
PAYLOAD_FIELDS = [
    "version",
    "org_name",
    "org_profile",
    "answers",
    "audit_log",
    "asset_scope",
    "current_role",
    "current_user_name",
    "sprs_history",
    "org_assets",
    "org_inventory",
    "live_asset_snapshots",
    "scope_confirmed",
    "last_export_at",
    "assessment_fingerprint_at_export",
    "env_scope",
    "msp_mode",
    "scoped_controls",  # conditional, but must be present in state
]

# Fields that _empty_workspace must include for save/load to work.
EMPTY_FIELDS = [
    "client_id",
    "version",
    "org_name",
    "org_profile",
    "answers",
    "audit_log",
    "asset_scope",
    "scoped_controls",
    "current_role",
    "current_user_name",
    "msp_mode",
    "sprs_history",
    "org_assets",
    "org_asset_bytes",
    "org_inventory",
    "live_asset_snapshots",
    "scope_confirmed",
    "last_export_at",
    "assessment_fingerprint_at_export",
    "env_scope",
    "restored_evidence",
]


def test_empty_workspace_has_all_required_fields():
    ws = _empty_workspace("test-client")
    for field in EMPTY_FIELDS:
        assert field in ws, f"Field '{field}' missing from _empty_workspace()"


def test_save_payload_fields_exist_in_state():
    """Every field save_workspace reads from state must exist in empty workspace or be handled with .get()."""
    ws = _empty_workspace("test-client")
    for field in PAYLOAD_FIELDS:
        if field == "scoped_controls":
            continue  # conditional, tested separately
        # Must exist in empty workspace or be accessed with .get() in save
        assert field in ws, f"Field '{field}' missing from _empty_workspace() but needed by save_workspace()"


def test_msp_mode_present():
    """Regression: msp_mode was missing from _empty_workspace."""
    ws = _empty_workspace("test-client")
    assert "msp_mode" in ws
    assert ws["msp_mode"] is False


def test_scoped_controls_present():
    """scoped_controls must exist so conditional save doesn't silently drop it."""
    ws = _empty_workspace("test-client")
    assert "scoped_controls" in ws


class TestWorkspaceRoundTrip:
    """Test save -> load round-trip with a temporary data directory."""

    def test_round_trip(self, tmp_path):
        """Save a workspace with known data, load it back, verify all fields match."""
        data_dir = tmp_path / "cmmc_data"
        data_dir.mkdir()

        # Patch DATA_DIR used by client_workspaces -> config
        import config  # noqa: E402

        with patch.object(config, "DATA_DIR", data_dir):
            # Create a workspace with all fields populated
            from workspace_service import _empty_workspace  # noqa: E402

            ws = _empty_workspace("round-trip-client")
            ws["org_name"] = "Test Corp"
            ws["msp_mode"] = True
            ws["scope_confirmed"] = True
            ws["current_user_name"] = "tester"
            ws["last_export_at"] = "2026-06-26T12:00:00Z"
            ws["sprs_history"] = [{"score": 88, "date": "2026-06-26"}]

            # Save
            save_workspace(ws)

            # Load
            loaded = load_workspace("round-trip-client")

            assert loaded["org_name"] == "Test Corp"
            assert loaded["msp_mode"] is True
            assert loaded["scope_confirmed"] is True
            assert loaded["current_user_name"] == "tester"
            assert loaded["last_export_at"] == "2026-06-26T12:00:00Z"
            assert len(loaded["sprs_history"]) == 1
            assert loaded["sprs_history"][0]["score"] == 88


def test_sprs_snapshot_records_real_readiness():
    """Snapshot bug fix: readiness was hardcoded 0; now records % controls met."""
    from workspace_service import _maybe_sprs_snapshot
    from controls import CMMC_FRAMEWORK

    scoped = list(CMMC_FRAMEWORK.keys())
    answers = {c: {"status": "MET"} for c in scoped}
    answers["AC.L2-3.1.1"] = {"status": "NOT MET"}
    answers["AC.L2-3.1.3"] = {"status": "NOT MET"}
    ws = {"answers": answers, "scoped_controls": scoped, "sprs_history": []}

    _maybe_sprs_snapshot(ws)
    snap = ws["sprs_history"][-1]
    assert snap["readiness"] > 0, "readiness must reflect actual % met"
    assert snap["controls_met"] == len(scoped) - 2
    assert snap["controls_total"] == len(scoped)
    assert snap["score"] < 110  # two gaps present
