"""Evidence coverage by family and composite readiness scores."""

from __future__ import annotations

from typing import Any, Dict, List

from controls import CMMC_FRAMEWORK
from report_readiness import evaluate_report_readiness
from ssp.constants import FAMILY_ORDER

FAMILY_CODE = {
    "Access Control": "AC",
    "Awareness and Training": "AT",
    "Audit and Accountability": "AU",
    "Configuration Management": "CM",
    "Identification and Authentication": "IA",
    "Incident Response": "IR",
    "Maintenance": "MA",
    "Media Protection": "MP",
    "Personnel Security": "PS",
    "Physical Protection": "PE",
    "Risk Assessment": "RA",
    "Security Assessment": "CA",
    "System and Communications Protection": "SC",
    "System and Information Integrity": "SI",
}


def _has_evidence_or_examine(ans: dict) -> bool:
    return bool(ans.get("evidence")) or bool((ans.get("examine") or "").strip())


def compute_evidence_coverage(
    answers: Dict[str, Any],
    scoped_controls: List[str],
) -> Dict[str, Any]:
    """Family-level evidence coverage for MET controls in scope."""
    families: Dict[str, Dict[str, Any]] = {}
    met_total = 0
    with_evidence_total = 0
    files_total = 0
    assessment_ready: Dict[str, bool] = {}

    for cid in scoped_controls:
        if cid not in CMMC_FRAMEWORK:
            continue
        fam = CMMC_FRAMEWORK[cid]["family"]
        row = families.setdefault(
            fam,
            {
                "family": fam,
                "code": FAMILY_CODE.get(fam, fam[:2].upper()),
                "scoped": 0,
                "met": 0,
                "with_evidence": 0,
                "without_evidence": 0,
                "weak_ids": [],
            },
        )
        row["scoped"] += 1
        ans = answers.get(cid, {})
        status = ans.get("status", "NOT STARTED")
        if status != "MET":
            assessment_ready[cid] = False
            continue
        row["met"] += 1
        met_total += 1
        files_total += len(ans.get("evidence") or [])
        has_evidence = _has_evidence_or_examine(ans)
        assessment_ready[cid] = has_evidence
        if has_evidence:
            row["with_evidence"] += 1
            with_evidence_total += 1
        else:
            row["without_evidence"] += 1
            if len(row["weak_ids"]) < 5:
                row["weak_ids"].append(cid)

    family_rows: List[Dict[str, Any]] = []
    for fam in FAMILY_ORDER:
        row = families.get(fam)
        if not row or row["scoped"] == 0:
            continue
        met = row["met"]
        if met:
            row["evidence_pct"] = round(100 * row["with_evidence"] / met)
        else:
            row["evidence_pct"] = None
        row["controls_label"] = f"{row['met']}/{row['scoped']}"
        family_rows.append(row)

    evidence_pct = round(100 * with_evidence_total / met_total) if met_total else 0

    weak_families = sorted(
        [r for r in family_rows if r["met"] and (r["evidence_pct"] or 0) < 50],
        key=lambda r: (r["evidence_pct"] or 0, -r["met"]),
    )

    return {
        "met_count": met_total,
        "with_evidence_count": with_evidence_total,
        "without_evidence_count": met_total - with_evidence_total,
        "assessment_ready_count": with_evidence_total,
        "assessment_ready": assessment_ready,
        "evidence_pct": evidence_pct,
        "evidence_files_count": files_total,
        "families": family_rows,
        "weak_families": weak_families,
    }


def compute_readiness_scores(
    answers: Dict[str, Any],
    org_profile: Dict[str, str],
    scoped_controls: List[str],
) -> Dict[str, Any]:
    """Assessment, documentation, and evidence readiness — not compliance."""
    report = evaluate_report_readiness(answers, org_profile, scoped_controls)
    evidence = compute_evidence_coverage(answers, scoped_controls)

    assessment = report["assessment_score"]
    documentation = report["narrative_score"]
    evidence_score = evidence["evidence_pct"]

    audit_readiness = round(
        assessment * 0.30 + documentation * 0.35 + evidence_score * 0.35
    )

    return {
        "assessment_readiness": assessment,
        "documentation_readiness": documentation,
        "evidence_readiness": evidence_score,
        "audit_readiness": audit_readiness,
        "profile_score": report["profile_score"],
        "export_readiness": report["score"],
        "evidence_detail": evidence,
    }


def format_evidence_coverage_report(
    coverage: Dict[str, Any],
    scores: Dict[str, Any],
    org_name: str = "",
) -> str:
    lines = [
        f"Evidence Coverage & Readiness — {org_name or 'Organization'}",
        "",
        f"Assessment readiness: {scores['assessment_readiness']}%",
        f"Documentation readiness: {scores['documentation_readiness']}%",
        f"Evidence readiness: {scores['evidence_readiness']}%",
        f"Audit readiness (composite): {scores['audit_readiness']}%",
        "",
        f"MET controls: {coverage['met_count']}",
        f"With evidence or examine ref: {coverage['with_evidence_count']}",
        f"Missing support: {coverage['without_evidence_count']}",
        f"Evidence files attached: {coverage['evidence_files_count']}",
        "",
        "BY FAMILY (MET controls in scope)",
    ]
    for row in coverage["families"]:
        pct = row["evidence_pct"]
        pct_label = f"{pct}%" if pct is not None else "n/a"
        lines.append(
            f"  {row['code']:3} | {row['met']}/{row['scoped']} MET | "
            f"evidence {row['with_evidence']}/{row['met'] or 0} | {pct_label}"
        )
    if coverage["weak_families"]:
        lines.extend(["", "WEAKEST FAMILIES (<50% evidence on MET)"])
        for row in coverage["weak_families"][:8]:
            lines.append(f"  {row['code']} — {row['evidence_pct']}% ({row['with_evidence']}/{row['met']} MET)")
    return "\n".join(lines)
