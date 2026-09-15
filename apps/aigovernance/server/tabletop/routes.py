from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from .models import ExerciseCreateBody
from .scenarios import list_scenarios, get_scenario
from .store import list_exercises, get_exercise, create_exercise, delete_exercise
from .docx import export_exercise_docx

router = APIRouter()


@router.get("/api/tabletop/scenarios")
def list_tabletop_scenarios():
    return {"scenarios": list_scenarios()}


@router.get("/api/tabletop/scenarios/{scenario_id}")
def get_tabletop_scenario(scenario_id: str):
    s = get_scenario(scenario_id)
    if not s:
        raise HTTPException(404, "Scenario not found")
    return {"scenario": s}


@router.post("/api/tabletop/exercise")
def submit_exercise(body: ExerciseCreateBody):
    scenario = get_scenario(body.scenarioId)
    if not scenario:
        raise HTTPException(404, "Scenario not found")
    responses = [r.model_dump() for r in body.responses]
    exercise = create_exercise(
        scenario, responses, participants=body.participants
    )
    return {"exercise": exercise}


@router.get("/api/tabletop/exercises")
def list_tabletop_exercises():
    return {"exercises": list_exercises()}


@router.get("/api/tabletop/exercises/{eid}")
def get_tabletop_exercise(eid: str, format: str = Query("")):
    exercise = get_exercise(eid)
    if not exercise:
        raise HTTPException(404, "Exercise not found")
    if format == "docx":
        data = export_exercise_docx(exercise)
        return Response(
            content=data,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            headers={
                "Content-Disposition": (
                    f'attachment; filename="tabletop-{eid}.docx"'
                )
            },
        )
    return {"exercise": exercise}


@router.delete("/api/tabletop/exercises/{eid}")
def delete_tabletop_exercise(eid: str):
    if not delete_exercise(eid):
        raise HTTPException(404, "Exercise not found")
    return {"status": "deleted"}
