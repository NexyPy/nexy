import importlib.abc
import importlib.machinery
import importlib.util
import sys

from nexy.utils.fs.vfs import VFS


class NexyVFSLoader(importlib.abc.SourceLoader):
    def __init__(self, path: str) -> None:
        self.path = path
        self.vfs = VFS()

    def get_filename(self, fullname: str) -> str:
        return self.path

    def get_data(self, path: str) -> bytes:
        return self.vfs.read(path).encode("utf-8")


class NexyVFSFinder(importlib.abc.MetaPathFinder):
    def __init__(self) -> None:
        self.vfs = VFS()

    def find_spec(
        self, fullname: str, path: list[str] | None, target: object | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        if not fullname.startswith("__nexy__"):
            return None

        parts = fullname.split(".")

        py_path = "/".join(parts) + ".py"
        if self.vfs.exists(py_path):
            return importlib.util.spec_from_loader(fullname, NexyVFSLoader(py_path))

        init_path = "/".join(parts) + "/__init__.py"
        if self.vfs.exists(init_path):
            return importlib.util.spec_from_loader(
                fullname, NexyVFSLoader(init_path), is_package=True
            )

        return None


def install_vfs_importer() -> None:
    if not any(isinstance(finder, NexyVFSFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, NexyVFSFinder())
