"""Synthetic SOC 2 demo organization."""

from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256
from typing import Any, Dict

from soc2_catalog import SOC2_CONTROLS
from workspace_service import default_control_answer

DEMO_ORG = "Trident Defense Systems"

DEMO_GAPS = {
    "CC6.1": {
        "status": "IN PROGRESS",
        "implementation_narrative": (
            "Entra Conditional Access enforces MFA for all production SaaS admin roles. "
            "Two legacy service accounts still lack phishing-resistant MFA — remediation in flight."
        ),
        "remediation_plan": "Migrate service accounts to managed identities; enforce FIDO2 for admins.",
        "owner": "Jordan Lee",
        "target_date": "2026-09-15",
    },
    "CC7.1": {
        "status": "NOT MET",
        "implementation_narrative": (
            "CloudTrail is enabled in the primary AWS account; secondary sandbox account logging is incomplete."
        ),
        "remediation_plan": "Enable organization trail; forward to SIEM with 90-day retention.",
        "owner": "Sam Patel",
        "target_date": "2026-08-01",
    },
    "CC6.6": {
        "status": "PLANNED",
        "implementation_narrative": "GuardDuty enabled in prod; EDR rollout to contractor laptops scheduled Q3.",
        "remediation_plan": "Deploy EDR agent; tune GuardDuty findings workflow.",
        "owner": "Jordan Lee",
        "target_date": "2026-10-01",
    },
}

AUDIT_PERIOD_START = "2026-01-01"
AUDIT_PERIOD_END = "2026-06-30"

DEMO_EVIDENCE_CONTROLS = [
    "CC1.1", "CC1.2", "CC1.3", "CC1.4",
    "CC2.1", "CC2.2",
    "CC3.1", "CC3.2", "CC3.3",
    "CC4.1", "CC4.2",
    "CC5.1", "CC5.2", "CC5.3",
    "CC6.2", "CC6.3", "CC6.4", "CC6.7",
    "CC7.3", "CC7.4",
    "CC8.1",
    "CC9.1", "CC9.2",
    "A1.1", "A1.2",
    "C1.1", "C1.2",
    "PI1.1", "PI1.2", "PI1.3",
    "P1.1", "P3.1", "P5.1", "P7.1",
]

def _fake_sha(content: str) -> str:
    return sha256(content.encode()).hexdigest()


def get_demo_session_payload() -> Dict[str, Any]:
    answers: Dict[str, Any] = {}
    today = datetime.now()
    for i, cid in enumerate(SOC2_CONTROLS):
        meta = SOC2_CONTROLS[cid]
        ans = default_control_answer()
        gap = DEMO_GAPS.get(cid)
        if gap:
            ans.update(gap)
        else:
            ans["status"] = "MET"
            ans["implementation_narrative"] = (
                f"Trident Defense Systems satisfies {meta['title']} through documented policies, Entra ID access controls, "
                f"and quarterly access reviews. Evidence: policy export, access review ticket, sample log extract."
            )
            ans["owner"] = "Jordan Lee"

        if cid in DEMO_EVIDENCE_CONTROLS:
            ev_type = ("policy_export", "config_screenshot", "access_review_log", "training_record")[i % 4]
            offset_days = (i * 7) % 220
            upload_date = (today - timedelta(days=offset_days)).strftime("%Y-%m-%d")
            content = f"demo_evidence_{cid}_{ev_type}"
            evidence_entry = {
                "filename": f"soc2_{ev_type}_{cid.lower().replace('.','_')}.pdf",
                "upload_date": upload_date,
                "sha256": _fake_sha(content),
                "data_bytes": content.encode(),
                "source": "manual",
                "review_status": "approved",
                "valid_from": AUDIT_PERIOD_START,
                "valid_to": AUDIT_PERIOD_END,
            }
            ans.setdefault("evidence", []).append(evidence_entry)

        answers[cid] = ans

    return {
        "org_name": DEMO_ORG,
        "answers": answers,
        "is_demo": True,
        "demo_id": "northwind",
    }
