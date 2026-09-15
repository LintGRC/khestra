"""General-purpose evidence file store — write/read/manifest by asset ID.

Replaces per-app copies of evidence_store.py across CMMC, SOC2, and AI Gov.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

from kevidence.config import get_data_dir
from kevidence.crypto import get_hmac_key, sign_manifest, verify_manifest_signature

_log = logging.getLogger("evidence.filestore")
_HMAC_SIG_KEY = "hmac_signature"

MANIFEST_NAME = "manifest.json"
ALLOWED_EXTENSIONS = frozenset(
    {".pdf", ".png", ".jpg", ".jpeg", ".json", ".conf", ".txt", ".csv", ".docx", ".xlsx", ".md", ".log"}
)
MAX_EVIDENCE_MB = 50


def _evidence_root() -> Path:
    return get_data_dir() / "evidence"


def evidence_file_key(asset_id: str, filename: str) -> str:
    return f"{asset_id}_{safe_evidence_filename(filename)}"


def safe_evidence_filename(name: str) -> str:
    base = (name or "file").replace("\\", "/").split("/")[-1]
    base = "".join(c for c in base if c.isalnum() or c in "._- ")
    return base[:200] or "evidence_file"


def _disk_name(file_key: str) -> str:
    return re.sub(r"[^\w\-]+", "_", file_key)[:220]


def get_evidence_bytes(
    asset_id: str,
    ev: Dict[str, Any],
    restored_evidence: Optional[Dict[str, bytes]] = None,
    *,
    evidence_dir: Optional[Path] = None,
) -> Optional[bytes]:
    if ev.get("data_bytes"):
        return ev["data_bytes"]
    key = evidence_file_key(asset_id, ev.get("filename", ""))
    if restored_evidence and key in restored_evidence:
        return restored_evidence[key]
    if evidence_dir is not None:
        return read_evidence_file_from_disk(evidence_dir, asset_id, ev.get("filename", ""))
    return None


def _load_manifest(folder: Path, skip_hmac: bool = False) -> Optional[dict]:
    manifest_path = folder / MANIFEST_NAME
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(raw, dict):
        return None
    sig = raw.pop(_HMAC_SIG_KEY, None)
    if not skip_hmac and sig:
        hmac_key = get_hmac_key(get_data_dir())
        manifest_json = json.dumps(raw, indent=2)
        if not verify_manifest_signature(manifest_json.encode(), sig, hmac_key):
            _log.error("Manifest HMAC verification failed for %s — rejecting", folder)
            return None
    elif not skip_hmac and not sig:
        _log.warning("Manifest has no HMAC signature — legacy file")
    return raw


def read_evidence_file_from_disk(
    folder: Path,
    asset_id: str,
    filename: str,
) -> Optional[bytes]:
    """Read a single evidence file without loading the full manifest into memory."""
    manifest = _load_manifest(folder)
    if manifest is None:
        return None
    target_key = evidence_file_key(asset_id, filename)
    for disk_name, meta in manifest.items():
        file_key = meta.get("file_key") or evidence_file_key(
            meta.get("asset_id", meta.get("control_id", "")), meta.get("filename", "")
        )
        if file_key != target_key:
            continue
        path = folder / disk_name
        if not path.is_file():
            continue
        try:
            resolved = path.resolve()
            if not resolved.is_relative_to(folder.resolve()):
                _log.error("Path traversal blocked: %s is outside %s", disk_name, folder)
                continue
        except (ValueError, OSError):
            _log.warning("Path resolution failed for %s", disk_name)
            continue
        data = path.read_bytes()
        expected_sha = meta.get("sha256", "")
        if expected_sha:
            actual = hashlib.sha256(data).hexdigest().lower()
            if actual != expected_sha.lower():
                _log.error("Evidence hash mismatch for %s — expected %s, got %s", disk_name, expected_sha, actual)
                return None
        return data
    return None


def metadata_without_bytes(items: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    """Strip binary data from evidence entries for JSON-safe serialization."""
    return [{k: v for k, v in ev.items() if k != "data_bytes"} for ev in items]


def answers_without_evidence_bytes(answers: Dict[str, Any]) -> Dict[str, Any]:
    """JSON-safe copy of control answers — strips binary data; bytes live in evidence/ on disk."""
    clean: Dict[str, Any] = {}
    for cid, ans in answers.items():
        row = dict(ans)
        evs = []
        for ev in ans.get("evidence") or []:
            evs.append({k: v for k, v in ev.items() if k != "data_bytes"})
        row["evidence"] = evs
        clean[cid] = row
    return clean


def persist_evidence_to_disk(
    folder: Path,
    entries: list[Dict[str, Any]],
    asset_id: str,
    restored_evidence: Optional[Dict[str, bytes]] = None,
) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    restored = restored_evidence or {}
    manifest: Dict[str, Dict[str, str]] = {}
    seen_keys: set[str] = set()

    for ev in entries:
        fname = ev.get("filename") or ""
        if not fname:
            continue
        key = evidence_file_key(asset_id, fname)
        data = ev.get("data_bytes") or restored.get(key)
        if not data:
            continue
        disk = _disk_name(key)
        (folder / disk).write_bytes(data)
        manifest[disk] = {
            "file_key": key,
            "asset_id": asset_id,
            "filename": fname,
            "sha256": ev.get("sha256", ""),
        }
        seen_keys.add(disk)

    manifest_json = json.dumps(manifest, indent=2)
    hmac_key = get_hmac_key(get_data_dir())
    sig = sign_manifest(manifest_json.encode(), hmac_key)
    manifest_signed = json.loads(manifest_json)
    manifest_signed[_HMAC_SIG_KEY] = sig
    (folder / MANIFEST_NAME).write_text(json.dumps(manifest_signed, indent=2), encoding="utf-8")


def load_evidence_from_disk(folder: Path) -> Dict[str, bytes]:
    manifest = _load_manifest(folder)
    if manifest is None:
        return {}
    out: Dict[str, bytes] = {}
    for disk_name, meta in manifest.items():
        path = folder / disk_name
        if not path.is_file():
            continue
        try:
            resolved = path.resolve()
            if not resolved.is_relative_to(folder.resolve()):
                _log.error("Path traversal blocked: %s is outside %s", disk_name, folder)
                continue
        except (ValueError, OSError):
            _log.warning("Path resolution failed for %s", disk_name)
            continue
        asset_id = meta.get("asset_id", meta.get("control_id", ""))
        file_key = meta.get("file_key") or evidence_file_key(asset_id, meta.get("filename", ""))
        out[file_key] = path.read_bytes()
        expected_sha = meta.get("sha256", "")
        if expected_sha:
            actual = hashlib.sha256(out[file_key]).hexdigest().lower()
            if actual != expected_sha.lower():
                _log.error("Evidence hash mismatch for %s in manifest", disk_name)
                del out[file_key]
    return out


def verify_evidence_hash(ev: Dict[str, Any], data: bytes) -> bool:
    expected = (ev.get("sha256") or "").strip().lower()
    if not expected:
        return False
    actual = hashlib.sha256(data).hexdigest().lower()
    return actual == expected


def allowed_extension(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def within_size_limit(data: bytes) -> bool:
    return len(data) <= MAX_EVIDENCE_MB * 1024 * 1024
