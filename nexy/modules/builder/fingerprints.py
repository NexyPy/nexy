"""What tells a build that a route file, or the configuration around it, has changed."""

from __future__ import annotations

from pathlib import Path

from nexy.core.config import Config
from nexy.helpers.fs.fingerprint import first_stat_fingerprint, stat_fingerprint

_layout_chain_cache: dict[str, str] = {}

_LAYOUT_ROOT: Path | None = None
_LAYOUT_LIMIT: Path | None = None


def _layout_bounds() -> tuple[Path, Path]:
    global _LAYOUT_ROOT, _LAYOUT_LIMIT
    if _LAYOUT_ROOT is None:
        root = Path(Config.ROUTER_PATH).resolve()
        _LAYOUT_ROOT = root
        _LAYOUT_LIMIT = root.parent
    return _LAYOUT_ROOT, _LAYOUT_LIMIT or _LAYOUT_ROOT


def layout_chain_fingerprint(directory: Path) -> str:
    """Fingerprint of every layout.* wrapping this directory, cached per dir."""
    key = directory.as_posix()
    if key in _layout_chain_cache:
        return _layout_chain_cache[key]
    root, limit = _layout_bounds()
    parts: list[str] = []
    current = directory
    while str(current).startswith(str(limit)):
        for name in Config.LAYOUT_FILE_NAMES:
            layout_file = current / name
            if layout_file.is_file():
                lst = layout_file.stat()
                parts.append(f"L{layout_file.as_posix()}:{lst.st_mtime_ns}:{lst.st_size}")
        if current in (root, limit):
            break
        current = current.parent
    chain = "|".join(parts)
    _layout_chain_cache[key] = chain
    return chain


def file_fingerprint(file_path: Path) -> str:
    """Change fingerprint of a route file: stat plus its layout chain."""
    base = stat_fingerprint(file_path)
    if not base:
        return ""
    chain = layout_chain_fingerprint(file_path.parent.resolve())
    return base + (f"|{chain}" if chain else "")


def config_fingerprint() -> str:
    """Config drives compile behaviour (layouts, aliases, FF) - any change
    must invalidate the whole build cache."""
    return first_stat_fingerprint(
        ("nexyconfig.py", "nexyconfig.example.py", "nexyconfig.toml", "pyproject.toml")
    )
