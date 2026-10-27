"""The small files `__nexy__/` keeps for the processes of one project: ports and the prod flag."""

from __future__ import annotations

from pathlib import Path

from nexy.helpers.fs.vfs import VFS

_PRODUCTION_MARKER = Path("__nexy__") / "nexy.prod"


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
