import shutil
from pathlib import Path

_DISK_PREFIX = "__nexy__"


def _key(path: str) -> str:
    """The form a path has in the VFS: forward slashes."""
    return path.replace("\\", "/")


def _scan_disk(prefix: str) -> set[str]:
    """The paths of the files under *prefix* on disk; their contents are not read."""
    root = Path(prefix)
    if not root.exists():
        return set()
    return {_key(str(file)) for file in root.rglob("*") if file.is_file()}


def _save(path: str, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


class VFS:
    """
    Virtual File System with persistent storage.
    Singleton class to store compiled files during runtime.
    Files are stored in memory and persisted to __nexy__ directory on disk.
    Uses lazy loading: only file paths are indexed at startup, content is read on demand.
    """

    _instance: "VFS | None" = None
    _files: dict[str, str] = {}
    _disk_files: set[str] = set()
    _dev_mode: bool = False
    _disk_prefix: str = _DISK_PREFIX

    def __new__(cls) -> "VFS":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._disk_files.clear()
            cls._disk_files.update(_scan_disk(cls._disk_prefix))
        return cls._instance

    def _on_disk(self, path: str) -> bool:
        """True for a path under the persisted prefix whose file exists on disk."""
        return path.startswith(self._disk_prefix) and Path(path).exists()

    def write(self, path: str, content: str) -> None:
        """Writes content to a virtual file path and persists to disk (unless in dev mode)."""
        path = _key(path)
        self._files[path] = content
        self._disk_files.add(path)
        if not self._dev_mode and path.startswith(self._disk_prefix):
            _save(path, content)

    def read(self, path: str) -> str:
        """Reads content from a virtual file path (checks memory first, then disk)."""
        path = _key(path)
        if path not in self._files and self._on_disk(path):
            self._files[path] = Path(path).read_text(encoding="utf-8")
            self._disk_files.add(path)
        if path not in self._files:
            raise FileNotFoundError(f"Virtual file not found: {path}")
        return self._files[path]

    def exists(self, path: str) -> bool:
        """Checks if a virtual file exists (checks memory first, then indexed disk paths)."""
        path = _key(path)
        if path in self._files or path in self._disk_files:
            return True
        if self._on_disk(path):
            self._disk_files.add(path)
            return True
        return False

    def list_files(self) -> list[str]:
        """Returns a list of all files in the VFS (memory + indexed disk paths)."""
        return list(set(self._files) | self._disk_files)

    @classmethod
    def set_dev_mode(cls, dev: bool = True) -> None:
        cls._dev_mode = dev

    @classmethod
    def is_dev_mode(cls) -> bool:
        return cls._dev_mode

    def clear(self, clear_disk: bool = False) -> None:
        """Clears all files from the VFS. If clear_disk is True, also deletes from disk."""
        self._files.clear()
        self._disk_files.clear()
        if clear_disk and Path(self._disk_prefix).exists():
            shutil.rmtree(self._disk_prefix)

    def delete(self, path: str) -> None:
        """Deletes a file from the VFS (memory and disk)."""
        path = _key(path)
        self._files.pop(path, None)
        self._disk_files.discard(path)
        if self._on_disk(path):
            Path(path).unlink(missing_ok=True)

    def flush_to_disk(self, prefix: str = _DISK_PREFIX) -> None:
        """Flushes all in-memory files to disk (already done automatically in write)."""
        if self._dev_mode:
            return
        for path, content in self._files.items():
            if path.startswith(prefix):
                _save(path, content)
