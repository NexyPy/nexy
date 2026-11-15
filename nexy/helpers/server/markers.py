"""The small files `__nexy__/` keeps for one project: ports, the prod flag, the build marker."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from nexy.helpers.fs.vfs import VFS

_PRODUCTION_MARKER = Path("__nexy__") / "nexy.prod"
_BUILD_MARKER = Path("__nexy__") / "build.json"


def write_port_file(name: str, port: int) -> None:
    """Save the port used for inter-process communication."""
    VFS().write(f"__nexy__/{name}.port", str(port))


def set_production(active: bool) -> None:
    """Create the marker that tells `Vite()` to serve the built client, or remove it."""
    if not active:
        _PRODUCTION_MARKER.unlink(missing_ok=True)
        return
    _PRODUCTION_MARKER.parent.mkdir(parents=True, exist_ok=True)
    _PRODUCTION_MARKER.write_text("1", encoding="utf-8")


def write_build_marker(version: str) -> None:
    """Record that `nexy build` finished, and with which Nexy, for `nexy start` to check."""
    marker = {"version": version, "built_at": datetime.now(UTC).isoformat(timespec="seconds")}
    _BUILD_MARKER.parent.mkdir(parents=True, exist_ok=True)
    _BUILD_MARKER.write_text(json.dumps(marker) + "\n", encoding="utf-8")


def has_build() -> bool:
    """True once `nexy build` has finished in this project."""
    return _BUILD_MARKER.is_file()
