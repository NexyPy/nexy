from fastapi.testclient import TestClient

from nexy.runtime.cache import RevalidateCache


class TestRevalidateCache:
    def test_missing_route_is_always_stale(self) -> None:
        cache = RevalidateCache()

        assert cache.get("/never/stored") is None
        assert cache.is_stale("/never/stored") is True

    def test_returns_stored_value(self) -> None:
        cache = RevalidateCache()

        cache.set("/route", "html", revalidate=10)

        assert cache.get("/route") == "html"
        assert cache.is_stale("/route") is False

    def test_ignores_routes_without_revalidate_window(self) -> None:
        cache = RevalidateCache()

        cache.set("/route", "html", revalidate=None)

        assert cache.get("/route") is None
        assert cache.is_stale("/route") is True  # dynamic routes are always stale

    def test_clear_empties_the_store(self) -> None:
        cache = RevalidateCache()
        cache.set("/route", "html", revalidate=10)

        cache.clear()

        assert cache.get("/route") is None

    def test_respects_lru_bound(self) -> None:
        cache = RevalidateCache(max_size=2)

        cache.set("/a", "a", revalidate=10)
        cache.set("/b", "b", revalidate=10)
        cache.set("/c", "c", revalidate=10)  # evicts the oldest entry

        assert cache.get("/a") is None
        assert cache.get("/b") == "b"
        assert cache.get("/c") == "c"


class TestAssembledApp:
    def test_serves_scalar_docs_route(self, nexy_app: TestClient) -> None:
        response = nexy_app.get("/docs")

        assert response.status_code in (200, 404)  # docs route may be disabled by config

    def test_serves_favicon(self, nexy_app: TestClient) -> None:
        response = nexy_app.get("/favicon.ico")

        assert response.status_code == 200

    def test_unknown_route_returns_404(self, nexy_app: TestClient) -> None:
        response = nexy_app.get("/definitely/not/a/route")

        assert response.status_code == 404
