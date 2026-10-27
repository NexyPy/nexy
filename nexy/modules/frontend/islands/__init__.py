"""The browser scripts that mount a framework's components in server-rendered pages.

Each script lives in a real ``.js`` file next to this module, so it can be read, linted and
tested as JavaScript. `ISLANDS_RUNTIME` (islands.js) is shared by all of them: selective
hydration honoring Astro-style ``client:`` directives. The default stays eager (client:load);
client:idle, client:visible and client:media defer hydration.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path


@cache
def script(name: str) -> str:
    """The text of ``<name>.js``, read once."""
    return (Path(__file__).parent / f"{name}.js").read_text(encoding="utf-8")


ISLANDS_RUNTIME = script("islands")

__all__ = ["ISLANDS_RUNTIME", "script"]
