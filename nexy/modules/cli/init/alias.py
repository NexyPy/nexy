"""The import alias of a new project: `@` by default, any other prefix on request.

The templates are written with `@/`; a project that chose another alias gets the same files
with that prefix, in its sources, its tsconfig and its nexyconfig.
"""

from __future__ import annotations

import re
from pathlib import Path

from nexy.modules.i18n import t

DEFAULT_ALIAS = "@"
_VALID = re.compile(r"^[@~#$][A-Za-z0-9_-]*$")
_SOURCES = (".nexy", ".tsx", ".ts", ".jsx", ".vue", ".svelte", ".mdx", ".md")


def validate_alias(value: str) -> bool | str:
    """True for a prefix like `@`, `~` or `#app`; otherwise the message to show."""
    if _VALID.match(value.strip()):
        return True
    return t(
        "init.alias_invalid",
        "Use @, ~, # or $, optionally followed by letters (for example ~ or @app).",
    )


def _rewrite(path: Path, pairs: tuple[tuple[str, str], ...]) -> None:
    text = path.read_bytes().decode("utf-8")
    result = text
    for old, new in pairs:
        result = result.replace(old, new)
    if result != text:
        path.write_bytes(result.encode("utf-8"))


def apply_alias(dest: Path, alias: str) -> None:
    """Rewrite the scaffold in *dest* so its import alias is *alias*."""
    alias = alias.strip()
    if alias == DEFAULT_ALIAS:
        return
    quotes = (('"@/', f'"{alias}/'), ("'@/", f"'{alias}/"))
    for path in sorted((dest / "src").rglob("*")):
        if path.is_file() and path.suffix in _SOURCES:
            _rewrite(path, quotes)
    for name, pairs in (
        ("tsconfig.json", ((f'"{DEFAULT_ALIAS}/*"', f'"{alias}/*"'),)),
        ("nexyconfig.py", (('{"@": ', f'{{"{alias}": '),)),
    ):
        if (dest / name).is_file():
            _rewrite(dest / name, pairs)
