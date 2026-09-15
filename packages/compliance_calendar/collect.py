"""Compliance calendar aggregation — shared across apps.

Collects due/overdue compliance items from the shared stores:
policy reviews, evidence requests, expiring/stale evidence, and risk
reviews. Deterministic — no LLM, no stochastic scoring.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

ITEM_TYPES = ("policy_review", "evidence_request", "evidence_expiring", "risk_review", "acceptance_expiry", "control_test", "poam_closeout", "reassessment", "affirmation", "report_target", "period_frozen", "management_review", "fria_review", "post_market")


def _day(value: str) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (ValueError, IndexError):
        return None


def _iso(d: date) -> str:
    return d.isoformat()


def _item(
    item_id: str,
    item_type: str,
    title: str,
    due: date,
    *,
    status: str,
    framework_id: str = "",
    link: str = "",
    details: str = "",
) -> Dict[str, Any]:
    today = date.today()
    return {
        "id": item_id,
        "type": item_type,
        "title": title,
        "date": _iso(due),
        "status": status,
        "days_remaining": (due - today).days if status == "upcoming" else (today - due).days,
        "framework_id": framework_id,
        "link": link,
        "details": details,
    }


def collect_items(framework_id: str = "", window_days: int = 30) -> Dict[str, Any]:
    today = date.today()
    end = today + timedelta(days=max(1, min(int(window_days), 365)))
    items: List[Dict[str, Any]] = []
    fw_low = (framework_id or "").lower()

    # 1. Policy reviews (published, overdue or due soon)
    try:
        from policies.review_reminders import get_policies_due_review
        from policies.store import get_document

        for p in get_policies_due_review():
            if fw_low:
                doc = get_document(p["id"]) or {}
                tags = doc.get("framework_tags") or []
                if fw_low not in [str(t).lower() for t in tags]:
                    continue
            due = _day(str(p.get("next_review_date") or ""))
            if due is None:
                continue
            status = "overdue" if p.get("urgency") == "overdue" else "upcoming"
            items.append(_item(
                f"pol:{p['id']}", "policy_review", p["title"], due,
                status=status, framework_id="",
                link="policies", details=f"Policy review due ({p.get('status', '')})",
            ))
    except Exception:
        pass

    # 2. Evidence requests (open, due in window or overdue)
    try:
        from evidence_hub.store import list_requests

        for req in list_requests(framework_id=framework_id or None):
            if req.get("status") not in ("open", ""):
                continue
            due = _day(str(req.get("due_date") or ""))
            if due is None:
                continue
            if due < today:
                items.append(_item(
                    f"req:{req['id']}", "evidence_request", req.get("title") or "Evidence request", due,
                    status="overdue", framework_id=req.get("framework_id", framework_id),
                    link="evidence-hub", details=f"Assigned to {req.get('assigned_to') or 'unassigned'}",
                ))
            elif due <= end:
                items.append(_item(
                    f"req:{req['id']}", "evidence_request", req.get("title") or "Evidence request", due,
                    status="upcoming", framework_id=req.get("framework_id", framework_id),
                    link="evidence-hub", details=f"Assigned to {req.get('assigned_to') or 'unassigned'}",
                ))
    except Exception:
        pass

    # 3. Expiring / stale evidence (freshness age-based)
    try:
        from evidence_hub.store import list_evidence, _freshness_score

        for ev in list_evidence(framework_id=framework_id or None):
            fs = _freshness_score(ev.get("uploaded_at") or "")
            if fs not in ("stale", "expired"):
                continue
            label = "Stale evidence" if fs == "stale" else "Expired evidence"
            items.append(_item(
                f"ev:{ev['id']}", "evidence_expiring", ev.get("display_title") or ev.get("name") or ev.get("filename") or "Evidence",
                today, status="overdue", framework_id="",
                link="evidence-hub", details=f"{label} — collected {str(ev.get('uploaded_at') or '')[:10]}",
            ))
    except Exception:
        pass

    # 4. Risk reviews (review_date in window or overdue)
    try:
        from risks.store import list_risks

        for risk in list_risks():
            rf = str(risk.get("framework") or "").lower()
            if fw_low and rf and rf != fw_low:
                continue
            due = _day(str(risk.get("review_date") or ""))
            if due is None:
                continue
            if due < today:
                items.append(_item(
                    f"risk:{risk['id']}", "risk_review", risk.get("title") or "Risk review", due,
                    status="overdue", framework_id=risk.get("framework", framework_id),
                    link="risks", details=f"Owner: {risk.get('owner') or 'unassigned'}",
                ))
            elif due <= end:
                items.append(_item(
                    f"risk:{risk['id']}", "risk_review", risk.get("title") or "Risk review", due,
                    status="upcoming", framework_id=risk.get("framework", framework_id),
                    link="risks", details=f"Owner: {risk.get('owner') or 'unassigned'}",
                ))
    except Exception:
        pass

    # 4b. Acceptance expiries (accepted risks lapse unless re-signed)
    try:
        from risks.store import list_risks

        for risk in list_risks():
            rf = str(risk.get("framework") or "").lower()
            if fw_low and rf and rf != fw_low:
                continue
            if risk.get("status") != "accepted":
                continue
            due = _day(str(risk.get("acceptance_expires") or ""))
            if due is None:
                continue
            owner = risk.get("owner") or "unassigned"
            ctl_owner = risk.get("control_owner") or ""
            confirm = f"Confirm with control owner {ctl_owner} that mitigation is still effective" if ctl_owner else "Confirm mitigation is still effective"
            if due < today:
                items.append(_item(
                    f"acc:{risk['id']}", "acceptance_expiry", risk.get("title") or "Risk acceptance", due,
                    status="overdue", framework_id=risk.get("framework", framework_id),
                    link="risks",
                    details=f"Acceptance expired — re-sign required. {confirm}. Owner: {owner}",
                ))
            elif due <= end:
                days = (due - today).days
                items.append(_item(
                    f"acc:{risk['id']}", "acceptance_expiry", risk.get("title") or "Risk acceptance", due,
                    status="upcoming", framework_id=risk.get("framework", framework_id),
                    link="risks",
                    details=f"Acceptance expires in {days}d. {confirm}. Owner: {owner}",
                ))
    except Exception:
        pass

    # 5. Control tests (recurring evidence-producing activities; due from last run)
    try:
        from control_tests.store import list_runs, list_tests, next_due
        from control_tests.framework import matches as test_matches

        for t in list_tests():
            if not t.get("active", True):
                continue
            if framework_id and not test_matches(t.get("framework", ""), framework_id):
                continue
            runs = list_runs(t["id"])
            last_run = runs[0] if runs else None
            due = next_due(t, last_run.get("run_date", "") if last_run else "")
            if due is None:
                continue
            freq = t.get("frequency") or "quarterly"
            last_txt = f"Last run: {str(last_run.get('run_date') or 'never')}" if last_run else "Never run"
            if due < today:
                items.append(_item(
                    f"ct:{t['id']}", "control_test", t.get("title") or "Control test", due,
                    status="overdue", framework_id=t.get("framework", framework_id),
                    link="control-tests",
                    details=f"{freq.title().replace('_', ' ')} · {last_txt} · Owner: {t.get('owner') or 'unassigned'}",
                ))
            elif due <= end:
                items.append(_item(
                    f"ct:{t['id']}", "control_test", t.get("title") or "Control test", due,
                    status="upcoming", framework_id=t.get("framework", framework_id),
                    link="control-tests",
                    details=f"{freq.title().replace('_', ' ')} · {last_txt} · Owner: {t.get('owner') or 'unassigned'}",
                ))
    except Exception:
        pass

    # 6. Program milestones (32 CFR 170 — POA&M closeout, reassessment,
    #    annual affirmation) written by the framework apps (e.g. cmmc).
    try:
        from compliance_calendar.store import list_milestones

        for m in list_milestones(due_before=_iso(end)):
            mf = str(m.get("framework_id") or "").lower()
            if fw_low and mf != fw_low:
                continue
            due = _day(str(m.get("due_date") or ""))
            if due is None:
                continue
            status = "overdue" if due < today else "upcoming"
            items.append(_item(
                f"mil:{mf}:{m.get('client_id') or ''}:{m.get('milestone_type')}",
                str(m.get("milestone_type") or "milestone"),
                m.get("title") or "Milestone",
                due,
                status=status,
                framework_id=mf,
                link=m.get("link") or "",
                details=m.get("details") or "",
            ))
    except Exception:
        pass

    items.sort(key=lambda it: (it["date"], it["type"]))
    overdue = [i for i in items if i["status"] == "overdue"]
    upcoming = [i for i in items if i["status"] == "upcoming"]
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "window_days": max(1, min(int(window_days), 365)),
        "window_start": _iso(today),
        "window_end": _iso(end),
        "total": len(items),
        "overdue_count": len(overdue),
        "upcoming_count": len(upcoming),
        "overdue": overdue,
        "upcoming": upcoming,
        "items": items,
    }
