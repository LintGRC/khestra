"""Organization membership — ties Entra users to client workspaces and per-org roles."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app_config import USER_ROLES
from config import DATA_DIR
from sandbox_config import sandbox_creator_role

MEMBERSHIP_FILE = DATA_DIR / "org_memberships.json"


@dataclass
class OrgMembership:
    client_id: str
    user_oid: str
    user_email: str
    user_name: str
    role: str
    joined_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load() -> Dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not MEMBERSHIP_FILE.exists():
        return {"memberships": []}
    try:
        return json.loads(MEMBERSHIP_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"memberships": []}


def _save(data: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = MEMBERSHIP_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, MEMBERSHIP_FILE)


def list_memberships() -> List[OrgMembership]:
    rows = _load().get("memberships") or []
    out: List[OrgMembership] = []
    for row in rows:
        try:
            out.append(OrgMembership(**row))
        except TypeError:
            continue
    return out


def memberships_for_user(user_oid: str) -> List[OrgMembership]:
    oid = (user_oid or "").strip()
    return [m for m in list_memberships() if m.user_oid == oid]


def membership_for_user(user_oid: str, client_id: str) -> Optional[OrgMembership]:
    oid = (user_oid or "").strip()
    for m in memberships_for_user(oid):
        if m.client_id == client_id:
            return m
    return None


def org_count_for_user(user_oid: str) -> int:
    return len(memberships_for_user(user_oid))


def add_membership(
    *,
    client_id: str,
    user_oid: str,
    user_email: str,
    user_name: str,
    role: str,
) -> OrgMembership:
    if role not in USER_ROLES:
        raise ValueError(f"Invalid role: {role}")
    oid = (user_oid or "").strip()
    if not oid:
        raise ValueError("user_oid required")

    data = _load()
    rows = data.get("memberships") or []
    for row in rows:
        if row.get("client_id") == client_id and row.get("user_oid") == oid:
            row.update(
                {
                    "user_email": user_email,
                    "user_name": user_name,
                    "role": role,
                }
            )
            _save(data)
            return OrgMembership(**row)

    record = OrgMembership(
        client_id=client_id,
        user_oid=oid,
        user_email=user_email,
        user_name=user_name,
        role=role,
        joined_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )
    rows.append(record.to_dict())
    data["memberships"] = rows
    _save(data)
    return record


def create_org_with_owner(
    *,
    client_id: str,
    display_name: str,
    user_oid: str,
    user_email: str,
    user_name: str,
) -> OrgMembership:
    return add_membership(
        client_id=client_id,
        user_oid=user_oid,
        user_email=user_email,
        user_name=user_name,
        role=sandbox_creator_role(),
    )


def client_ids_for_user(user_oid: str) -> List[str]:
    return [m.client_id for m in memberships_for_user(user_oid)]
