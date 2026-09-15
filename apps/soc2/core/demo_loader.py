"""Load synthetic SOC 2 demo workspace."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict

from client_workspaces import active_client_id
from demo_data import AUDIT_PERIOD_START, AUDIT_PERIOD_END, get_demo_session_payload
from workspace_service import save_workspace


def _build_demo_policies(org_name: str) -> list:
    from policy_content import TEMPLATES
    from policy_export import fill_template

    seeded = []
    for key in ("acceptable_use_policy", "access_control_policy", "incident_response_policy",
                 "change_management_policy", "vendor_management_policy", "data_classification_policy",
                 "password_authentication_policy", "risk_assessment_policy",
                 "business_continuity_policy", "code_of_conduct_policy"):
        data = fill_template(key, org_name=org_name)
        import uuid
        now = date.today().strftime("%Y-%m-%d")
        data["id"] = uuid.uuid4().hex[:12]
        data["created_at"] = now
        data["updated_at"] = now
        data["filename"] = ""
        data["file_uploaded"] = False
        seeded.append(data)
    return seeded


def load_demo(demo_id: str = "northwind", client_id: str | None = None, org_name: str | None = None) -> Dict[str, Any]:
    from collectors.engine import run_collector
    from soc2_collectors.attach import attach_check_to_controls

    payload = get_demo_session_payload()
    cid = client_id or active_client_id()
    name = org_name or payload["org_name"]
    ws: Dict[str, Any] = {
        "client_id": cid,
        "org_name": name,
        "answers": payload["answers"],
        "audit_log": [],
        "audit_periods": [{
            "id": "demo_period",
            "name": "SOC 2 Type II — 2026",
            "start_date": AUDIT_PERIOD_START,
            "end_date": AUDIT_PERIOD_END,
            "frozen": False,
            "frozen_at": None,
            "created_at": "2026-01-01",
        }],
        "evidence_requests": [],
        "exceptions": [],
        "risks": [],
        "policies": _build_demo_policies(name),
        "policy_attestations": [],
        "findings": [],
        "current_role": "Assessor",
        "current_user_name": "",
        "is_demo": True,
        "demo_id": demo_id,
        "restored_evidence": {},
    }

    for connector_id in ("entra", "github"):
        run = run_collector(connector_id, use_fixture=True)
        for check in run.checks:
            if check.status == "error":
                continue
            ws, _ = attach_check_to_controls(ws, connector_id, check)

    save_workspace(ws)
    return ws
