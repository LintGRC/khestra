"""Organization-level SSP assets — topology diagrams and appendix file references."""

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from security_utils import safe_evidence_filename

TOPOLOGY_KEY = "topology"
APPENDIX_PREFIX = "appendix:"


def default_org_assets() -> Dict[str, Any]:
    return {
        "topology_filename": "",
        "appendix_files": [],  # [{"filename": str, "label": str}]
    }


def merge_org_assets(stored: Dict[str, Any] | None) -> Dict[str, Any]:
    assets = default_org_assets()
    if stored:
        assets["topology_filename"] = stored.get("topology_filename") or ""
        files = stored.get("appendix_files") or []
        assets["appendix_files"] = [
            {"filename": f.get("filename", ""), "label": f.get("label", "")}
            for f in files
            if f.get("filename")
        ]
    return assets


def asset_storage_key(kind: str, filename: str) -> str:
    safe = safe_evidence_filename(filename)
    if kind == TOPOLOGY_KEY:
        return f"{TOPOLOGY_KEY}:{safe}"
    return f"{APPENDIX_PREFIX}{safe}"


def set_topology_bytes(session_bytes: Dict[str, bytes], filename: str, data: bytes) -> None:
    session_bytes[asset_storage_key(TOPOLOGY_KEY, filename)] = data


def get_topology_bytes(
    org_assets: Dict[str, Any], session_bytes: Dict[str, bytes]
) -> Optional[tuple[str, bytes]]:
    name = org_assets.get("topology_filename") or ""
    if not name:
        return None
    key = asset_storage_key(TOPOLOGY_KEY, name)
    data = session_bytes.get(key)
    if data:
        return name, data
    return None


def add_appendix_file(
    org_assets: Dict[str, Any],
    session_bytes: Dict[str, bytes],
    filename: str,
    data: bytes,
    label: str = "",
) -> Dict[str, Any]:
    assets = deepcopy(org_assets)
    safe = safe_evidence_filename(filename)
    files: List[Dict[str, str]] = list(assets.get("appendix_files") or [])
    files = [f for f in files if f.get("filename") != safe]
    files.append({"filename": safe, "label": (label or safe).strip()})
    assets["appendix_files"] = files
    session_bytes[asset_storage_key("appendix", safe)] = data
    return assets


def remove_topology(org_assets: Dict[str, Any], session_bytes: Dict[str, bytes]) -> Dict[str, Any]:
    assets = deepcopy(org_assets)
    name = assets.get("topology_filename") or ""
    if name:
        session_bytes.pop(asset_storage_key(TOPOLOGY_KEY, name), None)
    assets["topology_filename"] = ""
    return assets


def remove_appendix(
    org_assets: Dict[str, Any], session_bytes: Dict[str, bytes], filename: str
) -> Dict[str, Any]:
    assets = deepcopy(org_assets)
    safe = safe_evidence_filename(filename)
    session_bytes.pop(asset_storage_key("appendix", safe), None)
    assets["appendix_files"] = [
        f for f in assets.get("appendix_files", []) if f.get("filename") != safe
    ]
    return assets


def _disk_name(storage_key: str) -> str:
    return storage_key.replace(":", "__")


def storage_key_from_disk_name(filename: str) -> str:
    return filename.replace("__", ":", 1)


def persist_org_assets_to_disk(
    org_assets: Dict[str, Any],
    org_asset_bytes: Dict[str, bytes],
    folder: Optional["Path"] = None,
) -> None:
    import json
    from pathlib import Path

    from config import resolve_org_assets_dir

    folder = folder or resolve_org_assets_dir()
    (folder / "manifest.json").write_text(json.dumps(org_assets, indent=2), encoding="utf-8")
    for key, data in org_asset_bytes.items():
        (folder / _disk_name(key)).write_bytes(data)


def load_org_assets_from_disk(folder: Optional["Path"] = None) -> tuple[Dict[str, Any], Dict[str, bytes]]:
    import json
    from pathlib import Path

    from config import resolve_org_assets_dir

    folder = folder or resolve_org_assets_dir()
    manifest = folder / "manifest.json"
    if not manifest.exists():
        return default_org_assets(), {}
    org_assets = merge_org_assets(json.loads(manifest.read_text(encoding="utf-8")))
    blobs: Dict[str, bytes] = {}
    for path in folder.iterdir():
        if path.name == "manifest.json":
            continue
        if path.is_file():
            blobs[storage_key_from_disk_name(path.name)] = path.read_bytes()
    return org_assets, blobs
