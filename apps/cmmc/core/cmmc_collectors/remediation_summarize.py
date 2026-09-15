"""Build remediation_plan text from collector JSON with fail/warn/error checks."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from evidence_store import get_evidence_bytes

from cmmc_collectors.evidence_summarize import (
    _format_collected_at,
    _parse_collector_payload,
    collector_evidence_bytes,
)

_GAP_CHECK_STATUSES = frozenset({"fail", "warn", "error"})


def _mitigation_line(check_name: str, evidence: str, status: str) -> str:
    name = (check_name or "check").strip()
    summary = (evidence or "").strip()
    prefix = "Review and resolve" if status == "warn" else "Remediate"
    if summary:
        return f"{prefix} {name}: {summary}"
    return f"{prefix} {name}"


def merge_remediation_plan(existing: str, new_text: str, *, mode: str = "append") -> str:
    existing = (existing or "").strip()
    new_text = (new_text or "").strip()
    if not new_text:
        return existing
    if mode == "replace" or not existing:
        return new_text
    if new_text in existing:
        return existing
    return f"{existing}\n{new_text}"


def summarize_collector_remediation_gaps(
    control_id: str,
    answers: Dict[str, Any],
    restored_evidence: Optional[Dict[str, bytes]] = None,
) -> Dict[str, Any]:
    """Summarize fail/warn collector checks on one control into remediation_plan text."""
    ans = answers.get(control_id) or {}
    evidence_list = ans.get("evidence") or []
    lines: List[Dict[str, str]] = []
    collector_count = 0

    for ev in evidence_list:
        filename = ev.get("filename") or ""
        if not str(filename).startswith("collector_"):
            continue
        data = collector_evidence_bytes(control_id, ev, restored_evidence)
        if not data:
            continue
        payload = _parse_collector_payload(data)
        if not payload:
            continue
        collector_count += 1
        status = str(payload.get("status") or "unknown").lower()
        if status not in _GAP_CHECK_STATUSES:
            continue
        check_name = str(payload.get("check_name") or payload.get("check_id") or "check")
        summary = str(payload.get("evidence") or "").strip()
        lines.append(
            {
                "filename": filename,
                "check_id": str(payload.get("check_id") or ""),
                "connector": str(payload.get("collector") or ""),
                "status": status,
                "collected_at": _format_collected_at(payload, ev),
                "mitigation_line": _mitigation_line(check_name, summary, status),
            }
        )

    remediation_plan = "\n".join(line["mitigation_line"] for line in lines)

    return {
        "control_id": control_id,
        "collector_count": collector_count,
        "gap_count": len(lines),
        "remediation_plan": remediation_plan,
        "lines": lines,
    }


def apply_remediation_summary_to_control(
    state: Dict[str, Any],
    control_id: str,
    *,
    mode: str = "append",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    from workspace_service import patch_control

    summary = summarize_collector_remediation_gaps(
        control_id,
        state["answers"],
        state.get("restored_evidence"),
    )
    if summary["gap_count"] == 0:
        raise ValueError("No fail or warn collector checks on this control")

    ans = state["answers"].get(control_id) or {}
    new_plan = merge_remediation_plan(ans.get("remediation_plan") or "", summary["remediation_plan"], mode=mode)

    ws = patch_control(state, control_id, remediation_plan=new_plan)
    return ws, {**summary, "remediation_plan": new_plan, "mode": mode}
