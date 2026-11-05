import importlib.abc
import importlib.machinery
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


_PREFIX = "__nexy__/"


def _spellings(path: str) -> list[str]:
    """Other ways the file may be named: lowercase, and `-` for `_` or the reverse.

    Only the part after `__nexy__/` is changed: the folder itself has a fixed name.
    """
    head = _PREFIX if path.startswith(_PREFIX) else ""
    tail = path[len(head) :]
    variants = [tail.lower(), tail.replace("_", "-"), tail.replace("-", "_")]
    return [head + variant for variant in variants if variant != tail]


def _spec(fullname: str, path: str, is_package: bool) -> importlib.machinery.ModuleSpec:
    """The spec of a compiled module, located at *path* in the VFS.

    Built by hand: on Python 3.15 the stubs of `spec_from_loader` still ask for `load_module`,
    which 3.15 removed from `SourceLoader`.
    """
    spec = importlib.machinery.ModuleSpec(fullname, NexyVFSLoader(path), origin=path)
    spec.has_location = True
    if is_package:
        spec.submodule_search_locations = [path.rsplit("/", 1)[0]]
    return spec


class NexyVFSFinder(importlib.abc.MetaPathFinder):
    def __init__(self) -> None:
        self.vfs = VFS()

    def _find_vfs_path(self, base_path: str) -> str | None:
        if self.vfs.exists(base_path):
            return base_path
        return next((path for path in _spellings(base_path) if self.vfs.exists(path)), None)

    def find_spec(
        self, fullname: str, _path: Sequence[str] | None, _target: object | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        if not fullname.startswith("__nexy__"):
            return None

        base_path = "/".join(fullname.split("."))
        for suffix, is_package in _CANDIDATES:
            found = self._find_vfs_path(base_path + suffix)
            if found:
                return _spec(fullname, found, is_package)
        return None


def install_vfs_importer() -> None:
    """Installs the Nexy VFS importer into sys.meta_path."""
    if not any(isinstance(finder, NexyVFSFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, NexyVFSFinder())
