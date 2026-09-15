"""CMMC Level 1 track — 15 FAR 52.204-21 safeguarding requirements (§170.15).

Level 1 (Self) assessment for FCI-only contracts: per-practice status,
scoring (MET count / 15), and the SPRS submission text including the
required Level 1 affirmation (§170.22).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

L1_CONTROLS: List[Dict[str, str]] = [
    {"id": "AC.L1-b.1.i", "title": "Limit information system access to authorized users, processes acting on behalf of authorized users, or devices (including other information systems)."},
    {"id": "AC.L1-b.1.ii", "title": "Limit information system access to the types of transactions and functions that authorized users are permitted to execute."},
    {"id": "AC.L1-b.1.iii", "title": "Verify and control/limit connections to and use of external information systems."},
    {"id": "AC.L1-b.1.iv", "title": "Control information posted or processed on publicly accessible information systems."},
    {"id": "IA.L1-b.1.v", "title": "Identify information system users, processes acting on behalf of users, or devices."},
    {"id": "IA.L1-b.1.vi", "title": "Authenticate (or verify) the identities of those users, processes, or devices, as a prerequisite to allowing access to organizational information systems."},
    {"id": "MP.L1-b.1.vii", "title": "Sanitize or destroy information system media containing Federal Contract Information before disposal or release for reuse."},
    {"id": "PE.L1-b.1.viii", "title": "Limit physical access to organizational information systems, equipment, and the respective operating environments to authorized individuals."},
    {"id": "PE.L1-b.1.ix", "title": "Escort visitors and monitor visitor activity; maintain audit logs of physical access; and control and manage physical access devices."},
    {"id": "SC.L1-b.1.x", "title": "Monitor, control, and protect organizational communications (i.e., information transmitted or received by organizational information systems) at the external boundaries and key internal boundaries of the information systems."},
    {"id": "SC.L1-b.1.xi", "title": "Implement subnetworks for publicly accessible system components that are physically or logically separated from internal networks."},
    {"id": "SI.L1-b.1.xii", "title": "Identify, report, and correct information and information system flaws in a timely manner."},
    {"id": "SI.L1-b.1.xiii", "title": "Provide protection from malicious code at appropriate locations within organizational information systems."},
    {"id": "SI.L1-b.1.xiv", "title": "Update malicious code protection mechanisms when new releases are available."},
    {"id": "SI.L1-b.1.xv", "title": "Perform periodic scans of the information system and real-time scans of files from external sources as files are downloaded, opened, or executed."},
]

L1_STATUSES = ("MET", "NOT MET")

DEFAULT_L1_ASSESSMENT: Dict[str, Any] = {
    "status_date": "",
    "affirming_official": "",
    "affirmed_at": "",
}


def merge_l1_assessment(saved: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    src = saved or {}
    out = dict(DEFAULT_L1_ASSESSMENT)
    for key in DEFAULT_L1_ASSESSMENT:
        val = src.get(key)
        if isinstance(val, str):
            out[key] = val.strip()
        elif val:
            out[key] = val
    return out


def l1_answers(ws: Dict[str, Any]) -> Dict[str, Any]:
    return ws.get("answers_l1") or {}


def build_l1_status(ws: Dict[str, Any]) -> Dict[str, Any]:
    """Per-practice status + Level 1 score (MET count / 15)."""
    answers = l1_answers(ws)
    rows = []
    met = 0
    for control in L1_CONTROLS:
        cid = control["id"]
        status = (answers.get(cid) or {}).get("status", "NOT MET")
        if status == "MET":
            met += 1
        rows.append({
            "id": cid,
            "title": control["title"],
            "status": status,
        })
    assessment = merge_l1_assessment(ws.get("l1_assessment"))
    return {
        "score": met,
        "total": len(L1_CONTROLS),
        "met": met,
        "rows": rows,
        "status_date": assessment.get("status_date"),
        "affirming_official": assessment.get("affirming_official"),
        "affirmed_at": assessment.get("affirmed_at"),
        "all_met": met == len(L1_CONTROLS),
    }


def apply_l1_status(ws: Dict[str, Any], control_id: str, status: str) -> Dict[str, Any]:
    if control_id not in {c["id"] for c in L1_CONTROLS}:
        raise ValueError(f"Unknown Level 1 practice: {control_id}")
    if status not in L1_STATUSES:
        raise ValueError(f"Status must be MET or NOT MET")
    answers = dict(l1_answers(ws))
    entry = dict(answers.get(control_id) or {})
    entry["status"] = status
    entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
    answers[control_id] = entry
    ws["answers_l1"] = answers
    return build_l1_status(ws)


def save_l1_assessment(ws: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    assessment = merge_l1_assessment(payload)
    if assessment.get("status_date") and not assessment["status_date"][:10]:
        raise ValueError("Invalid status date")
    ws["l1_assessment"] = assessment
    return build_l1_status(ws)


def build_l1_entry_text(ws: Dict[str, Any], org_profile: Dict[str, str]) -> str:
    """§170.15 Level 1 (Self) SPRS submission text incl. affirmation (§170.22)."""
    status = build_l1_status(ws)
    assessment = merge_l1_assessment(ws.get("l1_assessment"))
    scope = ws.get("cmmc_scope") or {}
    today = date.today().isoformat()
    status_date = assessment.get("status_date") or today

    lines = [
        "SPRS ENTRY SUMMARY — CMMC LEVEL 1 (SELF) (32 CFR 170.15)",
        "=" * 50,
        "",
        "Use this summary when entering your CMMC Level 1 self-assessment in SPRS (PIEE).",
        "The tool does NOT submit to PIEE — copy these values into the portal.",
        "",
        "CMMC ASSESSMENT",
        f"  CMMC Level:                Level 1 (Self)",
        f"  CMMC Status Date:          {status_date}",
        f"  Assessment scope:          {scope.get('scope_statement') or '(scope statement not set)'}",
        f"  CMMC Status:               {'Final Level 1 (Self)' if status['all_met'] else 'In progress — Level 1 has no POA&M; all 15 safeguards must be MET'}",
        f"  Overall score:             {status['score']} of {status['total']} safeguards MET",
        "",
        "ORGANIZATION",
        f"  Contractor / Org name:     {org_profile.get('org_name') or 'Organization'}",
        f"  System name:               {org_profile.get('system_name') or 'Information System'}",
        f"  CAGE Code:                 {org_profile.get('cage_code') or '(not set)'}",
        f"  UEI:                       {org_profile.get('uei') or '(not set)'}",
        "",
        "LEVEL 1 SAFEGUARDS (FAR 52.204-21)",
    ]
    for row in status["rows"]:
        lines.append(f"  [{row['status'] == 'MET' and 'x' or ' '}] {row['id']} — {row['title'][:80]}")
    lines.extend([
        "",
        "AFFIRMATION (32 CFR 170.22)",
        f"  Affirming Official:        {assessment.get('affirming_official') or '(not set)'}",
        "  Affirmation:               [ ] Submit CMMC affirmation in SPRS attesting to continuing compliance",
        "",
        "PIEE ENTRY CHECKLIST",
        "  [ ] Log in to PIEE (https://piee.eb.mil) → SPRS",
        "  [ ] Enter CMMC Level 1 (Self), Status Date, and Assessment Scope",
        "  [ ] Enter overall score and affirmation",
        "",
        f"Generated by CMMC local assessment tool on {today}.",
    ])
    return "\n".join(lines)
