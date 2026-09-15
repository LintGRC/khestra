"""Migrate legacy PE/PS control IDs and saved assessment answers."""

from typing import Any, Dict, List

# Personnel was labeled 3.10.x; Physical was labeled 3.9.x — swap to NIST numbering.
# Order: free PS 3.10.x slots before PE renames into 3.10.x.
CONTROL_ID_RENAMES = [
    ("PS.L2-3.10.1", "PS.L2-3.9.1"),
    ("PS.L2-3.10.2", "PS.L2-3.9.2"),
    ("PE.L2-3.9.1", "PE.L2-3.10.1"),
    ("PE.L2-3.9.5", "PE.L2-3.10.2"),
    ("PE.L2-3.9.2", "PE.L2-3.10.3"),
    ("PE.L2-3.9.3", "PE.L2-3.10.4"),
    ("PE.L2-3.9.4", "PE.L2-3.10.5"),
    ("PE.L2-3.9.6", "PE.L2-3.10.6"),
]

PE_3106_NAME = (
    "Enforce safeguarding measures for CUI at alternate work sites."
)


def migrate_control_ids_inplace(framework: dict) -> None:
    for old_id, new_id in CONTROL_ID_RENAMES:
        if old_id not in framework:
            continue
        framework[new_id] = framework.pop(old_id)
    if "PE.L2-3.10.6" in framework:
        framework["PE.L2-3.10.6"]["name"] = PE_3106_NAME


def migrate_answers(answers: Dict[str, Any]) -> Dict[str, Any]:
    migrated: Dict[str, Any] = {}
    for cid, data in answers.items():
        new_id = cid
        for old_id, renamed in CONTROL_ID_RENAMES:
            if cid == old_id:
                new_id = renamed
                break
        if new_id not in migrated:
            migrated[new_id] = data
        else:
            merged = dict(migrated[new_id])
            merged.update(data)
            migrated[new_id] = merged
    return migrated


def migrate_scoped_controls(scoped: List[str]) -> List[str]:
    mapping = dict(CONTROL_ID_RENAMES)
    return [mapping.get(cid, cid) for cid in scoped]
