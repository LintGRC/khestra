from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/api/effectiveness/summary")
def effectiveness_summary(
    framework: Optional[str] = Query(None),
    period: int = Query(12, ge=1, le=60),
):
    from .collect import collect_effectiveness

    return collect_effectiveness(framework_id=framework or "", period_months=period)
