from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


@dataclass
class Org:
    id: str
    name: str
    slug: str
    description: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Org":
        return Org(**d)


@dataclass
class User:
    id: str
    email: str
    name: str
    oid: str = ""
    default_role: str = "Viewer"
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "User":
        return User(**d)


@dataclass
class OrgMembership:
    id: str
    org_id: str
    user_id: str
    role: str  # Owner, Admin, Member, Viewer
    joined_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "OrgMembership":
        return OrgMembership(**d)


ORG_ROLES = ["Owner", "Admin", "Member", "Viewer"]

ORG_ROLE_PERMISSIONS = {
    "Owner": {"manage_org": True, "manage_members": True, "edit_controls": True, "view_all": True, "export": True},
    "Admin": {"manage_org": False, "manage_members": True, "edit_controls": True, "view_all": True, "export": True},
    "Member": {"manage_org": False, "manage_members": False, "edit_controls": True, "view_all": False, "export": False},
    "Viewer": {"manage_org": False, "manage_members": False, "edit_controls": False, "view_all": True, "export": False},
}


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
