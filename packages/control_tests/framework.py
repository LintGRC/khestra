"""Framework alias resolution for control tests.

Stores use differing framework spellings across apps (calendar pages pass
"CMMC"/"SOC2"/"AIGov", risk store uses "CMMC Rev 2"/"SOC 2", tests default
to canonical names). Single canonical-first mapping keeps filtering
consistent without the case/empty-string duplication trap.
"""

from __future__ import annotations

from typing import Dict, List

_FW_ALIASES: Dict[str, List[str]] = {
    "CMMC": ["CMMC", "cmmc", "CMMC Rev 2"],
    "CMMC Rev 2": ["CMMC Rev 2", "CMMC", "cmmc"],
    "SOC 2": ["SOC 2", "SOC2", "soc2"],
    "SOC2": ["SOC 2", "SOC2", "soc2"],
    "AI Gov": ["AI Gov", "AIGov", "aigov", "AI Governance"],
    "AIGov": ["AI Gov", "AIGov", "aigov"],
    "ISO 27001": ["ISO 27001", "ISO27001", "iso27001", "ISO 27001:2022"],
    "ISO27001": ["ISO 27001", "ISO27001", "iso27001", "ISO 27001:2022"],
}


def variants_for(param: str) -> List[str]:
    if not param:
        return []
    return _FW_ALIASES.get(param) or [param]


def matches(framework_value: str, param: str) -> bool:
    """True when framework_value (case-insensitive) is one of param's variants."""
    variants = variants_for(param)
    if not variants:
        return True
    return (framework_value or "").lower() in {v.lower() for v in variants}
