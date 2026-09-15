"""Manual posture path — computes posture from approved evidence in the Evidence Hub.

This is the free-tier posture feed (`docs/OPEN_CORE_SPLIT.md` D9). It reads
approved evidence mapped to controls and computes a posture rollup using the
shared ``rollup_statuses`` math.

Design rules:
  - Map evidence → controls, NOT checks → controls (check mapping is closed).
  - Produce the same output schema as ``build_framework_posture`` so the UI
    renders either feed without branching.
  - Label the source as "manual" so the UI distinguishes from collector posture.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from kevidence.control_capabilities import capability_for_control
from kevidence.posture_math import rollup_statuses


def _evidence_status(item: Dict[str, Any]) -> str:
    """Derive a check-like status from an evidence hub record.

    Approved evidence → "pass", rejected → "fail", pending → "warn",
    no evidence → "uncollected".
    """
    review = item.get("review_status", "")
    if review == "approved":
        return "pass"
    if review == "rejected":
        return "fail"
    if review == "pending":
        return "warn"
    return "uncollected"


def build_manual_posture(
    framework: str,
    evidence_by_control: Dict[str, List[Dict[str, Any]]],
    control_names: Optional[Dict[str, Optional[str]]] = None,
    *,
    control_capabilities: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Build posture rollup from manual evidence for one framework.

    Args:
        framework: Framework id (e.g. "cmmc", "soc2", "iso27001").
        evidence_by_control: ``{control_id: [evidence_item, ...]}`` from the
            evidence hub.
        control_names: Optional ``{control_id: display_name}`` for the UI.
        control_capabilities: Optional override for control→capability mapping.
            Falls back to the built-in open-core classification.

    Returns:
        A dict matching the ``build_framework_posture`` schema (capability rows
        carry ``checks`` with per-control rows) plus ``source: "manual"``.
    """
    capabilities: Dict[str, List[Dict[str, Any]]] = {}

    for control_id, items in evidence_by_control.items():
        cap = (control_capabilities or {}).get(
            control_id, capability_for_control(framework, control_id)
        )
        statuses = [_evidence_status(it) for it in items]
        badge = rollup_statuses(statuses)
        name = (control_names or {}).get(control_id) or control_id
        latest = max((it.get("uploaded_at", "") for it in items), default="")

        capabilities.setdefault(cap, []).append({
            "check_id": control_id,
            "check_name": name,
            "status": badge,
            "last_run_at": latest,
            "remediation": "",
            "console_url": "",
            "evidence_count": len(items),
            "controls": [
                {"control_id": control_id, "name": name, "attested_status": None}
            ],
        })

    cap_rows = []
    for cap, checks in capabilities.items():
        cap_rows.append({
            "capability": cap,
            "check_count": len(checks),
            "collector_badge": rollup_statuses([c["status"] for c in checks]),
            "attested_count": sum(1 for c in checks if c["status"] == "pass"),
            "checks": checks,
        })
    cap_rows.sort(key=lambda row: row["capability"])

    return {
        "framework": framework,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "manual",
        "capabilities": cap_rows,
    }
