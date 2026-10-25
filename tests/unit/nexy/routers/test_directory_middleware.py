"""`middleware.py` in a routes directory wraps every request under that directory's URL.

Like layouts and `dependencies.py`, the files stack from the routes root down, outermost first.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from nexy.modules.routers.fbrouter.directory_middleware import (
    DirectoryMiddleware,
    MiddlewareFileError,
    discover,
    url_pattern,
)

TAG = """
async def middleware(request, call_next):
    response = await call_next(request)
    response.headers["x-seen"] = response.headers.get("x-seen", "") + "{name},"
    return response
"""


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _client(entries, routes=()) -> TestClient:
    app = FastAPI()

    @app.get("/{full_path:path}")
    async def anything(full_path: str):
        return JSONResponse({"path": full_path})

    app.add_middleware(DirectoryMiddleware, entries=entries, routes=lambda: routes)
    return TestClient(app)


class TestUrlPattern:
    @pytest.mark.parametrize(
        ("parts", "matches", "misses"),
        [
            ((), ["/", "/anything", "/a/b"], []),
            (("admin",), ["/admin", "/admin/", "/admin/users"], ["/administrator", "/other"]),
            (("(shop)", "cart"), ["/cart", "/cart/42"], ["/shop/cart", "/(shop)/cart"]),
            (("users", "[id]"), ["/users/42", "/users/42/edit"], ["/users", "/people/42"]),
            (("docs", "[...path]"), ["/docs/a", "/docs/a/b/c"], ["/docs"]),
        ],
    )
    def test_directory_to_url_prefix(self, parts, matches, misses):
        pattern = url_pattern(parts)
        assert all(pattern.match(path) for path in matches)
        assert not any(pattern.match(path) for path in misses)


class TestDiscover:
    def test_no_middleware_files_means_no_entries(self, tmp_path):
        _write(tmp_path, "index.nexy", "x")
        assert discover(tmp_path) == []

    def test_entries_are_ordered_from_the_root_down(self, tmp_path):
        _write(tmp_path, "admin/users/middleware.py", TAG.format(name="users"))
        _write(tmp_path, "middleware.py", TAG.format(name="root"))
        _write(tmp_path, "admin/middleware.py", TAG.format(name="admin"))
        assert [e.directory for e in discover(tmp_path)] == [
            (),
            ("admin",),
            ("admin", "users"),
        ]

    def test_hidden_directories_are_ignored(self, tmp_path):
        _write(tmp_path, "_drafts/middleware.py", TAG.format(name="draft"))
        _write(tmp_path, ".cache/middleware.py", TAG.format(name="cache"))
        assert discover(tmp_path) == []

    def test_a_file_without_a_middleware_function_is_an_error(self, tmp_path):
        _write(tmp_path, "admin/middleware.py", "x = 1\n")
        with pytest.raises(MiddlewareFileError, match="admin/middleware.py.*middleware"):
            discover(tmp_path)

    def test_a_non_async_function_is_an_error(self, tmp_path):
        _write(tmp_path, "middleware.py", "def middleware(request, call_next):\n    return None\n")
        with pytest.raises(MiddlewareFileError, match="async"):
            discover(tmp_path)

    def test_group_and_dynamic_directories_load(self, tmp_path):
        _write(tmp_path, "(shop)/middleware.py", TAG.format(name="shop"))
        _write(tmp_path, "users/[id]/middleware.py", TAG.format(name="user"))
        assert len(discover(tmp_path)) == 2


class TestRouteOwnership:
    """A middleware applies to the routes whose file is in its directory, groups included."""

    @pytest.fixture
    def entries(self, tmp_path):
        _write(tmp_path, "middleware.py", TAG.format(name="root"))
        _write(tmp_path, "(shop)/middleware.py", TAG.format(name="shop"))
        _write(tmp_path, "users/[id]/middleware.py", TAG.format(name="user"))
        return discover(tmp_path)

    ROUTES = (
        ("/open", ()),
        ("/cart", ("(shop)",)),
        ("/users/{id}/settings", ("users", "[id]")),
    )

    def test_a_group_middleware_only_wraps_its_own_routes(self, entries):
        client = _client(entries, self.ROUTES)
        assert client.get("/cart").headers["x-seen"] == "shop,root,"
        assert client.get("/open").headers["x-seen"] == "root,"

    def test_a_dynamic_directory_wraps_the_routes_below_it(self, entries):
        client = _client(entries, self.ROUTES)
        assert client.get("/users/42/settings").headers["x-seen"] == "user,root,"

    def test_an_unknown_url_only_gets_the_middleware_without_a_group(self, entries):
        client = _client(entries, self.ROUTES)
        assert client.get("/nowhere").headers["x-seen"] == "root,"

    def test_routes_added_later_are_seen(self, entries):
        later: list = []
        client = _client(entries, later)
        assert client.get("/cart").headers["x-seen"] == "root,"
        later.append(("/cart", ("(shop)",)))
        assert client.get("/cart").headers["x-seen"] == "shop,root,"


class TestBehaviour:
    @pytest.fixture
    def entries(self, tmp_path):
        _write(tmp_path, "middleware.py", TAG.format(name="root"))
        _write(tmp_path, "admin/middleware.py", TAG.format(name="admin"))
        _write(tmp_path, "admin/users/middleware.py", TAG.format(name="users"))
        return discover(tmp_path)

    def test_only_the_matching_directories_apply(self, entries):
        client = _client(entries)
        assert client.get("/other").headers["x-seen"] == "root,"
        assert client.get("/admin/settings").headers["x-seen"] == "admin,root,"

    def test_the_innermost_runs_last_on_the_way_in(self, entries):
        # Wrapping: root is outermost, so its after-hook runs last and appends last.
        seen = _client(entries).get("/admin/users/7").headers["x-seen"]
        assert seen == "users,admin,root,"

    def test_a_middleware_can_answer_without_calling_the_route(self, tmp_path):
        _write(
            tmp_path,
            "admin/middleware.py",
            "from fastapi.responses import PlainTextResponse\n"
            "async def middleware(request, call_next):\n"
            "    return PlainTextResponse('blocked', status_code=401)\n",
        )
        client = _client(discover(tmp_path))
        assert client.get("/admin/x").status_code == 401
        assert client.get("/admin/x").text == "blocked"
        assert client.get("/open").status_code == 200

    def test_an_outer_middleware_runs_before_an_inner_one(self, tmp_path):
        order = tmp_path / "order.txt"
        for rel, name in (("middleware.py", "root"), ("admin/middleware.py", "admin")):
            _write(
                tmp_path,
                rel,
                f"async def middleware(request, call_next):\n"
                f"    open({str(order)!r}, 'a').write('{name}\\n')\n"
                f"    return await call_next(request)\n",
            )
        _client(discover(tmp_path)).get("/admin/x")
        assert order.read_text().split() == ["root", "admin"]

    def test_the_request_is_untouched_when_nothing_matches(self, tmp_path):
        _write(tmp_path, "admin/middleware.py", TAG.format(name="admin"))
        response = _client(discover(tmp_path)).get("/public-page")
        assert "x-seen" not in response.headers
        assert response.json() == {"path": "public-page"}

    def test_internal_paths_are_never_wrapped(self, tmp_path):
        _write(
            tmp_path,
            "middleware.py",
            "from fastapi.responses import PlainTextResponse\n"
            "async def middleware(request, call_next):\n"
            "    return PlainTextResponse('blocked', status_code=401)\n",
        )
        client = _client(discover(tmp_path))
        for path in ("/__nexy__/main.ts", "/_nexy/hmr", "/public/logo.svg", "/@vite/client"):
            assert client.get(path).status_code == 200, path

    def test_websocket_and_lifespan_scopes_pass_through(self):
        # A non-http scope must reach the app untouched, not be treated as a request.
        reached = []

        async def app(scope, _receive, _send):
            reached.append(scope["type"])

        wrapped = DirectoryMiddleware(app, entries=[])

        import asyncio

        asyncio.run(wrapped({"type": "websocket", "path": "/ws"}, None, None))
        assert reached == ["websocket"]


class TestRoutesThatLookInternal:
    """A page whose URL starts like an asset URL is still a page, and its guard must run."""

    BLOCK = (
        "from fastapi.responses import PlainTextResponse\n"
        "async def middleware(request, call_next):\n"
        "    return PlainTextResponse('blocked', status_code=401)\n"
    )

    @pytest.fixture
    def guarded(self, tmp_path):
        _write(tmp_path, "middleware.py", self.BLOCK)
        return discover(tmp_path)

    @pytest.mark.parametrize("path", ["/assets", "/public/docs", "/@alice"])
    def test_a_real_route_with_an_asset_like_url_is_guarded(self, guarded, path):
        routes = (("/assets", ()), ("/public/docs", ()), ("/@{handle}", ()))
        assert _client(guarded, routes).get(path).status_code == 401

    def test_assets_stay_open_when_only_a_catch_all_route_matches(self, guarded):
        client = _client(guarded, (("/{rest:path}", ()),))
        assert client.get("/assets/app.js").status_code == 200

    @pytest.mark.parametrize("path", ["/__nexy__/main.ts", "/_nexy/hmr", "/node_modules/x.js"])
    def test_framework_urls_are_never_guarded_even_with_a_catch_all(self, guarded, path):
        client = _client(guarded, (("/{rest:path}", ()),))
        assert client.get(path).status_code == 200
