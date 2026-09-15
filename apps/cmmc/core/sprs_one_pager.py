"""Print-friendly SPRS one-pager for management review and PIEE prep."""

from datetime import datetime
from typing import Any, Dict, List

from controls import CMMC_FRAMEWORK


def build_sprs_one_pager(
    org_profile: Dict[str, str],
    sprs_result: Dict[str, Any],
    scoped_controls: List[str],
    answers: Dict[str, Any],
    width: int = 72,
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
    score = sprs_result.get("final_score", "N/A")
    breakdown = sprs_result.get("breakdown", {})
    today = datetime.now().strftime("%Y-%m-%d")
    met = sum(1 for c in scoped_controls if answers.get(c, {}).get("status") == "MET")
    gaps = breakdown.get("total_gaps_count", 0)

    def line(char: str = "-") -> str:
        return char * width

    def wrap(text: str, indent: int = 0) -> List[str]:
        words = text.split()
        lines: List[str] = []
        current = " " * indent
        for w in words:
            if len(current) + len(w) + 1 > width:
                lines.append(current.rstrip())
                current = " " * indent + w + " "
            else:
                current += w + " "
        if current.strip():
            lines.append(current.rstrip())
        return lines or [""]

    out: List[str] = [
        line("="),
        "SPRS ASSESSMENT ONE-PAGER".center(width),
        line("="),
        "",
        f"Organization:  {org}",
        f"System:        {system}",
        f"Date:          {today}",
        f"CAGE Code:     {cage}",
        f"UEI:           {uei}",
        f"Methodology:   {methodology}",
        f"Framework:     NIST SP 800-171 Rev 2 (CMMC Level 2)",
        "",
    ]
    if poc_parts:
        out.append(f"POC:           {' | '.join(poc_parts)}")
        out.append("")
    out.extend([
        line(),
        "SCORE SUMMARY",
        line(),
        f"  SPRS score:           {score} / 110",
        f"  Controls MET:         {met} / {len(scoped_controls)}",
        f"  Open gaps:            {gaps}",
        f"  5-point gaps:         {sprs_result.get('penalties', {}).get('5pt', 0)}",
        f"  3-point gaps:         {sprs_result.get('penalties', {}).get('3pt', 0)}",
        f"  1-point gaps:         {sprs_result.get('penalties', {}).get('1pt', 0)}",
        "",
    ])

    critical = sprs_result.get("critical_gaps") or []
    if critical:
        out.extend([line(), "TOP PRIORITY GAPS (5-POINT)", line()])
        for cid in critical[:8]:
            status = answers.get(cid, {}).get("status", "N/A")
            name = CMMC_FRAMEWORK[cid]["name"]
            out.append(f"  {cid}  [{status}]")
            for wl in wrap(name, indent=4):
                out.append(wl)
        if len(critical) > 8:
            out.append(f"  … and {len(critical) - 8} more")
        out.append("")

    out.extend(
        [
            line(),
            "BEFORE YOU SUBMIT",
            line(),
            "  [ ] Review SSP and POA&M exports for accuracy",
            "  [ ] Verify SPRS score against DoW methodology",
            "  [ ] Enter score manually in PIEE (no API from this tool)",
            "  [ ] Retain assessment records with your SSP",
            "",
            line(),
            "Draft generated locally — not an official submission.",
            f"CMMC assessment tool · {today}",
            line("="),
        ]
    )
    return "\n".join(out)
