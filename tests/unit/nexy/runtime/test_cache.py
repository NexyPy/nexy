import asyncio
import time
import types
from typing import Any

import pytest

from nexy.modules.routers.fbrouter import handlers
from nexy.modules.routers.fbrouter.handlers import make_isr_handler
from nexy.modules.routers.fbrouter.registrar import revalidate_window
from nexy.modules.runtime.cache import (
    REVALIDATE_CACHE,
    CacheEntry,
    RevalidateCache,
    reset_isr_cache,
)


class UnreadableCache(RevalidateCache):
    def get(self, _path: str) -> CacheEntry | None:
        raise OSError("store down")


class UnwritableCache(RevalidateCache):
    def set(self, _path: str, _value: str, _revalidate: int | None = None) -> None:
        raise OSError("store down")


@pytest.fixture(autouse=True)
def _fresh_isr_store() -> Any:
    reset_isr_cache()
    yield
    reset_isr_cache()


class TestRevalidateCache:
    """ISR cache store: TTL per route, bounded, stale-while-revalidate."""

    def test_empty_cache_misses(self):
        cache = RevalidateCache()
        assert cache.get("/blog") is None

    def test_set_then_get_returns_value(self):
        cache = RevalidateCache()
        cache.set("/blog", "<h1>Blog</h1>", revalidate=60)
        assert cache.get("/blog").value == "<h1>Blog</h1>"

    def test_fresh_route_is_not_stale(self):
        cache = RevalidateCache()
        cache.set("/blog", "<h1>Blog</h1>", revalidate=60)
        assert cache.is_stale("/blog") is False

    def test_expired_route_is_stale(self):
        cache = RevalidateCache()
        cache.set("/blog", "<h1>Blog</h1>", revalidate=0)
        time.sleep(0.01)
        assert cache.is_stale("/blog") is True

    def test_unknown_route_is_stale(self):
        cache = RevalidateCache()
        assert cache.is_stale("/nope") is True

    def test_set_without_revalidate_not_stored(self):
        cache = RevalidateCache()
        cache.set("/blog", "<h1>Blog</h1>", revalidate=None)
        assert cache.get("/blog") is None

    def test_cache_bounded(self):
        cache = RevalidateCache(max_size=2)
        cache.set("/a", "a", revalidate=60)
        cache.set("/b", "b", revalidate=60)
        cache.set("/c", "c", revalidate=60)
        assert len(cache._entries) <= 2


class TestIsrHandler:
    """ISR: fresh serves cache; stale serves cached HTML and regens in background."""

    def _reset(self):
        REVALIDATE_CACHE.clear()

    def _handler(self, revalidate: int, calls: list[int]):
        def _blog() -> str:
            calls.append(1)
            return f"<h1>Blog {len(calls)}</h1>"

        return make_isr_handler(_blog, revalidate)

    async def _response(self, handler):
        from fastapi import Request

        request = Request({"type": "http", "method": "GET", "path": "/blog", "headers": []})
        response = await handler(request)
        await asyncio.sleep(0)
        return response

    async def _fetch(self, handler):
        resp = await self._response(handler)
        if hasattr(resp, "body_iterator"):
            chunks = [c async for c in resp.body_iterator]
            return b"".join(chunks).decode()
        return resp.body.decode()

    def test_fresh_serves_cached_html(self):
        self._reset()
        calls: list[int] = []
        handler = self._handler(60, calls)
        first = asyncio.run(self._fetch(handler))
        second = asyncio.run(self._fetch(handler))
        assert first == "<h1>Blog 1</h1>"
        assert second == "<h1>Blog 1</h1>"  # cached, no re-render
        assert len(calls) == 1

    def test_stale_regens_in_background_but_serves_stale(self):
        self._reset()
        calls: list[int] = []
        handler = self._handler(0, calls)  # revalidate=0 -> dynamic-ish
        first = asyncio.run(self._fetch(handler))
        assert first == "<h1>Blog 1</h1>"

    @pytest.mark.parametrize("window", [1, 60, 300])
    def test_a_fresh_page_carries_its_window_in_the_header(self, window: int):
        self._reset()
        handler = self._handler(window, [])
        response = asyncio.run(self._response(handler))
        assert response.headers["cache-control"] == (
            f"public, s-maxage={window}, stale-while-revalidate={window}"
        )

    def test_a_stale_page_keeps_the_same_header(self):
        self._reset()
        REVALIDATE_CACHE._entries["/blog"] = CacheEntry("old", 0.0, 60)
        response = asyncio.run(self._response(self._handler(60, [])))
        assert response.headers["cache-control"] == (
            "public, s-maxage=60, stale-while-revalidate=60"
        )

    def test_a_failing_store_still_sends_the_header(self, monkeypatch: pytest.MonkeyPatch):
        self._reset()
        monkeypatch.setattr(handlers, "get_isr_cache", UnwritableCache)
        response = asyncio.run(self._response(self._handler(60, [])))
        assert response.headers["cache-control"] == (
            "public, s-maxage=60, stale-while-revalidate=60"
        )

    def test_an_unreadable_store_renders_a_fresh_page(self, monkeypatch: pytest.MonkeyPatch):
        self._reset()
        monkeypatch.setattr(handlers, "get_isr_cache", UnreadableCache)
        assert asyncio.run(self._fetch(self._handler(60, []))) == "<h1>Blog 1</h1>"

    def test_an_unwritable_store_returns_the_rendered_page(self, monkeypatch: pytest.MonkeyPatch):
        self._reset()
        monkeypatch.setattr(handlers, "get_isr_cache", UnwritableCache)
        assert asyncio.run(self._fetch(self._handler(60, []))) == "<h1>Blog 1</h1>"

    def test_scan_reads_revalidate_from_module(self):
        mod = types.ModuleType("routes.blog")
        mod.revalidate = 5

        def _blog() -> str:
            return "<h1>Blog</h1>"

        mod.Blog = _blog
        assert revalidate_window(mod) == 5

    def test_scan_defaults_revalidate_to_none(self):
        mod = types.ModuleType("routes.about")

        def _about() -> str:
            return "<h1>About</h1>"

        mod.About = _about
        assert revalidate_window(mod) is None
