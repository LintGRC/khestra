from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from typing import Optional
from pydantic import BaseModel

router = APIRouter()


class AssetCreate(BaseModel):
    name: str = ""
    type: str = ""
    owner: str = ""
    description: str = ""
    environment: str = ""
    data_classification: str = ""
    handles_cui: bool = False
    location: str = ""
    framework_tags: list[str] = []
    workspace_id: str = ""
    org_id: str = ""


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    owner: Optional[str] = None
    description: Optional[str] = None
    environment: Optional[str] = None
    data_classification: Optional[str] = None
    handles_cui: Optional[bool] = None
    location: Optional[str] = None
    framework_tags: Optional[list[str]] = None


@router.post("/api/assets/import/csv")
def import_assets_csv(file: UploadFile = File(...)):
    from .store import import_csv
    content = file.file.read()
    count = import_csv(content)
    return {"imported": count}


@router.get("/api/assets/export/csv")
def export_assets_csv():
    from .store import list_assets, export_csv
    assets = list_assets()
    csv_data = export_csv(assets)
    return Response(
        csv_data, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=assets.csv"},
    )


@router.get("/api/assets")
def list_assets():
    from .store import list_assets
    return {"assets": list_assets()}


@router.post("/api/assets")
def create_asset(body: AssetCreate):
    from .store import create_asset
    return {"asset": create_asset(
        name=body.name, type=body.type, owner=body.owner,
        description=body.description, environment=body.environment,
        data_classification=body.data_classification,
        handles_cui=body.handles_cui, location=body.location,
        framework_tags=body.framework_tags,
        workspace_id=body.workspace_id, org_id=body.org_id,
    )}


@router.get("/api/assets/{aid}")
def get_asset(aid: str):
    from .store import get_asset
    a = get_asset(aid)
    if not a:
        raise HTTPException(404, "Asset not found")
    return {"asset": a}


@router.patch("/api/assets/{aid}")
def update_asset(aid: str, body: AssetUpdate):
    from .store import update_asset
    a = update_asset(aid, **body.model_dump(exclude_none=True))
    if not a:
        raise HTTPException(404, "Asset not found")
    return {"asset": a}


@router.delete("/api/assets/{aid}")
def delete_asset(aid: str):
    from .store import delete_asset
    if not delete_asset(aid):
        raise HTTPException(404, "Asset not found")
    return {"status": "deleted"}
