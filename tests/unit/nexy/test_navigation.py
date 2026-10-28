"""`redirect`, `notFound` and friends: leave a page or answer 404/401/403 from anywhere.

They raise an HTTP exception, so the same call works in a page, an API handler, a modular
controller, an action and a dependency, and the router turns it into the right answer.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import nexy
from nexy import http
from nexy.modules.routers.error_handlers import handle_http_exception
from nexy.navigation import (
    forbidden,
    notFound,
    permanentRedirect,
    redirect,
    unauthorized,
)


def _raised(call, *args, **kwargs) -> HTTPException:
    with pytest.raises(HTTPException) as caught:
        call(*args, **kwargs)
    return caught.value


class TestRedirect:
    def test_it_is_a_temporary_redirect_by_default(self):
        assert _raised(redirect, "/login").status_code == 307

    def test_it_names_the_destination(self):
        assert _raised(redirect, "/login").headers == {"Location": "/login"}

    def test_a_permanent_redirect_is_a_308(self):
        assert _raised(permanentRedirect, "/new").status_code == 308

    def test_the_status_can_be_chosen(self):
        assert _raised(redirect, "/done", status=303).status_code == 303

    @pytest.mark.parametrize("status", [200, 404, 306, 500])
    def test_a_status_that_is_not_a_redirect_is_refused(self, status):
        with pytest.raises(ValueError, match="redirect"):
            redirect("/x", status=status)

    @pytest.mark.parametrize("url", ["/a\r\nSet-Cookie: x=1", "/a\nb", "/a\rb"])
    def test_a_line_break_in_the_destination_is_refused(self, url):
        with pytest.raises(ValueError, match="line break"):
            redirect(url)


class TestAnswers:
    def test_not_found_is_a_404(self):
        assert _raised(notFound).status_code == 404

    def test_not_found_can_say_what_is_missing(self):
        assert _raised(notFound, "No such post").detail == "No such post"

    def test_forbidden_is_a_403(self):
        assert _raised(forbidden).status_code == 403

    def test_unauthorized_is_a_401(self):
        assert _raised(unauthorized).status_code == 401

    def test_unauthorized_can_name_the_scheme(self):
        error = _raised(unauthorized, scheme="Bearer")
        assert error.headers == {"WWW-Authenticate": "Bearer"}


class TestTheRouterAnswers:
    @staticmethod
    def _client(raiser) -> TestClient:
        app = FastAPI()
        app.add_exception_handler(HTTPException, handle_http_exception)
        app.get("/go")(raiser)
        return TestClient(app, follow_redirects=False)

    def test_a_redirect_is_a_real_redirect_with_no_error_page(self):
        answer = self._client(lambda: redirect("/login")).get("/go")
        assert (answer.status_code, answer.headers["location"], answer.text) == (307, "/login", "")

    def test_an_api_client_is_redirected_too(self):
        answer = self._client(lambda: permanentRedirect("/v2")).get(
            "/go", headers={"accept": "application/json"}
        )
        assert (answer.status_code, answer.headers["location"]) == (308, "/v2")

    def test_a_plain_http_exception_with_a_location_is_a_redirect_as_well(self):
        def old() -> None:
            raise HTTPException(status_code=307, headers={"Location": "/about"})

        answer = self._client(old).get("/go")
        assert (answer.status_code, answer.text) == (307, "")

    def test_a_browser_gets_the_page_for_a_403(self):
        answer = self._client(lambda: forbidden()).get("/go", headers={"accept": "text/html"})
        assert answer.status_code == 403 and "<html" in answer.text.lower()

    def test_an_api_client_gets_json_for_a_401(self):
        answer = self._client(lambda: unauthorized()).get(
            "/go", headers={"accept": "application/json"}
        )
        assert answer.status_code == 401 and answer.json()["detail"]


class TestExports:
    @pytest.mark.parametrize(
        "name", ["redirect", "permanentRedirect", "notFound", "forbidden", "unauthorized"]
    )
    def test_nexy_and_nexy_http_both_export_it(self, name):
        assert getattr(nexy, name) is getattr(http, name)
