from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Optional

router = APIRouter()


@router.get("/api/audit-log")
def get_audit_log(
    framework_id: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(200),
    offset: int = Query(0),
):
    from .store import list_events
    entries = list_events(
        framework_id=framework_id,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
    )
    return {"entries": entries}


@router.get("/api/audit-log/verify")
def verify_audit_chain(limit: int = Query(100000)):
    from .store import verify_chain
    return verify_chain(limit=limit)


@router.get("/api/audit-log/export")
def export_audit_log_csv(
    framework_id: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
):
    from .store import export_events_csv
    csv_data = export_events_csv(framework_id=framework_id, resource_type=resource_type)
    return Response(
        csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-log-export.csv"},
    )
