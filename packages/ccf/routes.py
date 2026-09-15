"""Shared FastAPI router for CCF endpoints. Mount in any app server."""

from __future__ import annotations

from fastapi import APIRouter
from .ccf import (
    get_ccf_topics,
    get_framework_controls,
    get_mapped_controls,
    list_frameworks,
    map_control_to_ccf,
)

router = APIRouter(tags=["ccf"])


@router.get("/api/ccf/frameworks")
def list_all_frameworks():
    return {"frameworks": list_frameworks()}


@router.get("/api/ccf/topics")
def list_topics():
    topics = []
    for t in get_ccf_topics():
        topics.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "control_count": {
                "cmmc": len(t.cmmc),
                "soc2": len(t.soc2),
                "aigovernance": len(t.aigovernance),
            },
        })
    return {"topics": topics}


@router.get("/api/ccf/frameworks/{framework_id}/controls")
def framework_controls(framework_id: str):
    return {"framework_id": framework_id, "topics": get_framework_controls(framework_id)}


@router.get("/api/ccf/map")
def translate(source: str, control_id: str, target: str | None = None):
    """Map a control to CCF topics, optionally translate to another framework."""
    if target:
        result = get_mapped_controls(source, target, control_id)
    else:
        result = map_control_to_ccf(source, control_id)
    return {"source": source, "control_id": control_id, "target": target, "mappings": result}
