"""Build examine/test text from attached collector JSON evidence."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from evidence_store import get_evidence_bytes
from evidence_hub.store import resolve_evidence_bytes_from_hub


def collector_evidence_bytes(
    control_id: str,
    ev: Dict[str, Any],
    restored_evidence: Optional[Dict[str, bytes]] = None,
) -> Optional[bytes]:
    """Resolve a collector evidence entry's bytes: workspace first, hub fallback.

    Workspace entries usually carry inline bytes (data_bytes) or are served
    from restored_evidence; when both miss (metadata-only entries synced from
    the hub), fall back to reading the hub's `{eid}{ext}` file.
    """
    data = get_evidence_bytes(control_id, ev, restored_evidence)
    if data:
        return data
    filename = ev.get("filename") or ""
    if not str(filename).startswith("collector_"):
        return None
    return resolve_evidence_bytes_from_hub("CMMC", control_id, filename)


def _parse_collector_payload(data: bytes) -> Optional[Dict[str, Any]]:
    try:
        obj = json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(obj, dict) or not obj.get("check_id"):
        return None
    return obj


def _format_collected_at(payload: Dict[str, Any], ev_meta: Dict[str, Any]) -> str:
    return (payload.get("collected_at") or ev_meta.get("upload_date") or "").strip()


def summarize_control_collector_evidence(
    control_id: str,
    answers: Dict[str, Any],
    restored_evidence: Optional[Dict[str, bytes]] = None,
) -> Dict[str, Any]:
    """Summarize collector_* JSON files on one control into examine/test strings."""
    ans = answers.get(control_id) or {}
    evidence_list = ans.get("evidence") or []
    lines: List[Dict[str, str]] = []

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
        check_name = payload.get("check_name") or payload.get("check_id") or "check"
        status = payload.get("status") or "unknown"
        summary = (payload.get("evidence") or "").strip()
        collected = _format_collected_at(payload, ev)
        examine_line = f"{filename}: {check_name} — {summary} (collector {status}"
        if collected:
            examine_line += f", {collected}"
        examine_line += ")"
        lines.append(
            {
                "filename": filename,
                "check_id": str(payload.get("check_id") or ""),
                "connector": str(payload.get("collector") or ""),
                "status": str(status),
                "examine_line": examine_line,
            }
        )

    if not lines:
        return {
            "control_id": control_id,
            "collector_count": 0,
            "examine": "",
            "test": "",
            "lines": [],
        }

    examine = "; ".join(line["examine_line"] for line in lines)
    connectors = sorted({line["connector"] for line in lines if line["connector"]})
    filenames = [line["filename"] for line in lines]
    connector_phrase = connectors[0] if len(connectors) == 1 else "integrated systems"
    test = (
        f"Review attached collector JSON ({', '.join(filenames)}); "
        f"verify SHA-256 hashes and reconcile findings with live {connector_phrase} configuration."
    )

    return {
        "control_id": control_id,
        "collector_count": len(lines),
        "examine": examine,
        "test": test,
        "lines": lines,
    }


def merge_field(existing: str, new_text: str, *, mode: str = "append") -> str:
    existing = (existing or "").strip()
    new_text = (new_text or "").strip()
    if not new_text:
        return existing
    if mode == "replace" or not existing:
        return new_text
    if new_text in existing:
        return existing
    return f"{existing}; {new_text}"


def apply_evidence_summary_to_control(
    state: Dict[str, Any],
    control_id: str,
    *,
    mode: str = "append",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    from workspace_service import patch_control

    summary = summarize_control_collector_evidence(
        control_id,
        state["answers"],
        state.get("restored_evidence"),
    )
    if summary["collector_count"] == 0:
        raise ValueError("No collector evidence attached to this control")

    ans = state["answers"].get(control_id) or {}
    new_examine = merge_field(ans.get("examine") or "", summary["examine"], mode=mode)
    new_test = merge_field(ans.get("test") or "", summary["test"], mode=mode)

    ws = patch_control(
        state,
        control_id,
        examine=new_examine,
        test=new_test,
    )
    return ws, {**summary, "examine": new_examine, "test": new_test, "mode": mode}
