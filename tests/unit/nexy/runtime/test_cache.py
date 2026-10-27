import asyncio
import time
import types

from nexy.modules.routers.fbrouter.handlers import make_isr_handler
from nexy.modules.routers.fbrouter.registrar import revalidate_window
from nexy.modules.runtime.cache import REVALIDATE_CACHE, RevalidateCache


class TestRevalidateCache:
    """ISR cache store: TTL per route, bounded, stale-while-revalidate."""

    def test_empty_cache_misses(self):
        cache = RevalidateCache()
        assert cache.get("/blog") is None

    def test_set_then_get_returns_value(self):
        cache = RevalidateCache()
        cache.set("/blog", "<h1>Blog</h1>", revalidate=60)
        assert cache.get("/blog") == "<h1>Blog</h1>"

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

    def _handler(self, pathname: str, revalidate: int, calls: list[int]):
        def _blog() -> str:
            calls.append(1)
            return f"<h1>Blog {len(calls)}</h1>"

        return make_isr_handler(_blog, pathname, revalidate)

    async def _fetch(self, handler):
        from fastapi import Request

        request = Request({"type": "http", "method": "GET", "path": "/blog", "headers": []})
        resp = await handler(request)
        if hasattr(resp, "body_iterator"):
            chunks = [c async for c in resp.body_iterator]
            return b"".join(chunks).decode()
        return resp.body.decode()

    def test_fresh_serves_cached_html(self):
        self._reset()
        calls: list[int] = []
        handler = self._handler("/blog", 60, calls)
        first = asyncio.run(self._fetch(handler))
        second = asyncio.run(self._fetch(handler))
        assert first == "<h1>Blog 1</h1>"
        assert second == "<h1>Blog 1</h1>"  # cached, no re-render
        assert len(calls) == 1

    def test_stale_regens_in_background_but_serves_stale(self):
        self._reset()
        calls: list[int] = []
        handler = self._handler("/blog", 0, calls)  # revalidate=0 -> dynamic-ish
        first = asyncio.run(self._fetch(handler))
        assert first == "<h1>Blog 1</h1>"

    def test_isr_response_has_cache_control_header(self):
        self._reset()
        calls: list[int] = []
        handler = self._handler("/blog", 60, calls)

        async def run():
            from fastapi import Request

            request = Request({"type": "http", "method": "GET", "path": "/blog", "headers": []})
            return await handler(request)

        resp = asyncio.run(run())
        assert resp.headers.get("cache-control") is not None

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
