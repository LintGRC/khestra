from controls import CMMC_FRAMEWORK

from ssp.utils import add_placeholder


def add_executive_summary(
    doc,
    answers: dict,
    asset_scope: dict,
    scoped_controls: list,
    org_profile: dict | None = None,
    sprs_result: dict | None = None,
) -> None:
    profile = org_profile or {}
    org_name = profile.get("org_name") or "the organization"
    system_name = profile.get("system_name") or "CMMC Level 2 assessment system"

    doc.add_heading("1. Executive Summary", level=1)

    scoped = [cid for cid in scoped_controls if cid in answers]
    total_controls = len(scoped)
    met_count = sum(1 for cid in scoped if answers[cid].get("status") == "MET")
    readiness_pct = round((met_count / total_controls) * 100, 1) if total_controls else 0
    sprs_score = sprs_result["final_score"] if sprs_result else "N/A"

    doc.add_paragraph(
        f"This System Security Plan (SSP) documents the security posture of {org_name}'s "
        f"{system_name}. As of the preparation date, the organization reports a Supplier "
        f"Performance Risk System (SPRS) score of {sprs_score}/110 with {readiness_pct}% "
        f"of scoped controls marked MET ({met_count} of {total_controls})."
    )

    if profile.get("system_description", "").strip():
        doc.add_paragraph(profile["system_description"].strip())

    cui_level = asset_scope.get("CUI Assets", 0)
    if cui_level > 0:
        doc.add_paragraph(
            f"The system processes Controlled Unclassified Information (CUI) at {cui_level}% capacity, "
            f"requiring full implementation of applicable NIST SP 800-171 Rev 2 controls."
        )
    else:
        doc.add_paragraph(
            "The system has been scoped to exclude CUI processing, reducing the applicable control set."
        )

    critical_gaps = [
        cid
        for cid in scoped
        if answers[cid].get("status") not in ("MET", "NOT APPLICABLE", "INHERITED")
        and CMMC_FRAMEWORK[cid]["weight"] >= 5
    ]
    if critical_gaps:
        sample = ", ".join(critical_gaps[:3])
        suffix = " and others" if len(critical_gaps) > 3 else ""
        doc.add_paragraph(
            f"There are {len(critical_gaps)} critical security gaps identified. "
            f"Examples: {sample}{suffix}."
        )
    else:
        doc.add_paragraph(
            "No critical security gaps have been identified among scoped high-impact controls."
        )

    doc.add_page_break()
