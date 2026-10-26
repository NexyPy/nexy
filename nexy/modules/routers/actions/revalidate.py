"""Tell the browser which pages an action made stale."""

from __future__ import annotations

from contextvars import ContextVar

HEADER = "x-nexy-revalidate"

_paths: ContextVar[list[str] | None] = ContextVar("nexy_revalidate", default=None)


def revalidate(*paths: str) -> None:
    """Ask the browser to reload the data of *paths* (the current page when none is given).

    Call it inside an `@Action`; outside one it does nothing.
    """
    pending = _paths.get()
    if pending is not None:
        pending.extend(paths or ("*",))


def start_collecting() -> list[str]:
    """Begin recording the `revalidate` calls of one action; returns the list they fill."""
    collected: list[str] = []
    _paths.set(collected)
    return collected


def header_value(paths: list[str]) -> str:
    return ",".join(dict.fromkeys(paths))
