"""Read-only SSP preview payloads for the platform UI (mirrors Word export structure)."""

from __future__ import annotations

from typing import Any, Dict, List

from controls import CMMC_FRAMEWORK
from narrative_prefill import has_implementation_narrative

FAMILY_ORDER = [
    "Access Control",
    "Awareness and Training",
    "Audit and Accountability",
    "Configuration Management",
    "Identification and Authentication",
    "Incident Response",
    "Maintenance",
    "Media Protection",
    "Personnel Security",
    "Physical Protection",
    "Risk Assessment",
    "Security Assessment",
    "System and Communications Protection",
    "System and Information Integrity",
]


def _risk_severity(weight: int) -> str:
    if weight >= 5:
        return "Critical"
    if weight == 3:
        return "High"
    if weight == 1:
        return "Moderate"
    return "Low"


def _family_section_label(family_name: str) -> str:
    try:
        idx = FAMILY_ORDER.index(family_name) + 1
    except ValueError:
        idx = 0
    return f"5.{idx} {family_name}" if idx else family_name


def control_ssp_preview(control_id: str, ans: Dict[str, Any]) -> Dict[str, Any]:
    if control_id not in CMMC_FRAMEWORK:
        raise ValueError(f"Unknown control: {control_id}")

    info = CMMC_FRAMEWORK[control_id]
    status = ans.get("status", "NOT STARTED")
    weight = info.get("weight", 0)
    narrative = (ans.get("implementation_narrative") or "").strip()

    if narrative:
        description = narrative
        description_missing = False
    elif status == "MET":
        description = (
            "Control implementation narrative not provided. Describe how this control is implemented."
        )
        description_missing = True
    else:
        description = "Control not yet implemented."
        description_missing = True

    assessment_methods: List[str] = []
    examine = (ans.get("examine") or "").strip()
    interview = (ans.get("interview") or "").strip()
    test = (ans.get("test") or "").strip()
    if examine:
        assessment_methods.append(f"Examine: {examine}")
    if interview:
        assessment_methods.append(f"Interview: {interview}")
    if test:
        assessment_methods.append(f"Test: {test}")

    evidence_files = [
        {
            "filename": ev.get("filename", "unknown"),
            "upload_date": ev.get("upload_date", ""),
        }
        for ev in (ans.get("evidence") or [])
    ]

    placeholders = _placeholder_tokens(description)

    return {
        "control_id": control_id,
        "heading": f"{control_id} - {info['name']}",
        "family": info["family"],
        "family_section": _family_section_label(info["family"]),
        "attributes": [
            {"label": "Status", "value": status},
            {"label": "Impact Level", "value": _risk_severity(weight)},
            {"label": "Weight", "value": str(weight)},
        ],
        "description": description,
        "description_missing": description_missing,
        "assessment_methods": assessment_methods,
        "evidence_files": evidence_files,
        "placeholders": placeholders,
        "export_note": "Read-only preview — matches the control narrative section in your SSP export.",
    }


def _placeholder_tokens(text: str) -> List[str]:
    import re

    return list(dict.fromkeys(re.findall(r"\[[^\]]+\]", text)))


def ssp_progress_detail(answers: Dict[str, Any], scoped_controls: List[str]) -> Dict[str, Any]:
    scoped = [c for c in scoped_controls if c in CMMC_FRAMEWORK]
    documented = 0
    families: Dict[str, Dict[str, Any]] = {}

    for cid in scoped:
        fam = CMMC_FRAMEWORK[cid]["family"]
        row = families.setdefault(
            fam,
            {"family": fam, "scoped_count": 0, "documented_count": 0},
        )
        row["scoped_count"] += 1
        if has_implementation_narrative(answers.get(cid, {})):
            documented += 1
            row["documented_count"] += 1

    family_rows = []
    for fam in FAMILY_ORDER:
        row = families.get(fam)
        if not row:
            continue
        n = row["scoped_count"]
        d = row["documented_count"]
        family_rows.append(
            {
                **row,
                "documented_pct": round(100 * d / n) if n else 0,
            }
        )

    total = len(scoped)
    pct = round(100 * documented / total) if total else 0
    return {
        "documented_count": documented,
        "scoped_count": total,
        "documented_pct": pct,
        "empty_count": total - documented,
        "families": family_rows,
    }
