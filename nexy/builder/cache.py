import hashlib
import json
import time
from pathlib import Path


class BuildCache:
    _instance = None
    _cache: dict[str, dict] = {}
    _dirty: bool = False
    CACHE_FILE = ".nexy-cache.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_loaded"):
            self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        path = Path(self.CACHE_FILE)
        if path.exists():
            try:
                raw = path.read_text(encoding="utf-8")
                self._cache = json.loads(raw)
            except (json.JSONDecodeError, OSError):
                self._cache = {}

    def _save(self) -> None:
        if not self._dirty:
            return
        try:
            Path(self.CACHE_FILE).write_text(
                json.dumps(self._cache, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            self._dirty = False
        except OSError:
            pass

    @staticmethod
    def _file_hash(path: Path) -> str:
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()

    def is_cached(self, file_path: Path) -> bool:
        self._load()
        key = file_path.as_posix()
        entry = self._cache.get(key)
        if entry is None:
            return False
        try:
            return entry["hash"] == self._file_hash(file_path)
        except OSError:
            return False

    def mark_cached(self, file_path: Path) -> None:
        self._load()
        key = file_path.as_posix()
        try:
            self._cache[key] = {
                "hash": self._file_hash(file_path),
                "mtime": time.time(),
            }
            self._dirty = True
        except OSError:
            pass

    def flush(self) -> None:
        self._save()

    def clear(self) -> None:
        self._load()
        self._cache.clear()
        self._dirty = True
