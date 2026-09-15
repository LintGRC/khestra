"""SPRS / PIEE manual entry summary (no API — copy/paste handoff)."""

from datetime import datetime
from typing import Any, Dict, List, Optional


def build_sprs_entry_summary(
    org_profile: Dict[str, str],
    sprs_result: Dict[str, Any],
    scoped_controls: List[str],
    asset_scope: Dict[str, Any],
    cmmc_assessment: Optional[Dict[str, Any]] = None,
    cmmc_scope: Optional[Dict[str, Any]] = None,
) -> str:
    org = org_profile.get("org_name") or "Organization"
    system = org_profile.get("system_name") or "Information System"
    cage = org_profile.get("cage_code") or ""
    uei = org_profile.get("uei") or ""
    methodology = org_profile.get("assessment_methodology") or "Basic"
    poc_name = org_profile.get("poc_name") or ""
    poc_email = org_profile.get("poc_email") or ""
    poc_phone = org_profile.get("poc_phone") or ""
    poc_parts = [p for p in [poc_name, poc_email, poc_phone] if p]
    poc_line = f"  POC:                      {' | '.join(poc_parts)}" if poc_parts else ""
    score = sprs_result.get("final_score", "N/A")
    gaps = sprs_result.get("breakdown", {}).get("total_gaps_count", 0)
    critical = len(sprs_result.get("critical_gaps", []))
    today = datetime.now().strftime("%Y-%m-%d")
    cui_pct = asset_scope.get("CUI Assets", 0)

    assessment = cmmc_assessment or {}
    assessment_type = assessment.get("assessment_type") or ""
    status = (assessment.get("status") or "").lower()
    status_date = (assessment.get("status_date") or "").strip() or today
    type_label = {
        "level1_self": "Level 1 (Self)",
        "level2_self": "Level 2 (Self)",
        "level2_c3pao": "Level 2 (C3PAO)",
    }.get(assessment_type, assessment_type or "Not declared")
    status_label = {"conditional": "Conditional", "final": "Final"}.get(status, status.title() if status else "None")
    poam_status = "In use (Conditional)" if status == "conditional" else ("None" if status == "final" else "Not declared")

    scope_rec = cmmc_scope or {}
    esp_line = ""
    if scope_rec.get("esp") == "yes":
        esp_line = (
            f"  ESP in scope:            Yes — {scope_rec.get('esp_name') or '(name not set)'}"
            + (f" at {scope_rec.get('esp_facilities')}" if scope_rec.get("esp_facilities") else "")
        )
    elif scope_rec.get("esp") == "no":
        esp_line = "  ESP in scope:            No"
    facilities_line = f"  Facilities:              {scope_rec.get('facilities') or '(not set)'}"
    scope_statement_line = f"  Scope statement:         {scope_rec.get('scope_statement') or '(not set)'}"

    lines = [
        "SPRS ENTRY SUMMARY (Manual PIEE Submission)",
        "=" * 50,
        "",
        "Use this summary when entering your NIST SP 800-171 basic assessment in PIEE.",
        "The tool does NOT submit to PIEE — copy these values into the portal.",
        "",
        "CMMC ASSESSMENT (32 CFR Part 170)",
        f"  CMMC Level:                {type_label}",
        f"  CMMC Status:               {status_label}",
        f"  CMMC Status Date:          {status_date}",
        f"  Assessment scope:          {len(scoped_controls)} of 110 controls in scope; "
        f"{cui_pct}% of assets classified as CUI",
        f"  POA&M usage / compliance:  {poam_status}",
        f"  Affirming Official:        {assessment.get('affirming_official') or '(not set)'}",
        "",
        "ORGANIZATION",
        f"  Contractor / Org name:     {org}",
        f"  System name:               {system}",
        f"  CAGE Code:                 {cage if cage else '(not set)'}",
        f"  UEI:                       {uei if uei else '(not set)'}",
        f"  Assessment methodology:    {methodology}",
        poc_line,
        "",
        "SCORE (DoW Assessment Methodology — Rev 2)",
        f"  SPRS score:                {score} / 110",
        f"  Open gaps (scoped):        {gaps}",
        f"  Critical gaps (5-pt):      {critical}",
        "",
        "SCOPE",
        f"  CUI in scope:              {cui_pct}% of assets classified as CUI",
        f"  Controls in scope:         {len(scoped_controls)} of 110",
        esp_line,
        facilities_line,
        scope_statement_line,
        "",
        "PIEE ENTRY CHECKLIST",
        "  [ ] Log in to PIEE (https://piee.eb.mil)",
        "  [ ] Navigate to SPRS / NIST SP 800-171 basic assessment",
        "  [ ] Enter CMMC Level, Status Date, and Assessment Scope shown above",
        "  [ ] Enter assessment score shown above",
        "  [ ] Confirm POA&M usage / compliance status shown above",
        "  [ ] Confirm system scope description matches your SSP",
        "  [ ] Retain SSP and POA&M exports with this summary for records",
        "  [ ] Affirming Official affirms compliance in SPRS (annually)",
        "",
        "NOTES",
        "  - SSP .docx export supports C3PAO / audit preparation; it is not uploaded",
        "    to PIEE in the standard basic assessment flow.",
        "  - Verify score against DoW calculator before official submission.",
        "  - False Claims Act applies to inaccurate submissions.",
        "",
        f"Generated by CMMC local assessment tool on {today}.",
    ]
    return "\n".join(lines)
