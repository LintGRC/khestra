from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class AssignmentCreateBody(BaseModel):
    org_id: str
    framework: str
    ref_type: str
    ref_id: str
    user_id: str
    user_name: str = ""
    responsibility: str = "Responsible"
    notes: str = ""


class AssignmentUpdateBody(BaseModel):
    responsibility: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    notes: Optional[str] = None


@router.get("/api/raci")
def list_assignments(
    org_id: Optional[str] = Query(None),
    framework: Optional[str] = Query(None),
    ref_type: Optional[str] = Query(None),
    ref_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
):
    from .store import list_assignments
    return {"assignments": list_assignments(
        org_id=org_id,
        framework=framework,
        ref_type=ref_type,
        ref_id=ref_id,
        user_id=user_id,
    )}


@router.post("/api/raci")
def create_assignment(body: AssignmentCreateBody):
    from .store import create_assignment
    return {"assignment": create_assignment(
        org_id=body.org_id,
        framework=body.framework,
        ref_type=body.ref_type,
        ref_id=body.ref_id,
        user_id=body.user_id,
        user_name=body.user_name,
        responsibility=body.responsibility,
        notes=body.notes,
    )}


@router.get("/api/raci/{assignment_id}")
def get_assignment(assignment_id: str):
    from .store import get_assignment
    a = get_assignment(assignment_id)
    if not a:
        raise HTTPException(404, "Assignment not found")
    return {"assignment": a}


@router.patch("/api/raci/{assignment_id}")
def update_assignment(assignment_id: str, body: AssignmentUpdateBody):
    from .store import update_assignment
    a = update_assignment(
        assignment_id,
        responsibility=body.responsibility,
        user_id=body.user_id,
        user_name=body.user_name,
        notes=body.notes,
    )
    if not a:
        raise HTTPException(404, "Assignment not found")
    return {"assignment": a}


@router.delete("/api/raci/{assignment_id}")
def delete_assignment(assignment_id: str):
    from .store import delete_assignment
    if not delete_assignment(assignment_id):
        raise HTTPException(404, "Assignment not found")
    return {"status": "deleted"}


@router.get("/api/raci/matrix")
def get_matrix(
    org_id: str = Query(...),
    framework: Optional[str] = Query(None),
    ref_type: Optional[str] = Query(None),
):
    from .store import get_raci_matrix
    return get_raci_matrix(org_id, framework=framework, ref_type=ref_type)
