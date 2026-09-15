"""Encryption helpers for credential storage at rest (open side)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger("evidence.crypto")

_KEY_FILENAME = ".enc_key"


def _key_path(data_dir: Path) -> Path:
    return data_dir / _KEY_FILENAME


def _restrict_permissions(path: Path) -> None:
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def get_or_create_key(data_dir: Path) -> bytes:
    path = _key_path(data_dir)
    if path.is_file():
        try:
            key = path.read_bytes()
            Fernet(key)
            return key
        except (ValueError, InvalidToken, OSError) as exc:
            logger.warning("Corrupt encryption key at %s — regenerating: %s", path, exc)
    path.parent.mkdir(parents=True, exist_ok=True)
    key = Fernet.generate_key()
    path.write_bytes(key)
    _restrict_permissions(path)
    return key


def encrypt_value(plaintext: str, key: bytes) -> str:
    if not plaintext:
        return ""
    f = Fernet(key)
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(token: str, key: bytes) -> str:
    if not token:
        return ""
    f = Fernet(key)
    try:
        return f.decrypt(token.encode()).decode()
    except (InvalidToken, ValueError):
        logger.warning("Failed to decrypt value, returning raw")
        return token


def is_encrypted(value: str) -> bool:
    return bool(value) and value.startswith("gAAAAA")


def set_restricted_permissions(path: Path) -> None:
    _restrict_permissions(path)


def get_hmac_key(data_dir: Path) -> bytes:
    key = get_or_create_key(data_dir)
    return hashlib.sha256(b"khestra-evidence-hmac-v1:" + key).digest()


def sign_manifest(data: bytes, hmac_key: bytes) -> str:
    return hmac.new(hmac_key, data, hashlib.sha256).hexdigest()


def verify_manifest_signature(data: bytes, signature: str, hmac_key: bytes) -> bool:
    expected = sign_manifest(data, hmac_key)
    return hmac.compare_digest(expected, signature)


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".tmp.{os.getpid()}")
    try:
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        _restrict_permissions(tmp)
        tmp.rename(path)
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise


@contextmanager
def file_lock(target: Path):
    """Exclusive advisory lock guarding read-modify-write on shared state files.

    The evidence store is shared across app processes — serializing whole
    load→merge→save cycles prevents lost updates when two apps write at once.
    """
    import fcntl

    target.parent.mkdir(parents=True, exist_ok=True)
    lock_path = target.with_suffix(target.suffix + ".lock")
    with open(lock_path, "a+") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
