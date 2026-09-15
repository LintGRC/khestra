"""CMMC contract-clause tracking — 32 CFR 170.23 flowdown + DFARS 252.204-7020/7021.

Structured records per client: which contracts require which CMMC status
(Level 1 Self / Level 2 Self / Level 2 C3PAO) via the DFARS clause, whether
flowdown to subcontractors is required, and a mismatch warning against the
held CMMC status.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

CLAUSES = ("", "252.204-7020", "252.204-7021")
REQUIRED_STATUSES = ("", "level1_self", "level2_self", "level2_c3pao")
STATUS_LABELS = {
    "level1_self": "Level 1 (Self)",
    "level2_self": "Level 2 (Self)",
    "level2_c3pao": "Level 2 (C3PAO)",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def list_contracts(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    return list(ws.get("contracts") or [])


def add_contract(ws: Dict[str, Any], fields: Dict[str, Any]) -> Dict[str, Any]:
    contract = {
        "id": uuid.uuid4().hex[:12],
        "name": str(fields.get("name") or "").strip(),
        "contract_number": str(fields.get("contract_number") or "").strip(),
        "clause": str(fields.get("clause") or "").strip(),
        "required_status": str(fields.get("required_status") or "").strip(),
        "flowdown_required": bool(fields.get("flowdown_required")),
        "notes": str(fields.get("notes") or "").strip(),
        "created_at": _now(),
    }
    if not contract["name"]:
        raise ValueError("Contract name is required")
    if contract["clause"] not in CLAUSES:
        raise ValueError(f"Clause must be one of: {', '.join(c for c in CLAUSES if c)}")
    if contract["required_status"] not in REQUIRED_STATUSES:
        raise ValueError(f"Required status must be one of: {', '.join(REQUIRED_STATUSES)}")
    contracts = list_contracts(ws)
    contracts.append(contract)
    ws["contracts"] = contracts
    return contract


def update_contract(ws: Dict[str, Any], contract_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    contracts = list_contracts(ws)
    for c in contracts:
        if c["id"] == contract_id:
            for key in ("name", "contract_number", "clause", "required_status", "flowdown_required", "notes"):
                if key in fields:
                    c[key] = fields[key]
            if c["clause"] not in CLAUSES:
                raise ValueError(f"Clause must be one of: {', '.join(x for x in CLAUSES if x)}")
            if c["required_status"] not in REQUIRED_STATUSES:
                raise ValueError("Invalid required status")
            ws["contracts"] = contracts
            return c
    return None


def delete_contract(ws: Dict[str, Any], contract_id: str) -> bool:
    contracts = list_contracts(ws)
    kept = [c for c in contracts if c["id"] != contract_id]
    if len(kept) == len(contracts):
        return False
    ws["contracts"] = kept
    return True


def contracts_with_status(ws: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Contracts enriched with held CMMC status + mismatch flag."""
    held_type = (ws.get("cmmc_assessment") or {}).get("assessment_type") or ""
    held = STATUS_LABELS.get(held_type, "None")
    out = []
    for c in list_contracts(ws):
        required = c.get("required_status") or ""
        mismatch = bool(required and required != held_type)
        out.append({
            **c,
            "held_status": held,
            "held_status_key": held_type,
            "mismatch": mismatch,
        })
    return out
