import json
import os
from functools import cache
from pathlib import Path
from typing import Any

from nexy.core.config import Config

_CLIENT = Path("__nexy__/client")
_MANIFEST = _CLIENT / ".vite" / "manifest.json"
_PRODUCTION_MARKER = Path("__nexy__/nexy.prod")
_HMR_CLIENT = Path(__file__).parent / "modules" / "runtime" / "hmr_client.html"
_ENTRY_KEYS = ("__nexy__/main.ts", "/__nexy__/main.ts")


def Vite() -> str:
    """Return the client tags to prepend to every page.

    Dev mode serves the reload WebSocket script (with the compile-error overlay) on
    its own, plus the Vite client when the project actually runs Vite; prod mode
    inlines or links the built client from the Vite manifest.

    Returns:
        The `<script>` (and CSS) markup for the current mode. The reload channel is
        served even without a vite.config.ts or with Vite disabled, so every kind of
        project gets live reload; the Vite tags only appear when Vite runs.
    """
    running = os.path.exists("vite.config.ts") and Config().useVite
    if _PRODUCTION_MARKER.is_file():
        return _production_tags() if running else ""
    if running:
        return _development_tags()
    return _hmr_client()


@cache
def _hmr_client() -> str:
    return _HMR_CLIENT.read_text(encoding="utf-8")


# In development the stylesheet reaches the page through JavaScript, after the first paint. The
# page stays hidden until main.ts has run (its styles are in by then); the timer is the way out if
# it never does, so a broken client cannot leave a blank page.
BOOT_GATE_ID = "nexy-boot"
_BOOT_GATE = (
    f'<style id="{BOOT_GATE_ID}">html{{visibility:hidden}}</style>'
    f'<script>setTimeout(function(){{var g=document.getElementById("{BOOT_GATE_ID}");'
    "g&&g.remove()},2500)</script>"
)


def _development_tags() -> str:
    return f"""
    {_BOOT_GATE}
    {_hmr_client()}
    <script type="module" src="/@vite/client"></script>
    <script type="module" src="/__nexy__/main.ts"></script>
    """


def _production_tags() -> str:
    """The built client's tags; empty when it is missing, never the dev script."""
    try:
        entry = _entry()
        if entry is None:
            return ""
        return _inline_tags(entry) if _inline_requested() else _linked_tags(entry)
    except Exception:
        return ""


def _entry() -> dict[str, Any] | None:
    """The manifest entry of the client bundle, or None when there is no manifest or no entry."""
    if not _MANIFEST.is_file():
        return None
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    entry = next((data[key] for key in _ENTRY_KEYS if data.get(key)), None)
    return entry if entry and "file" in entry else None


def _inline_requested() -> bool:
    return os.getenv("NEXY_INLINE_CLIENT", "").strip() in ("1", "true", "TRUE")


def _built_file(name: str) -> Path:
    return _CLIENT.joinpath(name.lstrip("/"))


def _read_if_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _inline_tags(entry: dict[str, Any]) -> str:
    styles = "".join(
        f"<style>{_read_if_file(_built_file(name))}</style>"
        for name in entry.get("css") or []
        if _built_file(name).is_file()
    )
    code = _read_if_file(_built_file(entry["file"]))
    return f'{styles}<script type="module">\n{code}\n</script>'


def _linked_tags(entry: dict[str, Any]) -> str:
    links = "".join(
        f'<link rel="stylesheet" href="/{name.lstrip("/")}" />' for name in entry.get("css") or []
    )
    return f'{links}<script type="module" src="/{entry["file"].lstrip("/")}"></script>'
