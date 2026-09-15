"""Complementary User Entity Controls — CUEC management for SOC 2."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


def list_cuecs(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    return ws.get("cuecs") or []


def create_cuec(ws: Dict[str, Any], control_id: str, description: str, assigned_to: str = "") -> Dict[str, Any]:
    cuecs = ws.get("cuecs") or []
    cuec = {
        "id": uuid4().hex[:12],
        "control_id": control_id,
        "description": description,
        "assigned_to": assigned_to,
        "status": "open",
        "notes": "",
        "last_reviewed": "",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    cuecs.append(cuec)
    ws["cuecs"] = cuecs
    return cuec


def update_cuec(ws: Dict[str, Any], cuec_id: str, **kwargs) -> Optional[Dict[str, Any]]:
    cuecs = ws.get("cuecs") or []
    for cuec in cuecs:
        if cuec["id"] == cuec_id:
            for k, v in kwargs.items():
                if v is not None and k != "id":
                    cuec[k] = v
            ws["cuecs"] = cuecs
            return cuec
    return None


def delete_cuec(ws: Dict[str, Any], cuec_id: str) -> bool:
    cuecs = ws.get("cuecs") or []
    before = len(cuecs)
    ws["cuecs"] = [c for c in cuecs if c["id"] != cuec_id]
    return len(ws["cuecs"]) < before


def get_cuecs_for_control(ws: Dict[str, Any], control_id: str) -> List[Dict[str, Any]]:
    return [c for c in (ws.get("cuecs") or []) if c.get("control_id") == control_id]
