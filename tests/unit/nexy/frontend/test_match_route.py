"""Unit tests for the pure client-router mirror (no browser required)."""

from typing import Any

from nexy.modules.frontend.client_router import match_route

Routes = list[dict[str, Any]]


def _match(routes: Routes, pathname: str) -> tuple[dict[str, Any] | None, dict[str, str]]:
    return match_route(routes, pathname)


def test_match_index_route():
    routes: Routes = [{"path": "/", "file": "/src/routes/index.tsx"}]
    route, params = _match(routes, "/")
    assert route is not None


def test_match_index_route_params_empty():
    routes: Routes = [{"path": "/", "file": "/src/routes/index.tsx"}]
    _, params = _match(routes, "/")
    assert params == {}


def test_match_dynamic_slug():
    routes: Routes = [{"path": "/blog/{slug}", "file": "/src/routes/blog/[slug].tsx"}]
    route, _ = _match(routes, "/blog/hello")
    assert route is not None


def test_match_dynamic_slug_param():
    routes: Routes = [{"path": "/blog/{slug}", "file": "/src/routes/blog/[slug].tsx"}]
    _, params = _match(routes, "/blog/hello")
    assert params == {"slug": "hello"}


def test_match_catch_all_multi_segment():
    routes: Routes = [{"path": "/docs/{...path}", "file": "/src/routes/docs/[...path].tsx"}]
    route, _ = _match(routes, "/docs/a/b/c")
    assert route is not None


def test_match_catch_all_joined_param():
    routes: Routes = [{"path": "/docs/{...path}", "file": "/src/routes/docs/[...path].tsx"}]
    _, params = _match(routes, "/docs/a/b/c")
    assert params == {"path": "a/b/c"}


def test_catch_all_wildcard_requires_prefix():
    routes: Routes = [{"path": "/docs/{...path}", "file": "/src/routes/docs/[...path].tsx"}]
    route, _ = _match(routes, "/a/b")
    assert route is None


def test_no_match_unknown_route():
    routes: Routes = [{"path": "/", "file": "/src/routes/index.tsx"}]
    route, _ = _match(routes, "/inconnu")
    assert route is None


def test_no_match_unknown_route_empty_params():
    routes: Routes = [{"path": "/", "file": "/src/routes/index.tsx"}]
    _, params = _match(routes, "/inconnu")
    assert params == {}


def test_non_navigable_excluded():
    routes: Routes = [{"path": "/about", "file": "/src/routes/about.nexy"}]
    route, _ = _match(routes, "/about")
    assert route is None


def test_trailing_slash_matches_same_route():
    routes: Routes = [{"path": "/about", "file": "/src/routes/about.tsx"}]
    route, _ = _match(routes, "/about/")
    assert route is not None
