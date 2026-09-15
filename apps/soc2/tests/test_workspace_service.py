"""Verify SOC2 workspace state fields are consistent across _empty_workspace, save, and load.

The bug pattern: adding a field to save_workspace / load_workspace without
adding it to _empty_workspace leads to KeyError on bracket access after save/load.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

APP = Path(__file__).resolve().parents[1]
CORE = APP / "core"

if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from workspace_service import _empty_workspace, load_workspace, save_workspace  # noqa: E402

# Fields that save_workspace includes in its write payload.
PAYLOAD_FIELDS = [
    "version",
    "org_name",
    "answers",
    "audit_log",
    "audit_periods",
    "evidence_requests",
    "exceptions",
    "risks",
    "policies",
    "policy_attestations",
    "findings",
    "current_role",
    "current_user_name",
    "is_demo",
    "demo_id",
]

# Fields that _empty_workspace must include for save/load to work.
EMPTY_FIELDS = [
    "client_id",
    "version",
    "org_name",
    "answers",
    "audit_log",
    "audit_periods",
    "evidence_requests",
    "exceptions",
    "risks",
    "policies",
    "policy_attestations",
    "findings",
    "current_role",
    "current_user_name",
    "is_demo",
    "demo_id",
    "restored_evidence",
]


def test_empty_workspace_has_all_required_fields():
    ws = _empty_workspace("test-client")
    for field in EMPTY_FIELDS:
        assert field in ws, f"Field '{field}' missing from _empty_workspace()"


def test_save_payload_fields_exist_in_state():
    ws = _empty_workspace("test-client")
    for field in PAYLOAD_FIELDS:
        assert field in ws, f"Field '{field}' missing from _empty_workspace() but needed by save_workspace()"


def test_exceptions_initialized_as_list():
    ws = _empty_workspace("test-client")
    assert isinstance(ws["exceptions"], list)


def test_risks_initialized_as_list():
    ws = _empty_workspace("test-client")
    assert isinstance(ws["risks"], list)


def test_policies_initialized_as_list():
    ws = _empty_workspace("test-client")
    assert isinstance(ws["policies"], list)


def test_findings_initialized_as_list():
    ws = _empty_workspace("test-client")
    assert isinstance(ws["findings"], list)


def test_audit_periods_initialized_as_list():
    ws = _empty_workspace("test-client")
    assert isinstance(ws["audit_periods"], list)


def test_workspace_not_locked_when_empty():
    from workspace_service import workspace_is_locked  # noqa: E402

    ws = _empty_workspace("test-client")
    assert workspace_is_locked(ws) is False


def test_workspace_locked_when_period_frozen():
    from workspace_service import workspace_is_locked  # noqa: E402

    ws = _empty_workspace("test-client")
    ws["audit_periods"] = [{"id": "p1", "name": "Q1", "frozen": True}]
    assert workspace_is_locked(ws) is True


class TestWorkspaceRoundTrip:
    """Test save -> load round-trip with a temporary data directory."""

    def test_round_trip(self, tmp_path):
        data_dir = tmp_path / "cmmc_data"
        data_dir.mkdir()

        import config  # noqa: E402

        with patch.object(config, "DATA_DIR", data_dir):
            from workspace_service import _empty_workspace, load_workspace, save_workspace  # noqa: E402

            ws = _empty_workspace("round-trip-client")
            ws["org_name"] = "Test Corp"
            ws["is_demo"] = True
            ws["current_user_name"] = "tester"
            ws["exceptions"] = [{"id": "e1", "control_id": "CC6.1", "description": "Legacy MFA gap", "risk_level": "high", "status": "open"}]
            ws["risks"] = [{"id": "r1", "title": "Test Risk", "inherent_likelihood": "medium", "inherent_impact": "high"}]
            ws["policies"] = [{"id": "p1", "name": "AUP", "version": "2.1", "mapped_controls": ["CC6.1"]}]
            ws["findings"] = [{"id": "f1", "control_id": "CC6.1", "title": "MFA gap", "severity": "major", "status": "open"}]
            ws["audit_periods"] = [{"id": "ap1", "name": "Q1", "start_date": "2026-01-01", "end_date": "2026-03-31", "frozen": False}]
            ws["policy_attestations"] = [{"policy_id": "p1", "user_name": "Bob", "date": "2026-06-26"}]
            ws["evidence_requests"] = [{"id": "er1", "requested_to": "Alice", "description": "Need MFA screenshots"}]

            save_workspace(ws)
            loaded = load_workspace("round-trip-client")

            assert loaded["org_name"] == "Test Corp"
            assert loaded["is_demo"] is True
            assert loaded["current_user_name"] == "tester"
            assert len(loaded["exceptions"]) == 1
            assert loaded["exceptions"][0]["control_id"] == "CC6.1"
            assert len(loaded["risks"]) == 1
            assert len(loaded["policies"]) == 1
            assert len(loaded["findings"]) == 1
            assert len(loaded["audit_periods"]) == 1
            assert len(loaded["policy_attestations"]) == 1
            assert len(loaded["evidence_requests"]) == 1
