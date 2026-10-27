"""An `@Action` is a POST endpoint that takes JSON from scripts and forms from plain HTML."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

from nexy.modules.routers.actions.engine import ActionEngine
from nexy.modules.routers.actions.revalidate import revalidate
from nexy.modules.routers.actions.secret import forget_secret
from nexy.modules.routers.actions.store import ACTIONS_STORE


class Profile(BaseModel):
    name: str
    age: int = 0


@pytest.fixture(autouse=True)
def _store(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> Iterator[None]:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_ACTION_SECRET", "test-secret")
    monkeypatch.delenv("NEXY_ALLOWED_ORIGINS", raising=False)
    forget_secret()
    saved = dict(ACTIONS_STORE.registry), dict(ACTIONS_STORE.path_map)
    ACTIONS_STORE.registry.clear()
    ACTIONS_STORE.path_map.clear()
    yield
    ACTIONS_STORE.registry.clear()
    ACTIONS_STORE.registry.update(saved[0])
    ACTIONS_STORE.path_map.clear()
    ACTIONS_STORE.path_map.update(saved[1])
    forget_secret()


def _client(*handlers: Any) -> TestClient:
    for handler in handlers:
        handler.__module__ = "src.actions"
        ACTIONS_STORE.register(handler)
    app = FastAPI()
    ActionEngine().include_router(app)
    return TestClient(app, base_url="http://testserver")


def _url(handler: Any) -> str:
    return ACTIONS_STORE.path_map[f"src.actions.{handler.__name__}"]


async def create_user(name: str, age: int = 0) -> dict[str, Any]:
    return {"name": name, "age": age}


def double(value: int) -> int:
    return value * 2


async def save_profile(profile: Profile) -> Profile:
    return profile


async def fail() -> None:
    raise HTTPException(status_code=403, detail="no")


async def touch(request: Request, response: Response) -> str:
    response.set_cookie("seen", "1")
    return request.method


async def custom_answer() -> Response:
    return PlainTextResponse("custom", status_code=201)


async def refresh_users() -> str:
    revalidate("/users")
    return "ok"


async def refresh_current() -> str:
    revalidate()
    return "ok"


def test_a_json_call_runs_the_function():
    client = _client(create_user)
    response = client.post(_url(create_user), json={"name": "Ada", "age": 36})
    assert response.json() == {"name": "Ada", "age": 36}


def test_a_json_call_uses_the_defaults_of_the_function():
    client = _client(create_user)
    assert client.post(_url(create_user), json={"name": "Ada"}).json()["age"] == 0


def test_a_sync_function_runs_too():
    client = _client(double)
    assert client.post(_url(double), json={"value": 4}).json() == 8


def test_a_model_parameter_is_read_from_its_json_object():
    client = _client(save_profile)
    response = client.post(_url(save_profile), json={"profile": {"name": "Ada"}})
    assert response.json() == {"name": "Ada", "age": 0}


def test_an_invalid_input_is_a_422_with_the_field():
    client = _client(create_user)
    response = client.post(_url(create_user), json={"age": "x"})
    assert response.status_code == 422
    assert {item["loc"][-1] for item in response.json()["detail"]} == {"name", "age"}


def test_a_body_that_is_not_an_object_is_a_400():
    client = _client(create_user)
    assert client.post(_url(create_user), json=[1]).status_code == 400


def test_an_http_exception_keeps_its_status():
    client = _client(fail)
    assert client.post(_url(fail), json={}).status_code == 403


def test_the_request_and_response_are_injected_and_cookies_are_kept():
    client = _client(touch)
    response = client.post(_url(touch), json={})
    assert response.json() == "POST" and "seen=1" in response.headers["set-cookie"]


def test_a_response_returned_by_the_function_is_sent_as_it_is():
    client = _client(custom_answer)
    response = client.post(_url(custom_answer), json={})
    assert (response.status_code, response.text) == (201, "custom")


class TestFormWithoutJavaScript:
    def test_the_fields_are_read_and_the_visitor_goes_back(self):
        client = _client(create_user)
        response = client.post(
            _url(create_user),
            data={"name": "Ada", "age": "36"},
            headers={"referer": "http://testserver/users?page=2"},
            follow_redirects=False,
        )
        assert (response.status_code, response.headers["location"]) == (303, "/users?page=2")

    def test_a_referer_from_another_site_goes_home(self):
        client = _client(create_user)
        response = client.post(
            _url(create_user),
            data={"name": "Ada"},
            headers={"referer": "http://elsewhere.test/x"},
            follow_redirects=False,
        )
        assert response.headers["location"] == "/"

    def test_an_invalid_form_is_a_422(self):
        client = _client(create_user)
        assert client.post(_url(create_user), data={"age": "1"}).status_code == 422


class TestOrigin:
    def test_a_call_from_another_site_is_refused(self):
        client = _client(create_user)
        response = client.post(
            _url(create_user), json={"name": "Ada"}, headers={"origin": "http://evil.test"}
        )
        assert response.status_code == 403

    def test_a_call_from_the_same_site_is_accepted(self):
        client = _client(create_user)
        response = client.post(
            _url(create_user), json={"name": "Ada"}, headers={"origin": "http://testserver"}
        )
        assert response.status_code == 200

    def test_a_listed_origin_is_accepted(self, monkeypatch):
        monkeypatch.setenv("NEXY_ALLOWED_ORIGINS", "https://app.example.com")
        client = _client(create_user)
        response = client.post(
            _url(create_user),
            json={"name": "Ada"},
            headers={"origin": "https://app.example.com", "sec-fetch-site": "cross-site"},
        )
        assert response.status_code == 200

    def test_a_cross_site_fetch_without_origin_is_refused(self):
        client = _client(create_user)
        response = client.post(
            _url(create_user), json={"name": "Ada"}, headers={"sec-fetch-site": "cross-site"}
        )
        assert response.status_code == 403


class TestRevalidate:
    def test_the_paths_are_sent_to_the_browser(self):
        client = _client(refresh_users)
        response = client.post(_url(refresh_users), json={})
        assert response.headers["x-nexy-revalidate"] == "/users"

    def test_no_path_means_the_current_page(self):
        client = _client(refresh_current)
        response = client.post(_url(refresh_current), json={})
        assert response.headers["x-nexy-revalidate"] == "*"

    def test_an_action_that_does_not_ask_sends_no_header(self):
        client = _client(create_user)
        response = client.post(_url(create_user), json={"name": "Ada"})
        assert "x-nexy-revalidate" not in response.headers

    def test_outside_an_action_it_does_nothing(self):
        revalidate("/users")


def test_the_path_depends_on_the_secret(monkeypatch):
    _client(create_user)
    first = _url(create_user)
    ACTIONS_STORE.path_map.clear()
    monkeypatch.setenv("NEXY_ACTION_SECRET", "another")
    forget_secret()
    ActionEngine().include_router(FastAPI())
    assert _url(create_user) != first


def test_the_secret_is_kept_in_the_project_when_none_is_set(monkeypatch, tmp_path):
    monkeypatch.delenv("NEXY_ACTION_SECRET")
    forget_secret()
    first = ACTIONS_STORE._generate_hash("a.b")
    forget_secret()
    assert ACTIONS_STORE._generate_hash("a.b") == first
    assert (tmp_path / "__nexy__" / "action.key").exists()
