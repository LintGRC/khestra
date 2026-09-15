from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pdf_export.engine import generate_pdf


def build_ssp_summary_pdf(
    ws: Dict[str, Any],
    sprs_result: Dict[str, Any],
) -> bytes:
    org_profile = ws.get("org_profile") or {}
    org_name = org_profile.get("org_name") or "Organization"
    system_name = org_profile.get("system_name") or ""
    answers = ws.get("answers") or {}
    scoped = ws.get("scoped_controls") or []
    families = _control_family_counts(answers, scoped)

    sections: List[Dict[str, Any]] = [
        {"type": "heading", "content": "SSP Summary", "level": 0},
        {"type": "kv", "key": "Organization", "value": org_name},
        {"type": "kv", "key": "System", "value": system_name},
        {"type": "kv", "key": "Date", "value": datetime.now().strftime("%Y-%m-%d")},
        {"type": "kv", "key": "Scoped Controls", "value": str(len(scoped))},
        {"type": "page_break"},
        {"type": "heading", "content": "Control Status by Family", "level": 1},
    ]
    for fam in families:
        sections.append({
            "type": "kv",
            "key": fam["label"],
            "value": f"{fam['met']}/{fam['total']} met  ({fam['pct']:.0f}%)",
        })

    status_counts = _status_counts(answers, scoped)
    sections.append({"type": "page_break"})
    sections.append({"type": "heading", "content": "Status Distribution", "level": 1})
    for status, count in status_counts.items():
        sections.append({"type": "kv", "key": status, "value": str(count)})

    sections.append({"type": "page_break"})
    sections.append({"type": "heading", "content": "SPRS Score", "level": 1})
    final = sprs_result.get("final_score", "N/A")
    sections.append({"type": "kv", "key": "SPRS Score", "value": str(final)})
    breakd = sprs_result.get("breakdown", {})
    sections.append({"type": "kv", "key": "Base Score", "value": str(breakd.get("base", 110))})
    sections.append({
        "type": "kv",
        "key": "Total Gaps",
        "value": str(breakd.get("total_gaps_count", 0)),
    })
    penalties = sprs_result.get("penalties", {})
    sections.append({"type": "kv", "key": "5pt Deductions", "value": str(penalties.get("5pt", 0))})
    sections.append({"type": "kv", "key": "3pt Deductions", "value": str(penalties.get("3pt", 0))})
    sections.append({"type": "kv", "key": "1pt Deductions", "value": str(penalties.get("1pt", 0))})

    return generate_pdf(f"SSP Summary - {org_name}", sections)


def build_poam_pdf(
    ws: Dict[str, Any],
    poam_entries: List[Dict[str, Any]],
) -> bytes:
    org_name = ws.get("org_profile", {}).get("org_name") or "Organization"

    sections: List[Dict[str, Any]] = [
        {"type": "heading", "content": "POA&M Report", "level": 0},
        {"type": "kv", "key": "Organization", "value": org_name},
        {"type": "kv", "key": "Date", "value": datetime.now().strftime("%Y-%m-%d")},
        {"type": "kv", "key": "Open Items", "value": str(len(poam_entries))},
        {"type": "page_break"},
        {"type": "heading", "content": "Open Weaknesses", "level": 1},
    ]
    for i, entry in enumerate(poam_entries, 1):
        sections.append({
            "type": "heading",
            "content": f"{i}. {entry.get('Weakness Name', '')}",
            "level": 2,
        })
        sections.append({
            "type": "kv",
            "key": "Control",
            "value": entry.get("Control ACID", ""),
        })
        sections.append({
            "type": "kv",
            "key": "Risk",
            "value": str(entry.get("Risk", "")),
        })
        sections.append({
            "type": "kv",
            "key": "POC",
            "value": entry.get("POC", ""),
        })
        sections.append({
            "type": "kv",
            "key": "Due Date",
            "value": entry.get("Scheduled Completion Date", ""),
        })
        desc = entry.get("Weakness Description", "")
        if desc:
            sections.append({"type": "text", "content": desc})

    return generate_pdf(f"POA&M - {org_name}", sections)


def build_sprs_pdf(
    ws: Dict[str, Any],
    sprs_result: Dict[str, Any],
    answers: Dict[str, Any],
    scoped_controls: List[str],
) -> bytes:
    org_profile = ws.get("org_profile") or {}
    org_name = org_profile.get("org_name") or "Organization"
    system = org_profile.get("system_name") or "Information System"

    sections: List[Dict[str, Any]] = [
        {"type": "heading", "content": "SPRS Summary", "level": 0},
        {"type": "kv", "key": "Organization", "value": org_name},
        {"type": "kv", "key": "System", "value": system},
        {"type": "kv", "key": "Date", "value": datetime.now().strftime("%Y-%m-%d")},
        {"type": "page_break"},
        {"type": "heading", "content": "Score Breakdown", "level": 1},
    ]

    final = sprs_result.get("final_score", "N/A")
    breakd = sprs_result.get("breakdown", {})
    penalties = sprs_result.get("penalties", {})
    sections.append({"type": "kv", "key": "Final Score", "value": str(final)})
    sections.append({"type": "kv", "key": "Base Score", "value": str(breakd.get("base", 110))})
    sections.append({
        "type": "kv",
        "key": "5pt Deductions",
        "value": f"{penalties.get('5pt', 0)}  ({breakd.get('5pt_deductions', 0)} pts)",
    })
    sections.append({
        "type": "kv",
        "key": "3pt Deductions",
        "value": f"{penalties.get('3pt', 0)}  ({breakd.get('3pt_deductions', 0)} pts)",
    })
    sections.append({
        "type": "kv",
        "key": "1pt Deductions",
        "value": f"{penalties.get('1pt', 0)}  ({breakd.get('1pt_deductions', 0)} pts)",
    })
    sections.append({
        "type": "kv",
        "key": "MFA Deduction",
        "value": str(breakd.get("mfa_variable", 0)),
    })
    sections.append({
        "type": "kv",
        "key": "FIPS Deduction",
        "value": str(breakd.get("fips_variable", 0)),
    })
    sections.append({
        "type": "kv",
        "key": "Total Gaps",
        "value": str(breakd.get("total_gaps_count", 0)),
    })

    met = sum(1 for c in scoped_controls if answers.get(c, {}).get("status") == "MET")
    sections.append({"type": "kv", "key": "Controls Met", "value": f"{met} / {len(scoped_controls)}"})

    critical = sprs_result.get("critical_gaps", [])
    moderate = sprs_result.get("moderate_gaps", [])
    low = sprs_result.get("low_gaps", [])
    if critical:
        sections.append({"type": "page_break"})
        sections.append({"type": "heading", "content": "Critical Gaps (5pt)", "level": 1})
        for cid in critical:
            sections.append({"type": "bullet", "content": cid})
    if moderate:
        sections.append({"type": "heading", "content": "Moderate Gaps (3pt)", "level": 1})
        for cid in moderate:
            sections.append({"type": "bullet", "content": cid})
    if low:
        sections.append({"type": "heading", "content": "Low Gaps (1pt)", "level": 1})
        for cid in low:
            sections.append({"type": "bullet", "content": cid})

    return generate_pdf(f"SPRS Score - {org_name}", sections)


_CONTROL_FAMILY_LABELS: Dict[str, str] = {
    "AC": "Access Control",
    "AU": "Audit & Accountability",
    "AT": "Awareness & Training",
    "CM": "Configuration Management",
    "IA": "Identification & Authentication",
    "IR": "Incident Response",
    "MA": "Maintenance",
    "MP": "Media Protection",
    "PS": "Personnel Security",
    "PE": "Physical Protection",
    "PL": "Planning",
    "PM": "Program Management",
    "RA": "Risk Assessment",
    "CA": "Security Assessment",
    "SC": "System & Communications Protection",
    "SI": "System & Information Integrity",
    "SA": "System & Services Acquisition",
}


def _control_family(family_code: str) -> str:
    return _CONTROL_FAMILY_LABELS.get(family_code, f"Family {family_code}")


def _control_family_counts(
    answers: Dict[str, Any], scoped_controls: List[str]
) -> List[Dict[str, Any]]:
    counts: Dict[str, Dict[str, int]] = {}
    for cid in scoped_controls:
        parts = cid.split("-", 1)
        code = parts[0].split(".")[0]
        if code not in counts:
            counts[code] = {"total": 0, "met": 0}
        counts[code]["total"] += 1
        status = answers.get(cid, {}).get("status", "")
        if status == "MET":
            counts[code]["met"] += 1
    result = []
    for code, c in counts.items():
        result.append({
            "label": _control_family(code),
            "total": c["total"],
            "met": c["met"],
            "pct": (c["met"] / c["total"] * 100) if c["total"] else 0,
        })
    return sorted(result, key=lambda x: x["label"])


def _status_counts(
    answers: Dict[str, Any], scoped_controls: List[str]
) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for cid in scoped_controls:
        status = answers.get(cid, {}).get("status", "NOT STARTED")
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def build_executive_report(
    ws: Dict[str, Any],
    sprs_result: Dict[str, Any],
    poam_eligibility: Dict[str, Any],
    risks: List[Dict[str, Any]],
) -> bytes:
    """One-page executive board report: posture, top risks, POA&M health, resource ask."""
    org_profile = ws.get("org_profile") or {}
    org_name = org_profile.get("org_name") or "Organization"
    system = org_profile.get("system_name") or "Information System"
    answers = ws.get("answers") or {}
    scoped = ws.get("scoped_controls") or []
    sprs_history = list(ws.get("sprs_history") or [])

    final = sprs_result.get("final_score", 0)
    met = sum(1 for c in scoped if answers.get(c, {}).get("status") == "MET")
    total = len(scoped) or 1
    met_pct = round(met * 100.0 / total, 1)
    breakd = sprs_result.get("breakdown", {})
    open_gaps = breakd.get("total_gaps_count", 0)

    sections: List[Dict[str, Any]] = [
        {"type": "heading", "content": "Executive Board Report", "level": 0},
        {"type": "kv", "key": "Organization", "value": org_name},
        {"type": "kv", "key": "System", "value": system},
        {"type": "kv", "key": "Date", "value": datetime.now().strftime("%Y-%m-%d")},
        {"type": "page_break"},
        {"type": "heading", "content": "1. Executive Summary", "level": 1},
        {"type": "kv", "key": "SPRS Score", "value": f"{final} / 110"},
        {"type": "kv", "key": "Controls Met", "value": f"{met} / {total}  ({met_pct}%)"},
        {"type": "kv", "key": "Open POA&M Items", "value": str(open_gaps)},
        {"type": "kv", "key": "POA&M Eligibility", "value": _eligibility_label(poam_eligibility)},
    ]

    sections.append({"type": "page_break"})
    sections.append({"type": "heading", "content": "2. Posture Over Time", "level": 1})
    if len(sprs_history) >= 2:
        recent = sprs_history[-6:]
        sections.append({
            "type": "barchart",
            "title": "SPRS Score Trend",
            "labels": [h.get("timestamp", "")[:10] for h in recent],
            "values": [h.get("score", 0) for h in recent],
            "value_suffix": "",
        })
        sections.append({"type": "text", "content": "Note: historical snapshots are recorded each time a control status changes. Full readiness tracking began with the Executive Report feature."})
    else:
        sections.append({
            "type": "text",
            "content": "Not enough history yet. Snapshots are recorded as control statuses change; keep the workspace active to build the trend line.",
        })

    sections.append({"type": "page_break"})
    sections.append({"type": "heading", "content": "3. Top Risks", "level": 1})
    top_risks = sorted(
        [r for r in risks if r.get("status") != "closed"],
        key=lambda r: r.get("inherent_score", 0) or 0,
        reverse=True,
    )[:5]
    if top_risks:
        for i, risk in enumerate(top_risks, 1):
            sections.append({
                "type": "heading",
                "content": f"{i}. {risk.get('title', 'Untitled risk')}",
                "level": 2,
            })
            sections.append({"type": "kv", "key": "Inherent Score", "value": str(risk.get("inherent_score", 0))})
            sections.append({"type": "kv", "key": "Residual Score", "value": str(risk.get("residual_score", 0))})
            sections.append({"type": "kv", "key": "Treatment", "value": risk.get("treatment", "")})
            desc = risk.get("description", "")
            if desc:
                sections.append({"type": "text", "content": desc})
    else:
        sections.append({"type": "text", "content": "No open risks in the risk register."})

    sections.append({"type": "page_break"})
    sections.append({"type": "heading", "content": "4. POA&M Health", "level": 1})
    sections.append({"type": "kv", "key": "Open Items", "value": str(open_gaps)})
    sections.append({
        "type": "kv",
        "key": "Estimated Close Cost",
        "value": _total_close_cost(answers, scoped),
    })
    sections.append({
        "type": "kv",
        "key": "Avg Scheduled Completion",
        "value": _avg_target_date(answers, scoped),
    })
    overdue = _overdue_count(answers, scoped)
    sections.append({"type": "kv", "key": "Overdue Items", "value": str(overdue)})
    sections.append({
        "type": "kv",
        "key": "180-Day Closeout",
        "value": _eligibility_label(poam_eligibility),
    })

    resource_ask = (org_profile.get("board_resource_ask") or "").strip()
    if resource_ask:
        sections.append({"type": "page_break"})
        sections.append({"type": "heading", "content": "5. Resource Ask", "level": 1})
        sections.append({"type": "text", "content": resource_ask})

    return generate_pdf(f"Executive Board Report - {org_name}", sections)


def _eligibility_label(poam_eligibility: Dict[str, Any]) -> str:
    if not poam_eligibility:
        return "N/A"
    eligible = poam_eligibility.get("eligible")
    if eligible is True:
        return f"Eligible (score {poam_eligibility.get('score', '?')} >= {poam_eligibility.get('threshold', 88)})"
    if eligible is False:
        return f"Not eligible - score {poam_eligibility.get('score', '?')} below {poam_eligibility.get('threshold', 88)}"
    return "Undetermined"


def _total_close_cost(answers: Dict[str, Any], scoped_controls: List[str]) -> str:
    total = 0.0
    for cid in scoped_controls:
        ans = answers.get(cid, {})
        status = ans.get("status", "")
        if status in ("MET", "NOT APPLICABLE", "INHERITED"):
            continue
        try:
            total += float(ans.get("estimated_cost") or 0)
        except (TypeError, ValueError):
            pass
    return f"${total:,.0f}"


def _avg_target_date(answers: Dict[str, Any], scoped_controls: List[str]) -> str:
    dates = []
    for cid in scoped_controls:
        ans = answers.get(cid, {})
        status = ans.get("status", "")
        if status in ("MET", "NOT APPLICABLE", "INHERITED"):
            continue
        t = (ans.get("target_date") or "").strip()
        if t:
            dates.append(t[:10])
    if not dates:
        return "Not scheduled"
    return ", ".join(sorted(dates)[:4]) + ("..." if len(dates) > 4 else "")


def _overdue_count(answers: Dict[str, Any], scoped_controls: List[str]) -> int:
    today = datetime.now().date()
    overdue = 0
    for cid in scoped_controls:
        ans = answers.get(cid, {})
        status = ans.get("status", "")
        if status in ("MET", "NOT APPLICABLE", "INHERITED"):
            continue
        t = (ans.get("target_date") or "").strip()
        if not t:
            continue
        try:
            if datetime.strptime(t[:10], "%Y-%m-%d").date() < today:
                overdue += 1
        except ValueError:
            pass
    return overdue
