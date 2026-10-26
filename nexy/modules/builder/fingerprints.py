"""What tells a build that a route file, or the configuration around it, has changed."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from nexy.core.config import Config
from nexy.helpers.fs.ancestors import walk_up
from nexy.helpers.fs.fingerprint import first_stat_fingerprint, stat_fingerprint

_layout_chain_cache: dict[str, str] = {}


def _layout_stamps(directory: Path, limit: Path) -> Iterator[str]:
    """One ``path:mtime:size`` stamp for each layout file from *directory* up to *limit*."""
    for current in walk_up(directory, limit):
        for name in Config.LAYOUT_FILE_NAMES:
            layout = current / name
            if layout.is_file():
                stat = layout.stat()
                yield f"L{layout.as_posix()}:{stat.st_mtime_ns}:{stat.st_size}"


def layout_chain_fingerprint(directory: Path) -> str:
    """Fingerprint of every layout.* wrapping this directory, cached per dir.

    It climbs as far as the layout lookup does (the folder that holds the routes), so a layout
    placed there invalidates the pages below it.
    """
    key = directory.as_posix()
    if key not in _layout_chain_cache:
        limit = Path(Config.ROUTER_PATH).resolve().parent
        _layout_chain_cache[key] = "|".join(_layout_stamps(directory, limit))
    return _layout_chain_cache[key]


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
