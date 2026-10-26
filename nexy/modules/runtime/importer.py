import importlib.abc
import importlib.machinery
import importlib.util
import sys
from collections.abc import Sequence

from nexy.helpers.fs.vfs import VFS


class NexyVFSLoader(importlib.abc.SourceLoader):
    def __init__(self, path: str) -> None:
        self.path = path
        self.vfs = VFS()

    def get_filename(self, _fullname: str) -> str:
        return self.path

    def get_data(self, path: str) -> bytes:
        return self.vfs.read(path).encode("utf-8")


# What a compiled module can be stored as: a module, a .nexy, or a package.
_CANDIDATES = ((".py", False), (".nexy", False), ("/__init__.py", True))


class NexyVFSFinder(importlib.abc.MetaPathFinder):
    def __init__(self) -> None:
        self.vfs = VFS()

    def _find_vfs_path(self, base_path: str) -> str | None:
        if self.vfs.exists(base_path):
            return base_path
        candidates = [
            base_path.lower(),
            base_path.upper(),
            base_path.replace("_", "-"),
            base_path.replace("-", "_"),
        ]
        for candidate in candidates:
            if self.vfs.exists(candidate):
                return candidate
        for fname in self.vfs.list_files():
            normalized_fname = fname.replace("\\", "/")
            for cand in candidates:
                if normalized_fname == cand:
                    return cand
        return None

    def find_spec(
        self, fullname: str, _path: Sequence[str] | None, _target: object | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        if not fullname.startswith("__nexy__"):
            return None

        base_path = "/".join(fullname.split("."))
        for suffix, is_package in _CANDIDATES:
            found = self._find_vfs_path(base_path + suffix)
            if found:
                loader = NexyVFSLoader(found)
                return importlib.util.spec_from_loader(
                    fullname, loader, is_package=is_package or None
                )
        return None


def install_vfs_importer() -> None:
    """Installs the Nexy VFS importer into sys.meta_path."""
    if not any(isinstance(finder, NexyVFSFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, NexyVFSFinder())
