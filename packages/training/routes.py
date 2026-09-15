from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional


class QuizSubmitBody(BaseModel):
    assignment_id: str
    answers: list[int] = []
import json

router = APIRouter()


class ModuleCreateBody(BaseModel):
    title: str
    description: str = ""
    category: str = ""
    is_required: bool = True
    renewal_period_days: int = 365
    control_ids: Optional[list[str]] = None
    created_by: str = ""


class ModuleUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_required: Optional[bool] = None
    renewal_period_days: Optional[int] = None
    control_ids: Optional[list[str]] = None


class AssignmentCreateBody(BaseModel):
    module_id: str
    person_id: str
    assigned_date: str = ""


class BulkAssignBody(BaseModel):
    module_id: str
    person_ids: list[str]
    assigned_date: str = ""


class AssignmentUpdateBody(BaseModel):
    status: Optional[str] = None
    completion_date: Optional[str] = None
    expiry_date: Optional[str] = None
    evidence_id: Optional[str] = None
    notes: Optional[str] = None
    exemption_reason: Optional[str] = None
    exempted_by: Optional[str] = None
    exempted_date: Optional[str] = None


class BulkCompleteBody(BaseModel):
    assignment_ids: list[str]
    completion_date: str


# ─── Modules ─────────────────────────


@router.get("/api/training/modules")
def get_modules(control_id: Optional[str] = Query(None)):
    from .store import list_modules
    return {"modules": list_modules(control_id=control_id)}


@router.post("/api/training/modules")
def create_module(body: ModuleCreateBody):
    from .store import create_module
    control_ids_str = json.dumps(body.control_ids) if body.control_ids else ""
    return {"module": create_module(
        title=body.title,
        description=body.description,
        category=body.category,
        is_required=body.is_required,
        renewal_period_days=body.renewal_period_days,
        control_ids=control_ids_str,
        created_by=body.created_by,
    )}


@router.get("/api/training/modules/{module_id}")
def get_module(module_id: str):
    from .store import get_module
    m = get_module(module_id)
    if not m:
        raise HTTPException(404, "Training module not found")
    return {"module": m}


@router.patch("/api/training/modules/{module_id}")
def update_module(module_id: str, body: ModuleUpdateBody):
    from .store import update_module
    control_ids_str = json.dumps(body.control_ids) if body.control_ids is not None else None
    m = update_module(
        module_id,
        title=body.title,
        description=body.description,
        category=body.category,
        is_required=body.is_required,
        renewal_period_days=body.renewal_period_days,
        control_ids=control_ids_str,
    )
    if not m:
        raise HTTPException(404, "Training module not found")
    return {"module": m}


@router.delete("/api/training/modules/{module_id}")
def delete_module(module_id: str):
    from .store import delete_module
    if not delete_module(module_id):
        raise HTTPException(404, "Training module not found")
    return {"status": "deleted"}


# ─── Assignments ─────────────────────


@router.get("/api/training/assignments")
def get_assignments(
    module_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    person_id: Optional[str] = Query(None),
):
    from .store import list_assignments
    return {"assignments": list_assignments(
        module_id=module_id,
        status=status,
        person_id=person_id,
    )}


@router.post("/api/training/assignments")
def create_assignment(body: AssignmentCreateBody):
    from .store import create_assignment
    return {"assignment": create_assignment(
        module_id=body.module_id,
        person_id=body.person_id,
        assigned_date=body.assigned_date,
    )}


@router.post("/api/training/assignments/bulk")
def bulk_assign(body: BulkAssignBody):
    from .store import create_bulk_assignments
    assignments = create_bulk_assignments(
        module_id=body.module_id,
        person_ids=body.person_ids,
        assigned_date=body.assigned_date,
    )
    return {"assignments": assignments, "count": len(assignments)}


@router.post("/api/training/assignments/bulk-complete")
def bulk_complete(body: BulkCompleteBody):
    from .store import bulk_complete_assignments
    updated = bulk_complete_assignments(
        assignment_ids=body.assignment_ids,
        completion_date=body.completion_date,
    )
    return {"updated": updated}


@router.post("/api/training/quiz/submit")
def submit_quiz(body: QuizSubmitBody):
    from .store import get_assignment, update_assignment, get_module
    from .models import utcnow
    a = get_assignment(body.assignment_id)
    if not a:
        raise HTTPException(404, "Assignment not found")
    mod = get_module(a.get("module_id", ""))
    questions = []
    if mod:
        qq = mod.get("quiz_questions", [])
        if isinstance(qq, str):
            import json
            try:
                qq = json.loads(qq)
            except Exception:
                qq = []
        questions = qq if isinstance(qq, list) else []

    if not questions:
        raise HTTPException(400, "No quiz questions configured for this module")

    correct = sum(1 for i, ans in enumerate(body.answers) if i < len(questions) and ans == questions[i]["correct"])
    total = len(questions)
    score = round(correct / total * 100) if total else 0
    passed = score >= 70

    update_assignment(body.assignment_id, status="completed" if passed else "in_progress", completed_at=utcnow())
    return {"score": score, "correct": correct, "total": total, "passed": passed}


@router.get("/api/training/assignments/{assignment_id}")
def get_assignment(assignment_id: str):
    from .store import get_assignment
    a = get_assignment(assignment_id)
    if not a:
        raise HTTPException(404, "Training assignment not found")
    return {"assignment": a}


@router.patch("/api/training/assignments/{assignment_id}")
def update_assignment(assignment_id: str, body: AssignmentUpdateBody):
    from .store import update_assignment
    a = update_assignment(
        assignment_id,
        status=body.status,
        completion_date=body.completion_date,
        expiry_date=body.expiry_date,
        evidence_id=body.evidence_id,
        notes=body.notes,
        exemption_reason=body.exemption_reason,
        exempted_by=body.exempted_by,
        exempted_date=body.exempted_date,
    )
    if not a:
        raise HTTPException(404, "Training assignment not found")
    return {"assignment": a}


@router.delete("/api/training/assignments/{assignment_id}")
def delete_assignment(assignment_id: str):
    from .store import delete_assignment
    if not delete_assignment(assignment_id):
        raise HTTPException(404, "Training assignment not found")
    return {"status": "deleted"}


# ─── Stats ────────────────────────────


@router.get("/api/training/stats")
def get_stats():
    from .store import get_stats
    return get_stats()


# ─── Auto-assign & Alerts ────────────


@router.post("/api/training/auto-assign")
def auto_assign():
    from .store import auto_assign_all
    return auto_assign_all()


@router.get("/api/training/alerts")
def get_alerts():
    from .store import get_alerts
    return get_alerts()
