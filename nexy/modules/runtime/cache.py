"""ISR stores share one rendered page per URL in memory, on disk or in Redis."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from nexy.core.config import Config


@dataclass(frozen=True)
class CacheEntry:
    """One stored page and the wall clock time at which it becomes stale."""

    value: str
    expires_at: float
    revalidate: int


@runtime_checkable
class ISRCache(Protocol):
    """The three operations an ISR store must provide."""

    def get(self, path: str) -> CacheEntry | None: ...

    def set(self, path: str, value: str, revalidate: int | None = None) -> None: ...

    def invalidate(self, path: str) -> None: ...


def _path_key(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8")).hexdigest()


_REDIS_PREFIX = "nexy:isr:"


def _redis_key(path: str) -> str:
    return f"{_REDIS_PREFIX}{_path_key(path)}"


def _window(revalidate: int | None) -> int | None:
    return revalidate if revalidate is not None and revalidate > 0 else None


def _payload(value: str, revalidate: int) -> str:
    return json.dumps(
        {"value": value, "expires_at": time.time() + revalidate, "revalidate": revalidate}
    )


def _entry(payload: Any) -> CacheEntry | None:
    try:
        return CacheEntry(
            str(payload["value"]),
            float(payload["expires_at"]),
            int(payload["revalidate"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _decode(raw: Any) -> str | None:
    try:
        return raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
    except (AttributeError, ValueError):
        return None


class RevalidateCache:
    """Bounded per-route runtime cache with TTL (ISR stale-while-revalidate).

    Routes without a revalidate window are never stored (dynamic). The store
    is thread-safe; the LRU bound keeps memory flat under traffic.
    """

    def __init__(self, max_size: int = 256) -> None:
        self._max_size = max_size
        self._entries: dict[str, CacheEntry] = {}
        self._order: list[str] = []
        self._lock = threading.Lock()

    def _touch(self, path: str) -> None:
        if path in self._order:
            self._order.remove(path)
        self._order.append(path)
        while len(self._order) > self._max_size:
            evict = self._order.pop(0)
            self._entries.pop(evict, None)

    def set(self, path: str, value: str, revalidate: int | None = None) -> None:
        window = _window(revalidate)
        if window is None:
            return
        with self._lock:
            self._entries[path] = CacheEntry(value, time.time() + window, window)
            self._touch(path)

    def get(self, path: str) -> CacheEntry | None:
        with self._lock:
            return self._entries.get(path)

    def is_stale(self, path: str) -> bool:
        entry = self.get(path)
        return entry is None or time.time() > entry.expires_at

    def invalidate(self, path: str) -> None:
        """Drop one path, or every path when called with `*`."""
        if path == "*":
            self.clear()
            return
        with self._lock:
            self._entries.pop(path, None)
            if path in self._order:
                self._order.remove(path)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._order.clear()


class FileISRCache:
    """A shared on-disk cache for one host, written atomically per URL."""

    def __init__(self, directory: str | Path = ".nexy/isr") -> None:
        self.directory = Path(directory)

    def _file(self, path: str) -> Path:
        return self.directory / f"{_path_key(path)}.json"

    def _read(self, path: str) -> CacheEntry | None:
        try:
            payload = json.loads(self._file(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return _entry(payload)

    def get(self, path: str) -> CacheEntry | None:
        return self._read(path)

    def set(self, path: str, value: str, revalidate: int | None = None) -> None:
        window = _window(revalidate)
        if window is None:
            self.invalidate(path)
            return
        self.directory.mkdir(parents=True, exist_ok=True)
        self._write(self._file(path), _payload(value, window))

    def _write(self, target: Path, payload: str) -> None:
        handle, name = tempfile.mkstemp(dir=target.parent, prefix=".tmp-")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                stream.write(payload)
            os.replace(name, target)
        except Exception:
            Path(name).unlink(missing_ok=True)
            raise

    def invalidate(self, path: str) -> None:
        if path == "*":
            for entry in self.directory.glob("*.json"):
                entry.unlink()
            return
        self._file(path).unlink(missing_ok=True)


class RedisISRCache:
    """A cache for several workers, built on any Redis client with get/set/delete."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def get(self, path: str) -> CacheEntry | None:
        return self._read(path)

    def _read(self, path: str) -> CacheEntry | None:
        raw = self.client.get(_redis_key(path))
        text = _decode(raw) if raw is not None else None
        if text is None:
            return None
        try:
            payload = json.loads(text)
        except ValueError:
            return None
        return _entry(payload)

    def set(self, path: str, value: str, revalidate: int | None = None) -> None:
        window = _window(revalidate)
        if window is None:
            self.invalidate(path)
            return
        self.client.set(_redis_key(path), _payload(value, window))

    def invalidate(self, path: str) -> None:
        if path == "*":
            for key in list(self.client.scan_iter(f"{_REDIS_PREFIX}*")):
                self.client.delete(key)
            return
        self.client.delete(_redis_key(path))


REVALIDATE_CACHE = RevalidateCache()

_DEFAULT_REDIS_URL = "redis://localhost:6379/0"
_SENTINEL = object()
_selected: Any = _SENTINEL
_cache: ISRCache | None = None


def reset_isr_cache() -> None:
    """Forget the resolved store so a new `nexyconfig.py` can choose another one."""
    global _selected, _cache
    _selected = _SENTINEL
    _cache = None


def get_isr_cache() -> ISRCache:
    """The store this process selected in `nexyconfig.py`, resolved once."""
    global _selected, _cache
    selected = Config().useISRCache
    if selected is not _selected or _cache is None:
        _cache = _create_isr_cache(selected)
        _selected = selected
    return _cache


def _create_isr_cache(spec: Any) -> ISRCache:
    if spec is None:
        return REVALIDATE_CACHE
    if isinstance(spec, ISRCache):
        return spec
    if isinstance(spec, str):
        return _named_cache(spec.lower(), {})
    if isinstance(spec, dict):
        if "type" not in spec:
            raise ValueError(f"Unknown ISR cache: {spec!r}")
        return _named_cache(str(spec["type"]).lower(), spec)
    raise ValueError(f"Unknown ISR cache: {spec!r}")


def _named_cache(kind: str, options: dict[str, Any]) -> ISRCache:
    if kind == "memory":
        return RevalidateCache()
    if kind == "file":
        return FileISRCache(options.get("directory", ".nexy/isr"))
    if kind == "redis":
        return _redis_cache(options)
    raise ValueError(f"Unknown ISR cache: {kind!r}")


def _redis_cache(options: dict[str, Any]) -> RedisISRCache:
    client = options.get("client")
    if client is None:
        url = str(options.get("url", _DEFAULT_REDIS_URL))
        try:
            module = importlib.import_module("redis")
        except ModuleNotFoundError as error:
            raise RuntimeError("The Redis ISR cache needs redis: uv add redis") from error
        client = module.Redis.from_url(url)
    return RedisISRCache(client)


__all__ = [
    "CacheEntry",
    "FileISRCache",
    "ISRCache",
    "RedisISRCache",
    "RevalidateCache",
    "REVALIDATE_CACHE",
    "get_isr_cache",
    "reset_isr_cache",
]
