"""Packages in the virtual file system: an empty ``__init__.py`` for every folder of a path."""

from __future__ import annotations

from nexy.helpers.fs.vfs import VFS


def write_package_inits(vfs: VFS, directory: str) -> None:
    """Write an empty ``__init__.py`` for *directory* and each of its ancestors that has none.

    Compiled modules in subfolders (``demo/slug_catch_all.py``) then import as Python packages.
    """
    parts = directory.replace("\\", "/").split("/")
    for depth in range(1, len(parts) + 1):
        init_file = "/".join(parts[:depth]) + "/__init__.py"
        if not vfs.exists(init_file):
            vfs.write(init_file, "")
