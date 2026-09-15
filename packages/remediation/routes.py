"""Shared FastAPI router for the Remediation Hub. Mount in any app server."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from .models import (
    RemediationItem,
    framework_labels,
    framework_types,
    new_remediation_id,
)
from .store import RemediationStore

router = APIRouter(tags=["remediation"])

# Set by the app server during startup
_store: RemediationStore | None = None


def init_store(data_dir: str | None = None) -> RemediationStore:
    from pathlib import Path

    if data_dir:
        path = Path(data_dir)
    else:
        path = Path.cwd() / "data"
    global _store
    _store = RemediationStore(path)
    return _store


def get_store() -> RemediationStore:
    if _store is None:
        raise RuntimeError("Remediation store not initialized. Call init_store() during app startup.")
    return _store


@router.get("/api/remediation/types")
def list_types(framework: str = Query("")):
    """Return available remediation types, optionally filtered by framework."""
    if framework:
        return {"framework": framework, "types": framework_types(framework), "labels": framework_labels(framework)}
    return {"types": ["gap", "finding", "exception", "risk", "corrective_action", "vendor_remediation", "poam_entry", "milestone"]}


@router.get("/api/remediation")
def list_items(
    framework: str = Query(""),
    type_filter: str = Query("", alias="type"),
    status: str = Query(""),
    owner: str = Query(""),
    limit: int = Query(100),
    offset: int = Query(0),
):
    store = get_store()
    items = store.list(framework=framework or None, type_filter=type_filter or None, status=status or None, owner=owner or None, limit=limit, offset=offset)
    return {
        "items": [i.to_dict() for i in items],
        "total": store.count(framework=framework or None, type_filter=type_filter or None),
        "stats": store.stats(framework=framework or None),
    }


@router.get("/api/remediation/stats")
def get_stats(framework: str = Query("")):
    store = get_store()
    return store.stats(framework=framework or None)


@router.get("/api/remediation/{item_id}")
def get_item(item_id: str):
    store = get_store()
    item = store.get(item_id)
    if not item:
        raise HTTPException(404, "Remediation item not found")
    return item.to_dict()


@router.post("/api/remediation")
def create_item(item: RemediationItem):
    store = get_store()
    item.id = new_remediation_id()
    created = store.upsert(item)
    return created.to_dict()


@router.patch("/api/remediation/{item_id}")
def update_item(item_id: str, fields: dict):
    store = get_store()
    item = store.get(item_id)
    if not item:
        raise HTTPException(404, "Remediation item not found")
    for key, value in fields.items():
        if hasattr(item, key) and key not in ("id", "created_at"):
            setattr(item, key, value)
    updated = store.upsert(item)
    return updated.to_dict()


@router.delete("/api/remediation/{item_id}")
def delete_item(item_id: str):
    store = get_store()
    if not store.delete(item_id):
        raise HTTPException(404, "Remediation item not found")
    return {"status": "deleted"}
