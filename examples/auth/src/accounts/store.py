"""The accounts, kept in SQLite. A password is never stored: only a salted scrypt hash of it."""

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

DATABASE = Path(os.environ.get("AUTH_DB", "auth.db"))
SHORTEST_PASSWORD = 8
LONGEST_PASSWORD = 256  # scrypt is slow on purpose: a megabyte of password must not reach it
_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s.]+")


@dataclass(frozen=True)
class Account:
    id: int
    email: str
    created_at: str


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE)
    connection.execute(
        "create table if not exists account (id integer primary key, email text unique not null,"
        " password_hash text not null, created_at text not null)"
    )
    return connection


def hash_password(password: str) -> str:
    """A hash made slow on purpose, with a salt of its own, so two equal passwords differ."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{digest.hex()}"


def _matches(password: str, stored: str) -> bool:
    salt, digest = stored.split(":")
    found = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
    return hmac.compare_digest(found.hex(), digest)  # a time that tells nothing


def _password_problem(password: str) -> str:
    return "" if SHORTEST_PASSWORD <= len(password) <= LONGEST_PASSWORD else "password"


def create(email: str, password: str) -> tuple[Account | None, str]:
    """The new account and "", or None and the key of what was wrong."""
    email = email.strip().lower()
    if not _EMAIL.fullmatch(email):
        return None, "email"
    if problem := _password_problem(password):
        return None, problem
    created = datetime.now(UTC).date().isoformat()
    with closing(_connect()) as connection:
        try:
            cursor = connection.execute(
                "insert into account (email, password_hash, created_at) values (?, ?, ?)",
                (email, hash_password(password), created),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            return None, "taken"
    return Account(cursor.lastrowid or 0, email, created), ""


_SELECT = "select id, email, created_at, password_hash from account"
_BY = {"id": f"{_SELECT} where id = ?", "email": f"{_SELECT} where email = ?"}


def _row(column: str, value: object) -> tuple[int, str, str, str] | None:
    """One account by its id or its email; the queries are written out, never built from input."""
    with closing(_connect()) as connection:
        return connection.execute(_BY[column], (value,)).fetchone()


def find(account_id: int) -> Account | None:
    row = _row("id", account_id)
    return Account(*row[:3]) if row else None


def authenticate(email: str, password: str) -> Account | None:
    """The account when the password is its own; None for a wrong password or an unknown email."""
    row = _row("email", email.strip().lower())
    if row is None or len(password) > LONGEST_PASSWORD or not _matches(password, row[3]):
        return None
    return Account(*row[:3])


def change_password(account_id: int, current: str, new: str) -> str:
    """Change a password, given the current one. Returns the key of what was wrong, or ""."""
    row = _row("id", account_id)
    if row is None or len(current) > LONGEST_PASSWORD or not _matches(current, row[3]):
        return "current"
    if problem := _password_problem(new):
        return problem
    with closing(_connect()) as connection:
        connection.execute(
            "update account set password_hash = ? where id = ?", (hash_password(new), account_id)
        )
        connection.commit()
    return ""
