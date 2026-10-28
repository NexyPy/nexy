"""The request hooks: read the current request from a page, a handler or a controller."""

from __future__ import annotations

import pytest
from starlette.datastructures import URL
from starlette.requests import Request

import nexy
from nexy.hooks import useHeaders, useIsActive, useParams, useQuery, useRequest, useUrl
from nexy.modules.routers.context import current_request


@pytest.fixture
def in_request():
    """Run the test inside a request, like the router does."""
    tokens = []

    def start(path="/blog/post", query=b"", headers=None, params=None) -> Request:
        scope = {
            "type": "http",
            "method": "GET",
            "scheme": "https",
            "server": ("example.com", 443),
            "path": path,
            "query_string": query,
            "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
            "path_params": params or {},
        }
        request = Request(scope)
        tokens.append(current_request.set(request))
        return request

    yield start
    for token in tokens:
        current_request.reset(token)


class TestParams:
    def test_it_returns_the_dynamic_segments(self, in_request):
        in_request(params={"slug": "hello"})
        assert useParams() == {"slug": "hello"}

    def test_use_query_is_the_same_thing_under_its_old_name(self, in_request):
        in_request(params={"slug": "hello"})
        assert useQuery() == useParams()


class TestRequest:
    def test_it_returns_the_current_request(self, in_request):
        request = in_request()
        assert useRequest() is request

    def test_headers_are_a_plain_dict_with_lowercase_names(self, in_request):
        in_request(headers={"Accept-Language": "fr", "X-Thing": "1"})
        assert useHeaders() == {"accept-language": "fr", "x-thing": "1"}

    def test_the_url_names_its_parts(self, in_request):
        in_request(path="/blog", query=b"page=2")
        url = useUrl()
        assert (isinstance(url, URL), url.hostname, url.path, url.query) == (
            True,
            "example.com",
            "/blog",
            "page=2",
        )


class TestIsActive:
    @pytest.mark.parametrize(
        ("current", "href", "exact", "expected"),
        [
            ("/blog/post", "/blog/post", False, True),
            ("/blog/post", "/blog", False, True),
            ("/blog/post", "/blog", True, False),
            ("/blogger", "/blog", False, False),
            ("/anything", "/", False, False),
            ("/", "/", False, True),
            ("/blog/post/", "/blog/post", True, True),
            ("/blog/post", "/blog/post/?page=2#top", True, True),
        ],
    )
    def test_it_follows_the_rule_of_the_client(self, in_request, current, href, exact, expected):
        in_request(path=current)
        assert useIsActive(href, exact=exact) is expected


class TestOutsideARequest:
    @pytest.mark.parametrize("hook", [useParams, useRequest, useHeaders, useUrl])
    def test_a_hook_refuses_to_run(self, hook):
        with pytest.raises(RuntimeError, match="request"):
            hook()

    def test_the_active_check_refuses_too(self):
        with pytest.raises(RuntimeError, match="request"):
            useIsActive("/")


class TestExports:
    @pytest.mark.parametrize(
        "name", ["useParams", "useRequest", "useHeaders", "useUrl", "useIsActive"]
    )
    def test_nexy_exports_it(self, name):
        assert callable(getattr(nexy, name))
