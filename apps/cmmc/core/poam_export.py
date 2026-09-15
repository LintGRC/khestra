"""DoW-style POA&M export — CSV and Excel with readable column widths."""

from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Dict, List, Optional

import pandas as pd

from controls import CMMC_FRAMEWORK

POAM_COLUMNS = [
    "Weakness ID",
    "Control ACID",
    "SPRS Weight",
    "Weakness Name",
    "Weakness Description",
    "Likelihood",
    "Impact",
    "Risk",
    "POC",
    "Resources Required",
    "Scheduled Completion Date",
    "Milestone with Completion Dates",
    "Milestone Changes",
    "Source of Risk",
    "Mitigation",
    "Residual Risk",
    "170.21 POA&M Eligible",
]

RISK_LEVEL_LIKELIHOOD: dict[str, int] = {
    "critical": 5, "high": 4, "medium": 3, "low": 2,
}
RISK_LEVEL_IMPACT: dict[str, int] = {
    "critical": 5, "high": 4, "medium": 3, "low": 2,
}


def _exceptions_to_poam_entries(
    exceptions: List[Dict[str, Any]], scoped_controls: List[str]
) -> List[Dict[str, Any]]:
    """Convert exception/POA&M items into POA&M export row dicts."""
    entries: list[dict[str, Any]] = []
    known_controls = set(scoped_controls)
    for ex in exceptions:
        cid = ex.get("control_id") or ex.get("control_reference") or ""
        if cid and cid not in known_controls:
            continue
        likelihood = RISK_LEVEL_LIKELIHOOD.get(ex.get("risk_level", "medium"), 3)
        impact = RISK_LEVEL_IMPACT.get(ex.get("risk_level", "medium"), 3)
        control_info = CMMC_FRAMEWORK.get(cid, {})
        milestones = ex.get("milestones") or []
        milestone_str = "; ".join(
            f"{m.get('description','')} [{m.get('status','not_started')}]"
            + (f" — due {m.get('target_date','')}" if m.get('target_date') else "")
            + (f" ✓ {m.get('completion_date','')}" if m.get('completion_date') else "")
            for m in milestones
        )
        ra = ex.get("risk_assessment") or {}
        entries.append({
            "Weakness ID": f"WK-EX-{len(entries)+1:04d}",
            "Control ACID": cid,
            "SPRS Weight": control_info.get("weight", 0),
            "Weakness Name": ex.get("title", ""),
            "Weakness Description": ex.get("description", ""),
            "Likelihood": likelihood,
            "Impact": impact,
            "Risk": f"{likelihood} × {impact}",
            "POC": ex.get("owner", "TBD"),
            "Resources Required": "$0",
            "Scheduled Completion Date": ex.get("expiry_date", ""),
            "Milestone with Completion Dates": milestone_str,
            "Milestone Changes": "",
            "Source of Risk": "Exception / POA&M",
            "Mitigation": ex.get("compensating_controls", ""),
            "Residual Risk": ra.get("residual", ""),
        })
    return entries


def poam_gap_controls(answers: Dict[str, Any], scoped_controls: List[str]) -> List[str]:
    """Scoped controls that belong on the POA&M (non-MET, incl. unjustified N/A).

    Consistent with sprs_engine scoring: N/A without a written justification is
    treated as not met and appears on the POA&M.
    """
    gaps = []
    for cid in scoped_controls:
        if cid not in answers or cid not in CMMC_FRAMEWORK:
            continue
        ans = answers[cid]
        if ans["status"] in ("MET", "INHERITED"):
            continue
        if ans["status"] == "NOT APPLICABLE":
            if (ans.get("justification") or "").strip():
                continue
        gaps.append(cid)
    gaps.sort(key=lambda c: (-CMMC_FRAMEWORK[c]["weight"], c))
    return gaps


def poam_weakness_ids(answers: Dict[str, Any], scoped_controls: List[str]) -> Dict[str, str]:
    """control_id -> POA&M Weakness ID (e.g. 'AC.L2-3.1.1' -> 'WK-0001').

    Single source of truth for weakness numbering so the SSP can cross-reference
    "remediation tracked in POA&M Item #N" with the exported POA&M rows.
    """
    return {cid: f"WK-{i + 1:04d}" for i, cid in enumerate(poam_gap_controls(answers, scoped_controls))}


def build_poam_dataframe(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    exceptions: Optional[List[Dict[str, Any]]] = None,
) -> pd.DataFrame:
    from poam_eligibility import poam_eligibility

    poam_entries = []
    gap_controls = poam_gap_controls(answers, scoped_controls)

    eligibility = poam_eligibility(answers, scoped_controls)
    eligible_set = set(eligibility["eligible_ids"])

    for cid in gap_controls:
        ans = answers[cid]
        control_info = CMMC_FRAMEWORK[cid]
        likelihood = ans.get("likelihood", "Medium")
        impact = ans.get("impact", "Medium")
        poam_entries.append(
            {
                "Weakness ID": f"WK-{len(poam_entries)+1:04d}",
                "Control ACID": cid,
                "SPRS Weight": control_info["weight"],
                "Weakness Name": control_info["name"],
                "Weakness Description": ans.get("assessor_notes", ""),
                "Likelihood": likelihood,
                "Impact": impact,
                "Risk": f"{likelihood} × {impact}",
                "POC": ans.get("owner", "TBD"),
                "Resources Required": f"${ans.get('estimated_cost', '0')}",
                "Scheduled Completion Date": ans.get("target_date", ""),
                "Milestone with Completion Dates": "",
                "Milestone Changes": "",
                "Source of Risk": "Internal Assessment",
                "Mitigation": ans.get("remediation_plan", ""),
                "Residual Risk": "",
                "170.21 POA&M Eligible": "Yes" if cid in eligible_set else "No",
            }
        )

    if exceptions:
        poam_entries.extend(_exceptions_to_poam_entries(exceptions, scoped_controls))

    if not poam_entries:
        return pd.DataFrame(columns=POAM_COLUMNS)
    return pd.DataFrame(poam_entries)


def export_poam_csv(answers: Dict[str, Any], scoped_controls: List[str]) -> bytes:
    df = build_poam_dataframe(answers, scoped_controls)
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()


def export_poam_xlsx(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    exceptions: Optional[List[Dict[str, Any]]] = None,
) -> bytes:
    df = build_poam_dataframe(answers, scoped_controls, exceptions)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="POA&M")
        sheet = writer.sheets["POA&M"]
        for col_cells in sheet.columns:
            letter = col_cells[0].column_letter
            max_len = max(len(str(cell.value or "")) for cell in col_cells)
            sheet.column_dimensions[letter].width = min(max(max_len + 2, 12), 72)
    return output.getvalue()


def export_poam_oscal(
    answers: Dict[str, Any],
    scoped_controls: List[str],
    exceptions: Optional[List[Dict[str, Any]]] = None,
    org_name: str = "Organization",
) -> Dict[str, Any]:
    """Export the POA&M as an OSCAL plan-of-action-and-milestones JSON document.

    Minimal conformant subset of the OSCAL POA&M model: metadata + poam-items
    with props (control-id, poam-id, severity, target dates) and remediation
    tasks derived from milestones. Consumable by FedRAMP/OSCAL tooling.
    """
    import uuid as _uuid

    df = build_poam_dataframe(answers, scoped_controls, exceptions)

    def _rows() -> List[Dict[str, Any]]:
        if df.empty:
            return []
        return df.to_dict(orient="records")

    def _tasks(row: Dict[str, Any]) -> List[Dict[str, Any]]:
        milestone_str = str(row.get("Milestone with Completion Dates") or "")
        if not milestone_str:
            return []
        tasks = []
        for piece in milestone_str.split("; "):
            if not piece:
                continue
            tasks.append({
                "uuid": str(_uuid.uuid4()),
                "title": piece,
                "props": [{"name": "status", "value": "in-progress"}],
            })
        return tasks

    items = []
    for row in _rows():
        cid = str(row.get("Control ACID") or "")
        props = [
            {"name": "control-id", "value": cid},
            {"name": "poam-id", "value": str(row.get("Weakness ID") or "")},
            {"name": "severity", "value": str(row.get("Likelihood") or "medium")},
            {"name": "sprs-weight", "value": str(row.get("SPRS Weight") or 0)},
            {"name": "risk", "value": str(row.get("Risk") or "")},
            {"name": "poc", "value": str(row.get("POC") or "TBD")},
            {"name": "source", "value": str(row.get("Source of Risk") or "")},
        ]
        target = str(row.get("Scheduled Completion Date") or "")
        if target:
            props.append({"name": "target-date", "value": target})
        eligible = str(row.get("170.21 POA&M Eligible") or "")
        if eligible:
            props.append({"name": "poam-eligible", "value": eligible})
        remediation = str(row.get("Mitigation") or "")
        tasks = _tasks(row)
        item: Dict[str, Any] = {
            "uuid": str(_uuid.uuid4()),
            "title": str(row.get("Weakness Name") or cid),
            "description": str(row.get("Weakness Description") or ""),
            "props": props,
        }
        if remediation or tasks:
            item["remediation"] = {"purpose": remediation or "Tracked in Khestra POA&M"}
            if tasks:
                item["remediation"]["tasks"] = tasks
        items.append(item)

    return {
        "plan-of-action-and-milestones": {
            "uuid": str(_uuid.uuid4()),
            "metadata": {
                "title": f"POA&M — {org_name}",
                "last-modified": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "version": "0.1.0",
                "oscal-version": "1.1.2",
            },
            "poam-items": items,
        }
    }
