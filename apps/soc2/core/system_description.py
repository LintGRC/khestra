"""SOC 2 system description export — auditor-facing narrative pack.
Maps to AICPA Description Criteria (DC Section 200, 2018, rev. 2022).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from readiness import compute_dashboard
from soc2_catalog import SOC2_CONTROLS
from workspace_service import default_control_answer, list_audit_periods
from tsc_scoping import DEFAULT_SCOPE, get_in_scope_controls

# AICPA DC Section 200 — Description Criteria used to evaluate the System Description.
# Titles/descriptions + required flag come from the official lock (dc_200_official.py);
# only the app-specific wizard_field mapping is maintained here.
from dc_200_official import DC_CRITERIA, dc_description, dc_required, dc_title

_DC_WIZARD_FIELDS: Dict[str, List[str]] = {
    "DC-1.1": ["system_name", "system_description"],
    "DC-1.2": ["cloud_providers", "data_centers", "architecture_summary"],
    "DC-1.3": ["tech_stack", "software_inventory"],
    "DC-1.4": ["system_owner", "compliance_officer", "it_admin"],
    "DC-1.5": ["data_classification", "data_flows", "boundary_description"],
    "DC-1.6": ["incident_response_procedures", "change_management_procedures"],
    "DC-1.7": ["monitoring_tools", "reporting_frequency"],
    "DC-2.1": ["boundary_description", "scope_definition"],
    "DC-2.2": ["system_description", "service_catalog"],
    "DC-3.1": ["subservice_organizations", "reporting_method"],
    "DC-3.2": ["user_entity_controls"],
    "DC-4.1": ["service_commitments", "sla_documentation"],
    "DC-4.2": ["availability_requirements", "security_requirements", "confidentiality_requirements"],
    "DC-5.1": ["control_matrix", "risk_to_control_mapping"],
    "DC-6.1": ["system_changes", "change_log"],
    "DC-7.1": [],
}

DC_SECTION_200: Dict[str, Dict[str, Any]] = {
    _cid: {
        "title": dc_title(_cid),
        "description": dc_description(_cid),
        "wizard_fields": _DC_WIZARD_FIELDS.get(_cid, []),
        "required": dc_required(_cid),
    }
    for _cid in DC_CRITERIA
}

def dc_200_coverage(org_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate DC Section 200 coverage based on org profile fields."""
    covered = 0
    total = len(DC_SECTION_200)
    details: List[Dict[str, Any]] = []
    for dc_id, dc_meta in DC_SECTION_200.items():
        filled = sum(1 for f in dc_meta["wizard_fields"] if (org_profile.get(f) or "").strip())
        fields_total = len(dc_meta["wizard_fields"])
        is_covered = filled > 0 if dc_meta["required"] else True
        if is_covered:
            covered += 1
        details.append({
            "dc_id": dc_id,
            "title": dc_meta["title"],
            "required": dc_meta["required"],
            "filled": filled,
            "fields_total": fields_total,
            "covered": is_covered,
        })
    return {
        "dc_200_total": total,
        "dc_200_covered": covered,
        "dc_200_pct": round((covered / total) * 100) if total else 0,
        "dc_200_details": details,
    }


def generate_system_description(ws: Dict[str, Any]) -> str:
    """Markdown system description from workspace narratives and readiness."""
    dash = compute_dashboard(ws)
    org = ws.get("org_name") or "Organization"
    org_profile = ws.get("org_profile") or {}
    scope = ws.get("tsc_scope") or DEFAULT_SCOPE
    in_scope = get_in_scope_controls(scope)
    periods = list_audit_periods(ws)
    frozen = next((p for p in periods if p.get("frozen")), None)
    active = next((p for p in periods if not p.get("frozen")), None)
    dc = dc_200_coverage(org_profile)

    lines: List[str] = [
        f"# SOC 2 System Description — {org}",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Executive summary",
        "",
        f"- **Readiness:** {dash['readiness_pct']}% ({dash['controls_met']}/{dash['controls_total']} criteria met)",
        f"- **Evidence coverage:** {dash['evidence_coverage_pct']}%",
        f"- **Auto-collected coverage:** {dash['auto_coverage_pct']}%",
        f"- **Open gaps:** {dash['open_gaps']}",
        f"- **DC Section 200 coverage:** {dc['dc_200_pct']}% ({dc['dc_200_covered']}/{dc['dc_200_total']} description criteria)",
        "",
    ]

    if active:
        lines.extend([
            f"**Active audit period:** {active['name']} ({active['start_date']} → {active['end_date']})",
            "",
        ])
    if frozen:
        lines.extend([
            f"**Frozen audit period:** {frozen['name']} (locked {frozen.get('frozen_at') or '—'})",
            "",
        ])

    engagement = ws.get("soc2_engagement") or {}
    if engagement.get("type") or engagement.get("firm"):
        type_label = {"type1": "Type I", "type2": "Type II"}.get(engagement.get("type"), engagement.get("type") or "—")
        lines.extend([
            f"**Engagement:** {type_label} report",
            f"- **CPA firm:** {engagement.get('firm') or '—'}",
            f"- **CPA contact:** {engagement.get('cpa_contact') or '—'}",
            f"- **Engagement window:** "
            f"{engagement.get('engagement_start') or '—'} → {engagement.get('engagement_end') or '—'}",
            f"- **Engagement status:** {engagement.get('status') or '—'}",
            "",
        ])

    by_category: Dict[str, List[str]] = {}
    for cid, meta in in_scope.items():
        cat = meta["category"]
        by_category.setdefault(cat, []).append(cid)

    for category in sorted(by_category.keys()):
        lines.extend([f"## {category}", ""])
        for cid in by_category[category]:
            meta = in_scope[cid]
            ans = ws["answers"].get(cid, default_control_answer())
            status = ans.get("status", "NOT STARTED")
            narrative = (ans.get("implementation_narrative") or "").strip()
            evidence = ans.get("evidence") or []
            lines.append(f"### {cid} — {meta['title']}")
            lines.append("")
            lines.append(f"**Status:** {status}  ")
            lines.append(f"**Evidence items:** {len(evidence)}")
            if ans.get("owner"):
                lines.append(f"**Owner:** {ans['owner']}")
            if ans.get("target_date"):
                lines.append(f"**Target date:** {ans['target_date']}")
            lines.append("")
            lines.append(meta["description"])
            lines.append("")
            if narrative:
                lines.append("**Implementation narrative:**")
                lines.append("")
                lines.append(narrative)
                lines.append("")
            elif status not in ("NOT STARTED",):
                lines.append("*No implementation narrative recorded.*")
                lines.append("")
            if ans.get("operating_status") and ans["operating_status"] != "NOT TESTED":
                lines.append(f"**Operating effectiveness:** {ans['operating_status']}  ")
            if ans.get("frequency"):
                lines.append(f"**Frequency:** {ans['frequency']}  ")
            lrd = ans.get("last_review_date") or ""
            nrd = ans.get("next_review_date") or ""
            if lrd or nrd:
                parts = []
                if lrd: parts.append(f"Last review: {lrd}")
                if nrd: parts.append(f"Next review: {nrd}")
                lines.append(f"**{' / '.join(parts)}**  ")
            linked_policies = ans.get("linked_policies") or []
            if linked_policies:
                lines.append("**Linked policies:**  ")
                for p in linked_policies:
                    title = p.get("title", "?")
                    ver = p.get("version", "?")
                    lines.append(f"- {title} (v{ver})  ")
                lines.append("")
            linked_assets = ans.get("linked_assets") or []
            if linked_assets:
                lines.append("**Linked assets:**  ")
                for a in linked_assets:
                    name = a.get("name") or a.get("asset_name", "?")
                    atype = a.get("type") or a.get("asset_type", "?")
                    lines.append(f"- {name} ({atype})  ")
                lines.append("")
            linked_team = ans.get("linked_team") or []
            if linked_team:
                lines.append(f"**Linked team:** {', '.join(t if isinstance(t, str) else t.get('name', str(t)) for t in linked_team)}  ")
                lines.append("")
            if ans.get("remediation_plan") and status in ("NOT MET", "IN PROGRESS", "PLANNED"):
                lines.append("**Remediation plan:**")
                lines.append("")
                lines.append(ans["remediation_plan"])
                lines.append("")
            lines.append("---")
            lines.append("")

    # ── Complementary Controls ────────────────────────────────
    org_profile = ws.get("org_profile") or {}
    subservice = (org_profile.get("subservice_organizations") or "").strip()
    reporting = (org_profile.get("reporting_method") or "").strip()
    cuec = (org_profile.get("user_entity_controls") or "").strip()
    if subservice or reporting:
        lines.extend([
            "## Complementary Subservice Organization Controls (CSOC)",
            "",
        ])
        if reporting:
            lines.append(f"**Reporting method:** {reporting}")
            lines.append("")
        if subservice:
            lines.append("**Subservice organizations:**")
            lines.append("")
            lines.append(subservice)
            lines.append("")
        lines.append("---")
        lines.append("")
    if cuec:
        lines.extend([
            "## Complementary User Entity Controls (CUEC)",
            "",
            "The following controls are responsibilities of the user entity:",
            "",
            cuec,
            "",
            "---",
            "",
        ])

    # ── DC Section 200 Coverage ──────────────────────────────────
    lines.extend([
        "## Description Criteria (DC Section 200) Coverage",
        "",
        "The following table maps the system description to AICPA DC Section 200 criteria.",
        "",
    ])
    for d in dc["dc_200_details"]:
        icon = "✅" if d["covered"] else "⬜"
        req = "Required" if d["required"] else "Recommended"
        lines.append(f"- {icon} **{d['dc_id']}** — {d['title']} ({req})  ")
        if d["filled"] < d["fields_total"]:
            lines.append(f"  - *{d['filled']}/{d['fields_total']} fields populated*  ")
        lines.append("")
    lines.append("---")
    lines.append("")

    lines.extend([
        "## Disclaimer",
        "",
        "This document is generated from Khestra workspace data. It does not constitute a SOC 2 report "
        "or auditor opinion. Review all narratives and evidence before auditor handoff.",
        "",
    ])
    return "\n".join(lines)
