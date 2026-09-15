"""Format audit_log for UI and export."""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List

FIELD_LABELS = {
    "status": "Status",
    "implementation_narrative": "Implementation narrative",
    "assessor_notes": "Notes",
    "maturity": "Maturity",
    "evidence_added": "Evidence attached",
}


def describe_change(entry: Dict[str, Any]) -> str:
    field = entry.get("field", "")
    if field == "evidence_added":
        return f"Attached {entry.get('new_value', 'file')}"
    label = FIELD_LABELS.get(field, field.replace("_", " ").title())
    old = (entry.get("old_value") or "")[:120]
    new = (entry.get("new_value") or "")[:120]
    if field in ("implementation_narrative", "assessor_notes"):
        if old and new:
            return f"{label} updated"
        return f"{label} added" if new else f"{label} cleared"
    if old and new and old != new:
        return f"{label}: {old} → {new}"
    return f"{label}: {new or old}"


def recent_changes(audit_log: List[Dict[str, Any]], limit: int = 100) -> List[Dict[str, Any]]:
    return list(reversed(audit_log[-limit:]))


def audit_log_to_csv(audit_log: List[Dict[str, Any]]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["timestamp", "control_id", "field", "description", "user_role"])
    for entry in audit_log:
        writer.writerow(
            [
                entry.get("timestamp", ""),
                entry.get("control_id", ""),
                entry.get("field", ""),
                describe_change(entry),
                entry.get("user_role", ""),
            ]
        )
    return buf.getvalue().encode("utf-8")
