"""Multi-client workspaces for consultants / MSPs — one folder per defense client."""

from __future__ import annotations

import json
import os
import re
import shutil
import tarfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import DATA_DIR, resolve_session_state_path

CLIENTS_DIR = DATA_DIR / "clients"
MANIFEST_NAME = "clients.json"
DEFAULT_CLIENT_ID = "default"


def _manifest_path() -> Path:
    CLIENTS_DIR.mkdir(parents=True, exist_ok=True)
    return CLIENTS_DIR / MANIFEST_NAME


def _load_manifest() -> Dict[str, Any]:
    path = _manifest_path()
    if not path.exists():
        return {"clients": [], "active_client_id": DEFAULT_CLIENT_ID}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"clients": [], "active_client_id": DEFAULT_CLIENT_ID}


def _save_manifest(data: Dict[str, Any]) -> None:
    path = _manifest_path()
    tmp = path.with_suffix(f".{uuid.uuid4().hex}.tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def slugify_client_name(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", (name or "client").strip().lower()).strip("-")
    return slug[:48] or "client"


def resolve_client_dir(client_id: str) -> Path:
    folder = CLIENTS_DIR / client_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def client_session_path(client_id: str) -> Path:
    return resolve_client_dir(client_id) / "session_state.json"


def client_org_assets_dir(client_id: str) -> Path:
    folder = resolve_client_dir(client_id) / "org_assets"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def client_evidence_dir(client_id: str) -> Path:
    folder = resolve_client_dir(client_id) / "evidence"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def list_clients() -> List[Dict[str, str]]:
    manifest = _load_manifest()
    clients = manifest.get("clients") or []
    if not clients:
        ensure_default_client()
        manifest = _load_manifest()
        clients = manifest.get("clients") or []
    return clients


def active_client_id() -> str:
    manifest = _load_manifest()
    cid = manifest.get("active_client_id") or DEFAULT_CLIENT_ID
    if not client_session_path(cid).parent.exists():
        ensure_default_client()
        return DEFAULT_CLIENT_ID
    return cid


def set_active_client_id(client_id: str) -> None:
    manifest = _load_manifest()
    manifest["active_client_id"] = client_id
    _save_manifest(manifest)


def create_client(display_name: str) -> str:
    name = (display_name or "New client").strip()
    base = slugify_client_name(name)
    manifest = _load_manifest()
    clients = manifest.get("clients") or []
    existing = {c["id"] for c in clients}
    client_id = base
    n = 2
    while client_id in existing:
        client_id = f"{base}-{n}"
        n += 1
    clients.append(
        {
            "id": client_id,
            "name": name,
            "created": datetime.now().strftime("%Y-%m-%d"),
        }
    )
    manifest["clients"] = clients
    manifest["active_client_id"] = client_id
    _save_manifest(manifest)
    resolve_client_dir(client_id)
    client_org_assets_dir(client_id)
    return client_id


def rename_client(client_id: str, new_name: str) -> None:
    manifest = _load_manifest()
    for item in manifest.get("clients") or []:
        if item["id"] == client_id:
            item["name"] = (new_name or item["name"]).strip()
            break
    _save_manifest(manifest)


def delete_client(client_id: str) -> bool:
    if client_id == DEFAULT_CLIENT_ID:
        return False
    manifest = _load_manifest()
    clients = [c for c in manifest.get("clients") or [] if c["id"] != client_id]
    if len(clients) == len(manifest.get("clients") or []):
        return False
    client_dir = resolve_client_dir(client_id)
    if client_dir.exists():
        backup_dir = DATA_DIR / "_deleted_clients"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{client_id}_{uuid.uuid4().hex[:8]}.tar.gz"
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(client_dir, arcname=client_id)
    shutil.rmtree(client_dir, ignore_errors=True)
    manifest["clients"] = clients
    if manifest.get("active_client_id") == client_id:
        manifest["active_client_id"] = clients[0]["id"] if clients else DEFAULT_CLIENT_ID
    _save_manifest(manifest)
    return True


def ensure_default_client() -> None:
    """Create default client; migrate legacy single-user session_state.json if present."""
    CLIENTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()
    clients = manifest.get("clients") or []
    default_dir = resolve_client_dir(DEFAULT_CLIENT_ID)
    legacy = resolve_session_state_path()

    if not any(c["id"] == DEFAULT_CLIENT_ID for c in clients):
        label = "Default workspace"
        if legacy.exists():
            try:
                data = json.loads(legacy.read_text(encoding="utf-8"))
                label = (data.get("org_profile") or {}).get("org_name") or data.get("org_name") or label
            except (json.JSONDecodeError, OSError):
                pass
        clients.insert(0, {"id": DEFAULT_CLIENT_ID, "name": label, "created": datetime.now().strftime("%Y-%m-%d")})

    target = client_session_path(DEFAULT_CLIENT_ID)
    if legacy.exists() and not target.exists():
        shutil.copy2(legacy, target)
        legacy_org = DATA_DIR / "org_assets"
        client_org = client_org_assets_dir(DEFAULT_CLIENT_ID)
        if legacy_org.is_dir() and any(legacy_org.iterdir()):
            for item in legacy_org.iterdir():
                dest = client_org / item.name
                if item.is_file() and not dest.exists():
                    shutil.copy2(item, dest)

    manifest["clients"] = clients
    if not manifest.get("active_client_id"):
        manifest["active_client_id"] = DEFAULT_CLIENT_ID
    _save_manifest(manifest)


def client_label(client_id: str) -> str:
    for item in list_clients():
        if item["id"] == client_id:
            return item.get("name") or client_id
    return client_id
