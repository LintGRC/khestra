"""Password hashing via hashlib.pbkdf2_hmac — zero external dependencies."""

import hashlib
import hmac as _hmac
import os


_HASH_ALGO = "sha256"
_SALT_LENGTH = 32
_ITERATIONS = 600_000


def hash_password(plain: str) -> str:
    salt = os.urandom(_SALT_LENGTH)
    dk = hashlib.pbkdf2_hmac(_HASH_ALGO, plain.encode("utf-8"), salt, _ITERATIONS)
    return f"{_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(plain: str, stored: str) -> bool:
    try:
        parts = stored.split("$")
        if len(parts) != 3:
            return False
        iterations = int(parts[0])
        salt = bytes.fromhex(parts[1])
        expected = bytes.fromhex(parts[2])
        dk = hashlib.pbkdf2_hmac(_HASH_ALGO, plain.encode("utf-8"), salt, iterations)
        return _hmac.compare_digest(dk, expected)
    except (ValueError, IndexError):
        return False
