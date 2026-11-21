"""Slows down guessing: after LIMIT wrong passwords for one email in WINDOW seconds, that email
cannot sign in until the oldest of them is older than the window. Kept in memory: a restart, or a
second server process, starts again from zero. A site with several processes keeps this in a
shared store instead."""

import time

LIMIT = 5
WINDOW = 15 * 60
FAILURES: dict[str, list[float]] = {}


def _recent(email: str, now: float) -> list[float]:
    kept = [at for at in FAILURES.get(email, []) if now - at < WINDOW]
    FAILURES[email] = kept
    return kept


def blocked(email: str, now: float | None = None) -> bool:
    return len(_recent(email, time.monotonic() if now is None else now)) >= LIMIT


def failed(email: str, now: float | None = None) -> None:
    at = time.monotonic() if now is None else now
    _recent(email, at).append(at)


def succeeded(email: str) -> None:
    FAILURES.pop(email, None)
