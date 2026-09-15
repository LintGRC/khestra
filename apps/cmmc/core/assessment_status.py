"""CMMC assessment status lifecycle — 32 CFR Part 170.

Tracks the CMMC Status per client workspace: assessment type (Level 1 Self /
Level 2 Self / Level 2 C3PAO), Conditional vs Final status, the CMMC Status
Date, and the three program clocks that derive from it:

  - 180-day POA&M closeout clock  (§ 170.16(b)) — Conditional status expires
    if NOT MET requirements are not remediated + closeout self-assessment
    posted to SPRS within 180 days of the Status Date.
  - 3-year reassessment cycle      (§ 170.16(a)) — re-assess and re-post to
    SPRS within three years.
  - Annual affirmation             (§ 170.22)    — Affirming Official affirms
    continuing compliance after every assessment/closeout and annually.

Pure CMMC business logic — lives in the cmmc app, not the shared tier.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

from poam_eligibility import POAM_CLOSEOUT_DAYS, poam_eligibility
from poam_export import poam_gap_controls
from sprs_engine import calculate_detailed_sprs

_log = logging.getLogger("cmmc.assessment_status")

ASSESSMENT_TYPES = frozenset({"level1_self", "level2_self", "level2_c3pao"})
ASSESSMENT_TYPE_LABELS = {
    "level1_self": "Level 1 (Self)",
    "level2_self": "Level 2 (Self)",
    "level2_c3pao": "Level 2 (C3PAO)",
}
STATUS_VALUES = frozenset({"conditional", "final"})

REASSESSMENT_YEARS = 3
AFFIRMATION_YEARS = 1

EMPTY_ASSESSMENT: Dict[str, Any] = {
    "assessment_type": "",
    "status": "",
    "status_date": "",
    "affirming_official": "",
    "affirmed_at": "",
}


def merge_assessment(saved: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize a persisted assessment block; never fail on legacy data."""
    src = saved or {}
    out = dict(EMPTY_ASSESSMENT)
    for key in EMPTY_ASSESSMENT:
        val = src.get(key)
        if isinstance(val, str):
            out[key] = val.strip()
        elif val:
            out[key] = val
    return out


def _parse_day(value: str) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _iso(day: Optional[date]) -> str:
    return day.isoformat() if day else ""


def _days_until(day: Optional[date]) -> Optional[int]:
    if day is None:
        return None
    return (day - date.today()).days


def build_assessment_status(ws: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve the assessment status record + derived program clocks."""
    assessment = merge_assessment(ws.get("cmmc_assessment"))
    answers = ws.get("answers") or {}
    scoped = ws.get("scoped_controls") or []

    status_date = _parse_day(assessment.get("status_date"))
    status = assessment.get("status") or ""
    assessment_type = assessment.get("assessment_type") or ""

    gaps = poam_gap_controls(answers, scoped)
    sprs = calculate_detailed_sprs(answers, scoped)
    eligibility = poam_eligibility(answers, scoped)

    closeout_due = None
    if status == "conditional" and status_date:
        closeout_due = status_date + timedelta(days=POAM_CLOSEOUT_DAYS)
    reassessment_due = status_date + timedelta(days=365 * REASSESSMENT_YEARS) if status_date else None
    affirmation_due = status_date + timedelta(days=365 * AFFIRMATION_YEARS) if status_date else None

    today = date.today()
    closeout_days_left = _days_until(closeout_due) if closeout_due else None
    return {
        "assessment_type": assessment_type,
        "assessment_type_label": ASSESSMENT_TYPE_LABELS.get(assessment_type, ""),
        "status": status,
        "status_date": assessment.get("status_date"),
        "affirming_official": assessment.get("affirming_official"),
        "affirmed_at": assessment.get("affirmed_at"),
        "sprs_score": sprs["final_score"],
        "sprs_max": 110,
        "gap_count": len(gaps),
        "poam_eligible": bool(eligibility.get("eligible")),
        "poam_blocking": eligibility.get("blocking_ids") or [],
        "closeout_due": _iso(closeout_due),
        "closeout_days_left": closeout_days_left,
        "closeout_expired": bool(closeout_due and closeout_due < today),
        "reassessment_due": _iso(reassessment_due),
        "reassessment_days_left": _days_until(reassessment_due),
        "reassessment_expired": bool(reassessment_due and reassessment_due < today),
        "affirmation_due": _iso(affirmation_due),
        "affirmation_days_left": _days_until(affirmation_due),
        "affirmation_expired": bool(affirmation_due and affirmation_due < today),
    }


def sync_milestones(ws: Dict[str, Any]) -> None:
    """Write program milestones to the shared compliance calendar store.

    32 CFR 170 clocks: 180-day POA&M closeout (conditional), 3-year
    reassessment, annual affirmation. Best-effort — reminder failures must
    never break the status API.
    """
    try:
        from compliance_calendar.store import clear_milestones, upsert_milestone

        client_id = ws.get("client_id") or ""
        clear_milestones("cmmc", client_id)
        status = build_assessment_status(ws)
        if not status["status"]:
            return

        if status["closeout_due"]:
            upsert_milestone(
                "cmmc", "poam_closeout", status["closeout_due"],
                "CMMC POA&M closeout due",
                details=f"Conditional Level 2 status expires if NOT MET requirements are not remediated "
                        f"and a closeout self-assessment posted to SPRS within 180 days of the Status Date.",
                link="poam", client_id=client_id,
            )
        if status["reassessment_due"]:
            upsert_milestone(
                "cmmc", "reassessment", status["reassessment_due"],
                "CMMC reassessment due (3-year cycle)",
                details=f"Re-conduct the {status['assessment_type_label'] or 'CMMC'} assessment and "
                        f"post results to SPRS within three years of the Status Date.",
                link="readiness", client_id=client_id,
            )
        if status["affirmation_due"]:
            upsert_milestone(
                "cmmc", "affirmation", status["affirmation_due"],
                "CMMC annual affirmation due",
                details=f"Affirming Official must affirm continuing compliance with the "
                        f"{status['assessment_type_label'] or 'CMMC'} status annually.",
                link="organization", client_id=client_id,
            )
    except Exception as exc:  # pragma: no cover — best effort
        _log.warning("compliance calendar milestone sync failed: %s", exc)


def apply_assessment_status(
    ws: Dict[str, Any],
    *,
    assessment_type: str,
    status: str,
    status_date: str,
    affirming_official: str = "",
) -> Dict[str, Any]:
    """Validate and persist an assessment status update (32 CFR 170.15-17, 170.22)."""
    assessment_type = (assessment_type or "").strip()
    status = (status or "").strip().lower()
    status_date = (status_date or "").strip()[:10]

    if assessment_type and assessment_type not in ASSESSMENT_TYPES:
        raise ValueError(f"Unknown assessment type: {assessment_type}")
    if status and status not in STATUS_VALUES:
        raise ValueError(f"Unknown status: {status}")

    if status:
        if not assessment_type:
            raise ValueError("Assessment type is required when setting a status")
        if not _parse_day(status_date):
            raise ValueError("CMMC Status Date is required when setting a status")

    gaps = poam_gap_controls(ws.get("answers") or {}, ws.get("scoped_controls") or [])
    if status == "final" and gaps:
        raise ValueError(
            f"Final status requires all {len(gaps)} NOT MET requirement(s) to be remediated — "
            "use Conditional with a POA&M, or complete the closeout."
        )
    if status == "conditional":
        eligibility = poam_eligibility(ws.get("answers") or {}, ws.get("scoped_controls") or [])
        if not eligibility.get("eligible"):
            blocking = ", ".join(eligibility.get("blocking_ids") or [])
            reason = (
                f"SPRS {eligibility['score']} is below the {eligibility['threshold']} threshold"
                if eligibility["score"] < eligibility["threshold"]
                else f"not POA&M-eligible: {blocking}"
            )
            raise ValueError(f"Conditional status not available — {reason}")

    current = merge_assessment(ws.get("cmmc_assessment"))
    current.update(
        {
            "assessment_type": assessment_type,
            "status": status,
            "status_date": status_date,
            "affirming_official": (affirming_official or "").strip(),
        }
    )
    ws["cmmc_assessment"] = current
    sync_milestones(ws)
    return build_assessment_status(ws)


def complete_closeout(ws: Dict[str, Any]) -> Dict[str, Any]:
    """POA&M closeout (§ 170.16(b)) — promote Conditional to Final when gaps are remediated."""
    current = merge_assessment(ws.get("cmmc_assessment"))
    if current.get("status") != "conditional":
        raise ValueError("Closeout is only available for Conditional status")

    gaps = poam_gap_controls(ws.get("answers") or {}, ws.get("scoped_controls") or [])
    if gaps:
        raise ValueError(
            f"Closeout requires all NOT MET requirements remediated — {len(gaps)} still open: "
            + ", ".join(gaps[:8])
        )

    today = date.today().isoformat()
    current["status"] = "final"
    current["affirmed_at"] = today
    ws["cmmc_assessment"] = current
    sync_milestones(ws)
    return build_assessment_status(ws)
