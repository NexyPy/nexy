"""Removing files and folders, including the read-only ones Git leaves behind on Windows."""

from __future__ import annotations

import os
import shutil
import stat
from collections.abc import Callable
from pathlib import Path
from typing import Any


def _make_writable_and_retry(
    function: Callable[[str], Any], path: str, _exc_info: tuple[object, ...]
) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def remove_tree(path: Path) -> None:
    """Delete a folder; a read-only entry is made writable and deleted too."""
    shutil.rmtree(path, onerror=_make_writable_and_retry)


def remove_path(path: Path) -> None:
    """Delete a file, or a folder with what it holds."""
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink()
