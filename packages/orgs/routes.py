from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class OrgCreateBody(BaseModel):
    name: str
    slug: Optional[str] = None
    description: str = ""


class OrgUpdateBody(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None


class UserCreateBody(BaseModel):
    email: str
    name: str
    oid: str = ""
    default_role: str = "Viewer"


class UserUpdateBody(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    oid: Optional[str] = None
    default_role: Optional[str] = None


class MembershipBody(BaseModel):
    org_id: str
    user_id: str
    role: str = "Member"


class MembershipUpdateBody(BaseModel):
    role: str


# ─── Orgs ──────────────────────────────────────────


@router.get("/api/orgs")
def get_orgs():
    from .store import list_orgs
    return {"orgs": list_orgs()}


@router.post("/api/orgs")
def create_org(body: OrgCreateBody):
    from .store import create_org
    try:
        return {"org": create_org(body.name, body.slug, body.description)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/api/orgs/{org_id}")
def get_org(org_id: str):
    from .store import get_org
    org = get_org(org_id)
    if not org:
        raise HTTPException(404, "Org not found")
    return {"org": org}


@router.patch("/api/orgs/{org_id}")
def update_org(org_id: str, body: OrgUpdateBody):
    from .store import update_org
    try:
        org = update_org(org_id, name=body.name, slug=body.slug, description=body.description)
        if not org:
            raise HTTPException(404, "Org not found")
        return {"org": org}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/api/orgs/{org_id}")
def delete_org(org_id: str):
    from .store import delete_org
    if not delete_org(org_id):
        raise HTTPException(404, "Org not found")
    return {"status": "deleted"}


# ─── Users ─────────────────────────────────────────


@router.get("/api/users")
def get_users():
    from .store import list_users
    return {"users": list_users()}


@router.post("/api/users")
def create_user(body: UserCreateBody):
    from .store import create_user
    return {"user": create_user(body.email, body.name, body.oid, body.default_role)}


@router.post("/api/users/upsert")
def upsert_user(body: UserCreateBody):
    from .store import upsert_user
    return {"user": upsert_user(body.email, body.name, body.oid, body.default_role)}


@router.get("/api/users/{user_id}")
def get_user(user_id: str):
    from .store import get_user
    user = get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return {"user": user}


@router.patch("/api/users/{user_id}")
def update_user(user_id: str, body: UserUpdateBody):
    from .store import update_user
    user = update_user(user_id, name=body.name, email=body.email, oid=body.oid, default_role=body.default_role)
    if not user:
        raise HTTPException(404, "User not found")
    return {"user": user}


@router.delete("/api/users/{user_id}")
def delete_user(user_id: str):
    from .store import delete_user
    if not delete_user(user_id):
        raise HTTPException(404, "User not found")
    return {"status": "deleted"}


# ─── Memberships ───────────────────────────────────


@router.get("/api/memberships")
def get_memberships(org_id: Optional[str] = Query(None), user_id: Optional[str] = Query(None)):
    from .store import list_memberships
    return {"memberships": list_memberships(org_id=org_id, user_id=user_id)}


@router.post("/api/memberships")
def add_membership(body: MembershipBody):
    from .store import add_membership
    try:
        return {"membership": add_membership(body.org_id, body.user_id, body.role)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/api/memberships/{membership_id}")
def update_membership(membership_id: str, body: MembershipUpdateBody):
    from .store import update_membership
    m = update_membership(membership_id, body.role)
    if not m:
        raise HTTPException(404, "Membership not found")
    return {"membership": m}


@router.delete("/api/memberships/{membership_id}")
def remove_membership(membership_id: str):
    from .store import remove_membership
    if not remove_membership(membership_id):
        raise HTTPException(404, "Membership not found")
    return {"status": "removed"}


@router.get("/api/users/{user_id}/orgs")
def get_user_orgs(user_id: str):
    from .store import get_user_orgs
    return {"orgs": get_user_orgs(user_id)}
