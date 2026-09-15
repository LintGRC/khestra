from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class TestCreateBody(BaseModel):
    control_id: str
    framework: str
    test_procedure: str
    frequency: str = ""
    sample_size: int = 0
    sampling_methodology: str = ""
    population_size: int = 0
    confidence_level: float = 0.0
    margin_of_error: float = 0.0
    notes: str = ""
    created_by: str = ""


class TestUpdateBody(BaseModel):
    control_id: Optional[str] = None
    framework: Optional[str] = None
    test_procedure: Optional[str] = None
    frequency: Optional[str] = None
    sample_size: Optional[int] = None
    sampling_methodology: Optional[str] = None
    population_size: Optional[int] = None
    confidence_level: Optional[float] = None
    margin_of_error: Optional[float] = None
    status: Optional[str] = None
    last_tested: Optional[str] = None
    tested_by: Optional[str] = None
    evidence_id: Optional[str] = None
    notes: Optional[str] = None


class ResultCreateBody(BaseModel):
    result: str
    tested_by: str
    evidence_id: str = ""
    notes: str = ""


@router.get("/api/testing/tests")
def list_tests(
    control_id: Optional[str] = Query(None),
    framework: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    frequency: Optional[str] = Query(None),
):
    from .store import list_tests
    return {"tests": list_tests(
        control_id=control_id,
        framework=framework,
        status=status,
        frequency=frequency,
    )}


@router.post("/api/testing/tests")
def create_test(body: TestCreateBody):
    from .store import create_test
    return {"test": create_test(
        control_id=body.control_id,
        framework=body.framework,
        test_procedure=body.test_procedure,
        frequency=body.frequency,
        sample_size=body.sample_size,
        sampling_methodology=body.sampling_methodology,
        population_size=body.population_size,
        confidence_level=body.confidence_level,
        margin_of_error=body.margin_of_error,
        notes=body.notes,
        created_by=body.created_by,
    )}


@router.get("/api/testing/stats")
def get_stats():
    from .store import get_stats
    return get_stats()


@router.get("/api/testing/tests/{test_id}")
def get_test(test_id: str):
    from .store import get_test
    test = get_test(test_id)
    if not test:
        raise HTTPException(404, "Test not found")
    return {"test": test}


@router.patch("/api/testing/tests/{test_id}")
def update_test(test_id: str, body: TestUpdateBody):
    from .store import update_test
    test = update_test(
        test_id,
        control_id=body.control_id,
        framework=body.framework,
        test_procedure=body.test_procedure,
        frequency=body.frequency,
        sample_size=body.sample_size,
        status=body.status,
        last_tested=body.last_tested,
        tested_by=body.tested_by,
        evidence_id=body.evidence_id,
        notes=body.notes,
    )
    if not test:
        raise HTTPException(404, "Test not found")
    return {"test": test}


@router.delete("/api/testing/tests/{test_id}")
def delete_test(test_id: str):
    from .store import delete_test
    if not delete_test(test_id):
        raise HTTPException(404, "Test not found")
    return {"status": "deleted"}


@router.get("/api/testing/tests/{test_id}/results")
def get_results(test_id: str):
    from .store import get_results
    return {"results": get_results(test_id)}


@router.post("/api/testing/tests/{test_id}/results")
def add_result(test_id: str, body: ResultCreateBody):
    from .store import add_result
    r = add_result(
        test_id,
        result=body.result,
        tested_by=body.tested_by,
        evidence_id=body.evidence_id,
        notes=body.notes,
    )
    if not r:
        raise HTTPException(404, "Test not found")
    return {"result": r}
