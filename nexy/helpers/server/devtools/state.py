"""What the toolbar asks the server for: its routes, the errors it raised, the configuration."""

from __future__ import annotations

from collections import deque
from typing import Any

from fastapi import FastAPI

from nexy.helpers.server.devtools import STATE_PATH, source_of

# Newest first; the toolbar shows these next to the errors the browser raised.
RECENT: deque[dict[str, str]] = deque(maxlen=20)

_CONFIG_KEYS = (
    "useTitle",
    "useCSR",
    "useVite",
    "useFF",
    "useBadge",
    "useDevTools",
    "useWorkers",
    "ALIASES",
)
_HIDDEN_METHODS = {"HEAD", "OPTIONS"}


def record_error(kind: str, message: str, where: str, reference: str) -> None:
    RECENT.appendleft({"kind": kind, "message": message, "where": where, "reference": reference})


def routes_of(server: FastAPI) -> list[dict[str, Any]]:
    """The routes of the application, without Nexy's own."""
    found = []
    for route in server.routes:
        path = getattr(route, "path", "")
        if not path or path.startswith("/_nexy"):
            continue
        methods = sorted(set(_methods(route)) - _HIDDEN_METHODS)
        name = getattr(route, "name", "")
        found.append({"path": path, "methods": methods, "name": name, **source_of(route)})
    return found


def _methods(route: object) -> list[str]:
    declared = getattr(route, "methods", None)
    if declared:
        return list(declared)
    return ["WS"] if "WebSocket" in type(route).__name__ else ["FILES"]


def config_of(config: object) -> dict[str, Any]:
    return {key: _plain(getattr(config, key, None)) for key in _CONFIG_KEYS}


def _plain(value: Any) -> Any:
    if isinstance(value, (bool, int, float, str, dict)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return type(value).__name__


def setup_devtools(server: FastAPI, config: object) -> None:
    """Mount the endpoint the toolbar reads; development only."""

    @server.get(STATE_PATH, include_in_schema=False)
    async def devtools_state() -> dict[str, Any]:
        return {
            "routes": routes_of(server),
            "errors": list(RECENT),
            "config": config_of(config),
        }
