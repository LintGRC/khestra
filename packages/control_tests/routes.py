"""Control tests — shared FastAPI router."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .framework import matches
from .store import (
    add_run,
    create_test,
    delete_test,
    get_test,
    list_runs,
    list_tests,
    next_due,
    update_test,
)

router = APIRouter(tags=["control-tests"])


class TestCreate(BaseModel):
    title: str
    control_id: str = ""
    framework: str = ""
    frequency: str = "quarterly"
    owner: str = ""
    target_rpo_minutes: Optional[int] = None
    target_rto_minutes: Optional[int] = None


class TestUpdate(BaseModel):
    title: Optional[str] = None
    control_id: Optional[str] = None
    framework: Optional[str] = None
    frequency: Optional[str] = None
    owner: Optional[str] = None
    active: Optional[bool] = None
    target_rpo_minutes: Optional[int] = None
    target_rto_minutes: Optional[int] = None


class RunCreate(BaseModel):
    run_date: str = ""
    result: str = "passed"
    notes: str = ""
    evidence_hub_id: str = ""
    evidence_title: str = ""
    run_by: str = ""
    actual_rpo_minutes: Optional[int] = None
    actual_rto_minutes: Optional[int] = None
    verified_by: str = ""


def _enrich_runs(test: Dict[str, Any], runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tgt_rpo = test.get("target_rpo_minutes")
    tgt_rto = test.get("target_rto_minutes")
    out = []
    for r in runs:
        r = dict(r)
        r["met_rpo"] = (
            bool(tgt_rpo and r.get("actual_rpo_minutes") is not None and r["actual_rpo_minutes"] <= tgt_rpo)
            if tgt_rpo
            else None
        )
        r["met_rto"] = (
            bool(tgt_rto and r.get("actual_rto_minutes") is not None and r["actual_rto_minutes"] <= tgt_rto)
            if tgt_rto
            else None
        )
        r["has_evidence"] = bool(r.get("evidence_hub_id"))
        out.append(r)
    return out


def _enrich(test: Dict[str, Any], runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    today = date.today()
    run_count = len(runs)
    last_run = runs[0] if runs else None
    due = next_due(test, last_run.get("run_date", "") if last_run else "")
    runs = _enrich_runs(test, runs)
    runs_without_evidence = sum(1 for r in runs if not r.get("evidence_hub_id"))
    commitment = _commitment(test)
    return {
        **test,
        "run_count": run_count,
        "last_run": runs[0] if runs else None,
        "next_due": due.isoformat() if due else "",
        "overdue": bool(due and due < today),
        "expected_per_year": 12 // max(1, _months(test.get("frequency") or "")),
        "runs_without_evidence": runs_without_evidence,
        "commitment": commitment,
    }


def _fmt_minutes(mins: int) -> str:
    h, m = divmod(mins, 60)
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"


def _commitment(test: Dict[str, Any]) -> str:
    """Audit-ready statement of the tested commitment, e.g. 'RPO ≤ 4h · RTO ≤ 2h'."""
    parts = []
    if test.get("target_rpo_minutes") is not None:
        parts.append(f"RPO ≤ {_fmt_minutes(test['target_rpo_minutes'])}")
    if test.get("target_rto_minutes") is not None:
        parts.append(f"RTO ≤ {_fmt_minutes(test['target_rto_minutes'])}")
    return " · ".join(parts)


def _months(frequency: str) -> int:
    from .store import FREQUENCY_MONTHS

    return FREQUENCY_MONTHS.get(frequency, 3)


@router.get("/api/control-tests")
def get_control_tests(framework: str = Query("")):
    tests = list_tests()
    out = []
    for t in tests:
        if framework and not matches(t.get("framework", ""), framework):
            continue
        out.append(_enrich(t, list_runs(t["id"])))
    return {"tests": out, "count": len(out)}


@router.post("/api/control-tests")
def post_control_test(body: TestCreate):
    if not body.title.strip():
        raise HTTPException(status_code=422, detail="Title is required")
    test = create_test(
        title=body.title.strip(),
        control_id=body.control_id.strip(),
        framework=body.framework.strip(),
        frequency=body.frequency,
        owner=body.owner.strip(),
        target_rpo_minutes=body.target_rpo_minutes,
        target_rto_minutes=body.target_rto_minutes,
    )
    return _enrich(test, [])


@router.patch("/api/control-tests/{test_id}")
def patch_control_test(test_id: str, body: TestUpdate):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    test = update_test(test_id, fields)
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return _enrich(test, list_runs(test_id))


@router.delete("/api/control-tests/{test_id}")
def delete_control_test(test_id: str):
    if not delete_test(test_id):
        raise HTTPException(status_code=404, detail="Test not found")
    return {"deleted": test_id}


@router.get("/api/control-tests/{test_id}/runs")
def get_test_runs(test_id: str):
    test = get_test(test_id)
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return {
        "test_id": test_id,
        "test": _enrich(test, list_runs(test_id)),
        "runs": _enrich_runs(test, list_runs(test_id)),
    }


@router.post("/api/control-tests/{test_id}/runs")
def post_test_run(test_id: str, body: RunCreate):
    if get_test(test_id) is None:
        raise HTTPException(status_code=404, detail="Test not found")
    run = add_run(
        test_id,
        run_date=body.run_date,
        result=body.result,
        notes=body.notes,
        evidence_hub_id=body.evidence_hub_id,
        evidence_title=body.evidence_title,
        run_by=body.run_by,
        actual_rpo_minutes=body.actual_rpo_minutes,
        actual_rto_minutes=body.actual_rto_minutes,
        verified_by=body.verified_by,
    )
    test = get_test(test_id)
    enriched = _enrich(test, list_runs(test_id))
    return {"run": _enrich_runs(test, [run])[0], "test": enriched}
