"""Hash and check a password with scrypt: slow on purpose, with a random salt per password."""

import hashlib
import hmac
import secrets


def _scrypt(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    return f"{salt.hex()}:{_scrypt(password, salt).hex()}"


def password_matches(password: str, stored: str) -> bool:
    salt, digest = stored.split(":")
    return hmac.compare_digest(_scrypt(password, bytes.fromhex(salt)).hex(), digest)
