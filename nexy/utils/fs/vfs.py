from pathlib import Path


class VFS:
    """
    Virtual File System with persistent storage.
    Singleton class to store compiled files during runtime.
    Files are stored in memory and persisted to __nexy__ directory on disk.
    """

    _instance = None
    _files: dict[str, str] = {}
    _disk_files: set[str] = set()
    _dev_mode: bool = False
    _disk_prefix: str = "__nexy__"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_from_disk()
        return cls._instance

    def _load_from_disk(self) -> None:
        """Loads all files from __nexy__ directory into memory on initialization and caches disk files."""
        disk_path = Path(self._disk_prefix)
        if not disk_path.exists():
            return
        self._disk_files.clear()
        for file_path in disk_path.rglob("*"):
            if file_path.is_file():
                vfs_path = str(file_path).replace("\\", "/")
                self._disk_files.add(vfs_path)
                try:
                    self._files[vfs_path] = file_path.read_text(encoding="utf-8")
                except Exception:
                    pass

    def write(self, path: str, content: str) -> None:
        """Writes content to a virtual file path and persists to disk (unless in dev mode)."""
        path = path.replace("\\", "/")
        self._files[path] = content
        self._disk_files.add(path)

        # Persist to disk only if not in dev mode
        if not self._dev_mode and path.startswith(self._disk_prefix):
            disk_path = Path(path)
            disk_path.parent.mkdir(parents=True, exist_ok=True)
            disk_path.write_text(content, encoding="utf-8")

    def read(self, path: str) -> str:
        """Reads content from a virtual file path (checks memory first, then disk)."""
        path = path.replace("\\", "/")
        if path in self._files:
            return self._files[path]

        # Check disk if not in memory
        if path.startswith(self._disk_prefix):
            disk_path = Path(path)
            if disk_path.exists():
                content = disk_path.read_text(encoding="utf-8")
                self._files[path] = content
                self._disk_files.add(path)
                return content

        raise FileNotFoundError(f"Virtual file not found: {path}")

    def exists(self, path: str) -> bool:
        """Checks if a virtual file exists (checks memory first, then disk)."""
        path = path.replace("\\", "/")
        if path in self._files:
            return True

        # Check cached disk files first
        if path in self._disk_files:
            return True

        # Check disk if not in cache
        if path.startswith(self._disk_prefix):
            disk_path = Path(path)
            if disk_path.exists():
                self._disk_files.add(path)
                return True

        return False

    def list_files(self) -> list[str]:
        """Returns a list of all files in the VFS (memory + cached disk files)."""
        files = set(self._files.keys())
        files.update(self._disk_files)
        return list(files)

    @classmethod
    def set_dev_mode(cls, dev: bool = True) -> None:
        cls._dev_mode = dev

    def clear(self, clear_disk: bool = False) -> None:
        """Clears all files from the VFS. If clear_disk is True, also deletes from disk."""
        self._files.clear()
        self._disk_files.clear()

        if clear_disk:
            disk_path = Path(self._disk_prefix)
            if disk_path.exists():
                import shutil
                shutil.rmtree(disk_path)

    def delete(self, path: str) -> None:
        """Deletes a file from the VFS (memory and disk)."""
        path = path.replace("\\", "/")
        if path in self._files:
            del self._files[path]
        self._disk_files.discard(path)

        # Delete from disk
        if path.startswith(self._disk_prefix):
            disk_path = Path(path)
            if disk_path.exists():
                disk_path.unlink(missing_ok=True)

    def flush_to_disk(self, prefix: str = "__nexy__") -> None:
        """Flushes all in-memory files to disk (already done automatically in write)."""
        if self._dev_mode:
            return
        for path, content in self._files.items():
            if not path.startswith(prefix):
                continue
            disk_path = Path(path)
            disk_path.parent.mkdir(parents=True, exist_ok=True)
            disk_path.write_text(content, encoding="utf-8")
