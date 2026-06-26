import importlib.abc
import importlib.machinery
import importlib.util
import sys

from nexy.utils.fs.vfs import VFS


class NexyVFSLoader(importlib.abc.SourceLoader):
    def __init__(self, path: str) -> None:
        self.path = path
        self.vfs = VFS()

    def get_filename(self, _fullname: str) -> str:
        return self.path

    def get_data(self, path: str) -> bytes:
        return self.vfs.read(path).encode("utf-8")


class NexyVFSFinder(importlib.abc.MetaPathFinder):
    def __init__(self) -> None:
        self.vfs = VFS()

    def _find_vfs_path(self, base_path: str) -> str | None:
        if self.vfs.exists(base_path):
            return base_path
        candidates = {
            base_path,
            base_path.lower(),
            base_path.upper(),
            base_path.replace("_", "-"),
            base_path.replace("-", "_"),
        }
        for fname in self.vfs.list_files():
            for cand in candidates:
                if fname.replace("\\", "/") == cand:
                    return fname
        return None

    def find_spec(
        self, fullname: str, _path: list[str] | None, _target: object | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        # We only intercept imports starting with __nexy__
        if not fullname.startswith("__nexy__"):
            return None

        # Convert module name to virtual path
        # __nexy__.src.routes.index -> __nexy__/src/routes/index.py
        parts = fullname.split(".")
        base_path = "/".join(parts)

        # Check if it's a package or a module
        # Try as a module first (.py)
        py_path = base_path + ".py"
        found = self._find_vfs_path(py_path)
        if found:
            return importlib.util.spec_from_loader(fullname, NexyVFSLoader(found))

        # Try .nexy fallback
        nexy_path = base_path + ".nexy"
        found = self._find_vfs_path(nexy_path)
        if found:
            return importlib.util.spec_from_loader(fullname, NexyVFSLoader(found))

        # Try as a package (__init__.py)
        init_path = base_path + "/__init__.py"
        found = self._find_vfs_path(init_path)
        if found:
            return importlib.util.spec_from_loader(fullname, NexyVFSLoader(found), is_package=True)

        return None


def install_vfs_importer() -> None:
    """Installs the Nexy VFS importer into sys.meta_path."""
    if not any(isinstance(finder, NexyVFSFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, NexyVFSFinder())
