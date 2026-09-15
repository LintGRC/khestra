"""CMMC Assessment Scope record — 32 CFR Part 170.19.

Formalizes the assessment scope for SPRS submission and exports: whether an
External Service Provider (ESP) is in scope, ESP name and facilities, physical
facilities, the scope statement, and the asset summary.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

EMPTY_SCOPE: Dict[str, Any] = {
    "esp": "",            # "yes" | "no"
    "esp_name": "",       # External Service Provider name (§170.19(c))
    "esp_facilities": "", # ESP facility locations
    "facilities": "",     # Contractor facility locations
    "scope_statement": "",  # narrative scope statement
    "assets_in_scope": "",  # asset/system summary
}

ESP_VALUES = ("", "yes", "no")


def merge_scope(saved: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize a persisted scope record; never fail on legacy data."""
    src = saved or {}
    out = dict(EMPTY_SCOPE)
    for key in EMPTY_SCOPE:
        val = src.get(key)
        if isinstance(val, str):
            out[key] = val.strip()
        elif val:
            out[key] = val
    if out["esp"] not in ESP_VALUES:
        out["esp"] = ""
    return out


def apply_scope(ws: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and persist the assessment scope record."""
    cleaned = merge_scope(payload)
    if cleaned["esp"] == "yes" and not cleaned["esp_name"]:
        raise ValueError("ESP name is required when an External Service Provider is in scope")
    ws["cmmc_scope"] = cleaned
    return dict(cleaned)
