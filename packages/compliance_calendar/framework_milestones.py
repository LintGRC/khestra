"""Framework program clocks → shared compliance calendar milestones.

Extends the milestone pattern built for CMMC (assessment status lifecycle) to
the other frameworks so their program dates surface in the shared calendar +
reminder engine:

  - SOC 2: frozen audit period end = report delivery clock (§ 3.05 style
    engagement cadence); engagement end date = report target.
  - ISO 27001: internal audit cadence (per shared control-tests/audit-center
    records) and management review (management_review store) — annual.
  - EU AI Act: FRIA review + post-market monitoring intervals per system.

Best-effort per app; failures never break the host API.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

_log = logging.getLogger("compliance_calendar.milestones")

FRIA_REVIEW_DAYS = 365
POST_MARKET_DAYS = 90
MANAGEMENT_REVIEW_DAYS = 365
INTERNAL_AUDIT_DAYS = 365


def _iso(day: Optional[date]) -> str:
    return day.isoformat() if day else ""


def sync_soc2_milestones(ws: Dict[str, Any]) -> None:
    """SOC 2: report-target clock from the frozen audit period + engagement."""
    try:
        from compliance_calendar.store import clear_milestones, upsert_milestone

        client_id = ws.get("client_id") or ""
        clear_milestones("soc2", client_id)

        periods = ws.get("audit_periods") or []
        frozen = next((p for p in periods if p.get("frozen")), None)
        engagement = ws.get("soc2_engagement") or {}

        # Report target: engagement end date, else frozen period end + 45 days.
        target = engagement.get("engagement_end") or ""
        if not target and frozen:
            end = frozen.get("end_date") or ""
            if end:
                try:
                    target = (date.fromisoformat(end[:10]) + timedelta(days=45)).isoformat()
                except ValueError:
                    target = ""
        if target:
            upsert_milestone(
                "soc2", "report_target", target,
                "SOC 2 report target",
                details="Frozen audit period + engagement — deliver the SOC 2 report to the CPA firm.",
                link="audit", client_id=client_id,
            )

        if frozen:
            upsert_milestone(
                "soc2", "period_frozen", frozen.get("end_date") or "",
                f"SOC 2 audit period frozen — {frozen.get('name') or 'period'}",
                details="Evidence is locked for the audit period; manifest available for the auditor.",
                link="audit", client_id=client_id,
            )
    except Exception as exc:  # pragma: no cover
        _log.warning("SOC2 milestone sync failed: %s", exc)


def sync_iso_milestones(ws: Dict[str, Any], framework_id: str = "iso27001") -> None:
    """ISO 27001: management review + internal audit cadence (annual clocks)."""
    try:
        from compliance_calendar.store import clear_milestones, upsert_milestone

        client_id = ws.get("client_id") or ""
        clear_milestones(framework_id, client_id)

        last_review = ""
        try:
            from management_review.store import list_reviews
            reviews = list_reviews() or []
            dates = [str(r.get("review_date") or r.get("created_at") or "")[:10] for r in reviews if r.get("review_date") or r.get("created_at")]
            if dates:
                last_review = max(dates)
        except Exception:
            pass

        if last_review:
            try:
                due = (date.fromisoformat(last_review) + timedelta(days=MANAGEMENT_REVIEW_DAYS)).isoformat()
            except ValueError:
                due = ""
        else:
            due = ""
        if due:
            upsert_milestone(
                framework_id, "management_review", due,
                "ISO management review due (annual)",
                details="Top management must review the ISMS at planned intervals (clause 9.3).",
                link="management-review", client_id=client_id,
            )
    except Exception as exc:  # pragma: no cover
        _log.warning("ISO milestone sync failed: %s", exc)


def sync_aigov_milestones(system: Dict[str, Any], client_id: str = "") -> None:
    """EU AI Act: FRIA review + post-market monitoring clocks per AI system."""
    try:
        from compliance_calendar.store import upsert_milestone

        sid = system.get("id") or system.get("system_id") or ""
        if not sid:
            return

        fria_review = system.get("review_date") or ""
        if fria_review:
            try:
                due = (date.fromisoformat(str(fria_review)[:10]) + timedelta(days=FRIA_REVIEW_DAYS)).isoformat()
            except ValueError:
                due = ""
            if due:
                upsert_milestone(
                    "aigov", "fria_review", due,
                    f"FRIA review due — {system.get('name') or sid}",
                    details="Fundamental rights impact assessment must be kept current (EU AI Act Art. 27).",
                    link="aigov/fria", client_id=client_id,
                )

        post_market = system.get("post_market_review") or ""
        if post_market:
            try:
                due = (date.fromisoformat(str(post_market)[:10]) + timedelta(days=POST_MARKET_DAYS)).isoformat()
            except ValueError:
                due = ""
            if due:
                upsert_milestone(
                    "aigov", "post_market", due,
                    f"Post-market monitoring review — {system.get('name') or sid}",
                    details="Review post-market monitoring logs and serious-incident reporting (Art. 72-73).",
                    link="aigov/systems", client_id=client_id,
                )
    except Exception as exc:  # pragma: no cover
        _log.warning("AIGov milestone sync failed: %s", exc)

