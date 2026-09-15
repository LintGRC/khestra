"""Import POA&M / gap updates from CSV into assessment answers."""

import csv
import io
from typing import Any, Dict, List, Tuple

from controls import CMMC_FRAMEWORK

# Column aliases (case-insensitive match on header)
COLUMN_MAP = {
    "control acid": "control_id",
    "control_acid": "control_id",
    "control id": "control_id",
    "control_id": "control_id",
    "acid": "control_id",
    "cid": "control_id",
    "status": "status",
    "implementation status": "status",
    "weakness description": "assessor_notes",
    "description": "assessor_notes",
    "notes": "assessor_notes",
    "poc": "owner",
    "owner": "owner",
    "scheduled completion date": "target_date",
    "target date": "target_date",
    "target_date": "target_date",
    "mitigation": "remediation_plan",
    "remediation": "remediation_plan",
    "likelihood": "likelihood",
    "impact": "impact",
    "resources required": "estimated_cost",
    "estimated cost": "estimated_cost",
}

VALID_STATUSES = {
    "NOT STARTED",
    "IN PROGRESS",
    "PARTIALLY MET",
    "MET",
    "NOT APPLICABLE",
    "INHERITED",
    "PLANNED",
    "NOT MET",
}


def _normalize_header(h: str) -> str:
    return (h or "").strip().lower()


def _map_row(raw: Dict[str, str]) -> Dict[str, str]:
    mapped: Dict[str, str] = {}
    for key, val in raw.items():
        field = COLUMN_MAP.get(_normalize_header(key))
        if field and (val or "").strip():
            mapped[field] = val.strip()
    return mapped


def import_poam_csv(
    file_bytes: bytes,
    answers: Dict[str, Any],
    scoped_controls: List[str],
) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """
    Merge CSV rows into answers. Returns (updated_answers, applied_ids, warnings).
    """
    text = file_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return answers, [], ["CSV has no header row."]

    updated = {cid: dict(answers.get(cid, {})) for cid in answers}
    applied: List[str] = []
    warnings: List[str] = []

    for i, raw in enumerate(reader, start=2):
        row = _map_row(raw)
        cid = row.get("control_id", "").strip()
        if not cid:
            continue
        if cid not in CMMC_FRAMEWORK:
            warnings.append(f"Row {i}: unknown control {cid!r} — skipped.")
            continue
        if cid not in scoped_controls:
            warnings.append(f"Row {i}: {cid} not in scope — skipped.")
            continue

        ans = updated.setdefault(cid, {})
        if "status" in row:
            status = row["status"].upper().replace("_", " ")
            if status not in VALID_STATUSES:
                titled = status.title()
                if titled in VALID_STATUSES:
                    status = titled
            if status in VALID_STATUSES:
                ans["status"] = status
            else:
                warnings.append(f"Row {i}: invalid status {row['status']!r} for {cid}.")
        for field in ("assessor_notes", "owner", "target_date", "remediation_plan", "likelihood", "impact"):
            if field in row:
                ans[field] = row[field]
        if "estimated_cost" in row:
            ans["estimated_cost"] = row["estimated_cost"].replace("$", "").strip()
        applied.append(cid)

    if not applied:
        warnings.append("No rows matched scoped controls. Expected column: Control ACID or control_id.")

    return updated, applied, warnings
