import threading
import time
from dataclasses import dataclass


@dataclass
class _Entry:
    value: str
    expires_at: float
    revalidate: int


class RevalidateCache:
    """Bounded per-route runtime cache with TTL (ISR stale-while-revalidate).

    Routes without a revalidate window are never stored (dynamic). The store
    is thread-safe; the LRU bound keeps memory flat under traffic.
    """

    def __init__(self, max_size: int = 256) -> None:
        self._max_size = max_size
        self._entries: dict[str, _Entry] = {}
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
        if revalidate is None or revalidate <= 0:
            return
        with self._lock:
            self._entries[path] = _Entry(value, time.monotonic() + revalidate, revalidate)
            self._touch(path)

    def get(self, path: str) -> str | None:
        with self._lock:
            entry = self._entries.get(path)
            if entry is None:
                return None
            return entry.value

    def is_stale(self, path: str) -> bool:
        with self._lock:
            entry = self._entries.get(path)
            if entry is None:
                return True
            return time.monotonic() > entry.expires_at

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._order.clear()


REVALIDATE_CACHE = RevalidateCache()

__all__ = ["RevalidateCache", "REVALIDATE_CACHE"]
