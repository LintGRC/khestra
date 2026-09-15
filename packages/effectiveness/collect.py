"""Program-effectiveness metrics.

Aggregates existing stores into the four panels of the effectiveness page:

- maturity_distribution / automation_ratio (CMMC workspace only)
- findings_recurrence (per-app findings store; cmmc/soc2/aigov)
- exception_trend (per-app exceptions store; soc2 only)
- decision_velocity (risks store; mounted in every app)

Each source reports `available: False` when the store is not initialized in
the host app, so the UI can show an honest "not tracked here" state instead
of fabricating data.
"""

from __future__ import annotations

from typing import Any, Dict, List

MATURITY_LEVELS = ["Ad Hoc", "Documented", "Implemented", "Managed", "Optimized"]

_STATUS_SNAPSHOT = ["open", "in_review", "approved", "expired", "rejected", "closed"]

_FW_ALIASES: Dict[str, List[str]] = {
    "CMMC": ["CMMC", "cmmc", "CMMC Rev 2"],
    "CMMC Rev 2": ["CMMC Rev 2", "CMMC", "cmmc"],
    "SOC 2": ["SOC 2", "SOC2", "soc2"],
    "SOC2": ["SOC 2", "SOC2", "soc2"],
    "AI Gov": ["AI Gov", "AIGov", "aigov", "AI Governance"],
    "AIGov": ["AI Gov", "AIGov", "aigov"],
}


def _framework_variants(param: str) -> List[str]:
    if not param:
        return []
    return _FW_ALIASES.get(param) or [param]


def _family_of(control_id: str) -> str:
    for sep in (".", "-"):
        if sep in control_id:
            return control_id.split(sep)[0]
    return control_id


def _quarter(date_str: str) -> str:
    if not date_str or len(date_str) < 7:
        return ""
    y, m = date_str[:4], date_str[5:7]
    try:
        return f"{y}-Q{(int(m) - 1) // 3 + 1}"
    except ValueError:
        return ""


def _maturity_panel(framework_id: str) -> Dict[str, Any]:
    try:
        from workspace_service import load_workspace
        from cmmc_collectors.automation_coverage import automation_coverage_for_control
    except ImportError:
        return {
            "available": False,
            "levels": MATURITY_LEVELS,
            "counts": [0] * len(MATURITY_LEVELS),
            "total": 0,
            "automated": 0,
            "scoped_total": 0,
            "note": "Maturity and automation tracking live in the CMMC workspace; not tracked in this app.",
        }
    try:
        ws = load_workspace()
        answers = ws.get("answers") or {}
        scoped = ws.get("scoped_controls") or list(answers.keys())
        counts = {lvl: 0 for lvl in MATURITY_LEVELS}
        automated = 0
        total = 0
        for cid in scoped:
            ans = answers.get(cid) or {}
            maturity = ans.get("maturity") or ""
            if maturity in counts:
                counts[maturity] += 1
                total += 1
            if automation_coverage_for_control(cid, ans=ans).get("level") != "manual":
                automated += 1
        if total == 0:
            return {
                "available": False,
                "levels": MATURITY_LEVELS,
                "counts": [0] * len(MATURITY_LEVELS),
                "total": 0,
                "automated": 0,
                "scoped_total": len(scoped),
                "note": "No maturity ratings recorded yet in this workspace.",
            }
        return {
            "available": True,
            "levels": MATURITY_LEVELS,
            "counts": [counts[lvl] for lvl in MATURITY_LEVELS],
            "total": total,
            "automated": automated,
            "scoped_total": len(scoped),
            "note": "",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "available": False,
            "levels": MATURITY_LEVELS,
            "counts": [0] * len(MATURITY_LEVELS),
            "total": 0,
            "automated": 0,
            "scoped_total": 0,
            "note": f"Unable to read workspace: {exc}",
        }


def _findings_panel(framework_id: str, period_months: int) -> Dict[str, Any]:
    try:
        from findings.store import DB_PATH, list_findings
    except ImportError:
        return {"available": False, "by_family": [], "recurring_count": 0, "note": "Findings not tracked in this app."}
    if DB_PATH is None:
        return {"available": False, "by_family": [], "recurring_count": 0, "note": "Findings store not initialized in this app."}
    variants = _framework_variants(framework_id)
    canonical = {v.lower(): v for v in reversed(variants)}
    try:
        rows = list_findings()
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "by_family": [], "recurring_count": 0, "note": f"Unable to read findings: {exc}"}

    per_family: Dict[str, Dict[str, int]] = {}
    seen: set = set()
    for r in rows:
        rid = r.get("id")
        if rid is not None:
            if rid in seen:
                continue
            seen.add(rid)
        fw = r.get("framework") or ""
        if canonical:
            label = canonical.get(fw.lower())
            if label is None:
                continue
        else:
            label = fw
        cids = r.get("control_ids") or []
        fam = _family_of(cids[0]) if cids else (label or "general")
        year = (r.get("created_at") or "")[:4]
        if not year.isdigit():
            continue
        key = f"{label} / {fam}" if label else fam
        bucket = per_family.setdefault(key, {})
        bucket[year] = bucket.get(year, 0) + 1

    by_family = [
        {"family": key, "counts": {y: n for y, n in sorted(years.items())}}
        for key, years in per_family.items()
    ]
    recurring = 0
    for fam in by_family:
        ys = sorted(int(y) for y in fam["counts"])
        if any(b - a == 1 for a, b in zip(ys, ys[1:])):
            recurring += 1
    return {
        "available": True,
        "by_family": by_family,
        "recurring_count": recurring,
        "note": "",
    }


def _exceptions_panel(framework_id: str, period_months: int) -> Dict[str, Any]:
    try:
        from exceptions.store import DB_PATH, list_exceptions
    except ImportError:
        return {"available": False, "quarters": [], "by_status": {}, "note": "Exception tracking lives in the SOC 2 app; not tracked here."}
    if DB_PATH is None:
        return {"available": False, "quarters": [], "by_status": {}, "note": "Exception store not initialized in this app."}
    variants = _framework_variants(framework_id)
    rows: List[Dict[str, Any]] = []
    for fw in variants:
        try:
            rows += list_exceptions(framework=fw)
        except Exception:  # noqa: BLE001
            continue
    if not variants:
        try:
            rows = list_exceptions()
        except Exception as exc:  # noqa: BLE001
            return {"available": False, "quarters": [], "by_status": {}, "note": f"Unable to read exceptions: {exc}"}

    statuses = sorted({(r.get("status") or "open") for r in rows})
    quarters = sorted({_quarter(r.get("created_at") or "") for r in rows if _quarter(r.get("created_at") or "")})
    by_status = {s: [] for s in statuses}
    for q in quarters:
        for s in statuses:
            by_status[s].append(sum(1 for r in rows if _quarter(r.get("created_at") or "") == q and (r.get("status") or "open") == s))
    return {
        "available": True,
        "quarters": quarters,
        "by_status": by_status,
        "note": "",
    }


def _risks_panel(framework_id: str) -> Dict[str, Any]:
    try:
        from risks.store import list_risks
    except ImportError:
        return {"available": False, "note": "Risk register not available."}
    variants = _framework_variants(framework_id)
    rows: List[Dict[str, Any]] = []
    for fw in variants:
        try:
            rows += list_risks(framework=fw)
        except Exception:  # noqa: BLE001
            continue
    if not variants:
        try:
            rows = list_risks()
        except Exception as exc:  # noqa: BLE001
            return {"available": False, "note": f"Unable to read risks: {exc}"}

    from datetime import date

    today = date.today()
    unowned = [r for r in rows if not (r.get("owner") or "").strip()]
    open_rows = [r for r in rows if r.get("status") not in ("closed", "accepted")]
    decisions = [r for r in rows if (r.get("review_date") or "").strip()]
    expired_acceptances = [
        r for r in rows
        if r.get("status") == "accepted" and r.get("acceptance_expires")
        and (today - date.fromisoformat(str(r["acceptance_expires"])[:10])).days > 0
    ]

    def _age_days(created: str) -> int:
        try:
            d = date.fromisoformat((created or "")[:10])
            return (today - d).days
        except ValueError:
            return 0

    oldest_unowned = max((_age_days(r.get("created_at") or "") for r in unowned), default=0)
    oldest_open = max((_age_days(r.get("created_at") or "") for r in open_rows), default=0)
    return {
        "available": True,
        "total_risks": len(rows),
        "unowned_count": len(unowned),
        "oldest_unowned_days": oldest_unowned,
        "oldest_open_days": oldest_open,
        "decisions_made": len(decisions),
        "expired_acceptances": len(expired_acceptances),
        "note": "",
    }


def collect_effectiveness(framework_id: str = "", period_months: int = 12) -> Dict[str, Any]:
    return {
        "framework_id": framework_id,
        "period_months": period_months,
        "maturity_distribution": _maturity_panel(framework_id),
        "findings_recurrence": _findings_panel(framework_id, period_months),
        "exception_trend": _exceptions_panel(framework_id, period_months),
        "decision_velocity": _risks_panel(framework_id),
    }
