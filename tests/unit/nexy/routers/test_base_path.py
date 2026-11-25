"""The public prefix declared by `useBasePath` answers for the whole application (#468)."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from nexy.helpers.server.dev_mode import DEV_ENV_VAR


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, ""), ("/", ""), ("app", "/app"), ("/app/", "/app"), ("/a/b", "/a/b")],
)
def test_normalize_base_path_accepts_common_spellings(value: str | None, expected: str) -> None:
    from nexy.modules.routers.base_path import normalize_base_path

    assert normalize_base_path(value) == expected


def test_public_url_prefixes_a_root_relative_path(nexy_project) -> None:
    from nexy.core.config import Config
    from nexy.modules.routers.base_path import public_url

    nexy_project('useBasePath = "/app"')
    Config()

    assert public_url("/logo.svg") == "/app/logo.svg"


def test_public_url_without_a_base_keeps_the_path(nexy_project) -> None:
    from nexy.core.config import Config
    from nexy.modules.routers.base_path import public_url

    nexy_project("")
    Config()

    assert public_url("/logo.svg") == "/logo.svg"


def test_public_url_leaves_an_external_url_alone(nexy_project) -> None:
    from nexy.core.config import Config
    from nexy.modules.routers.base_path import public_url

    nexy_project('useBasePath = "/app"')
    Config()

    assert public_url("https://example.com/a") == "https://example.com/a"


def _scope(path: str, kind: str = "http") -> dict[str, Any]:
    return {"type": kind, "method": "GET", "path": path, "raw_path": path.encode(), "headers": []}


def _run(base: str, scope: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Send one scope through the middleware: the downstream scope and the messages sent back."""
    from nexy.modules.routers.base_path import BasePathMiddleware

    seen: list[dict[str, Any]] = []
    sent: list[dict[str, Any]] = []

    async def inner(inner_scope: dict[str, Any], _receive: Any, _send: Any) -> None:
        seen.append(dict(inner_scope))

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    asyncio.run(BasePathMiddleware(inner, base)(scope, receive, send))
    return (seen[0] if seen else None), sent


@pytest.mark.parametrize(
    ("path", "expected", "raw"),
    [("/app/about", "/about", b"/about"), ("/app", "/", b"/")],
)
def test_base_path_middleware_strips_the_prefix(path: str, expected: str, raw: bytes) -> None:
    seen, _ = _run("/app", _scope(path))

    assert ((seen or {})["path"], (seen or {})["raw_path"]) == (expected, raw)


def test_base_path_middleware_accepts_a_scope_without_raw_path() -> None:
    scope = _scope("/app/about")
    del scope["raw_path"]
    seen, _ = _run("/app", scope)

    assert (seen or {})["path"] == "/about"


def test_base_path_middleware_rejects_a_request_outside_the_prefix() -> None:
    _, sent = _run("/app", _scope("/about"))

    assert sent[0]["status"] == 404


def test_base_path_middleware_rejects_a_websocket_outside_the_prefix() -> None:
    _, sent = _run("/app", _scope("/_nexy/hmr", "websocket"))

    assert sent[0]["type"] == "websocket.close"


def test_base_path_middleware_passes_a_lifespan_scope_through() -> None:
    seen, _ = _run("/app", _scope("", "lifespan"))

    assert (seen or {})["type"] == "lifespan"


def _client(nexy_project, attrs: str) -> TestClient:
    from nexy.modules.routers.app import AppServer

    nexy_project(attrs)
    Path("src/routes").mkdir(parents=True)
    (Path("src/routes") / "about.nexy").write_text("<p>About</p>\n", encoding="utf-8")
    Path("public").mkdir()
    (Path("public") / "logo.svg").write_text("<svg></svg>\n", encoding="utf-8")
    return TestClient(AppServer().run(), raise_server_exceptions=False)


def test_the_app_serves_a_page_under_the_prefix(nexy_project) -> None:
    assert _client(nexy_project, 'useBasePath = "/app"').get("/app/about").status_code == 200


def test_the_app_404s_a_page_outside_the_prefix(nexy_project) -> None:
    assert _client(nexy_project, 'useBasePath = "/app"').get("/about").status_code == 404


def test_the_app_404s_the_root_under_a_prefix(nexy_project) -> None:
    assert _client(nexy_project, 'useBasePath = "/app"').get("/").status_code == 404


def test_the_app_serves_a_public_file_under_the_prefix(nexy_project) -> None:
    assert _client(nexy_project, 'useBasePath = "/app"').get("/app/logo.svg").status_code == 200


def test_the_app_keeps_the_root_when_no_prefix_is_set(nexy_project) -> None:
    assert _client(nexy_project, "").get("/about").status_code == 200


def test_the_app_serves_docs_under_the_prefix(nexy_project, monkeypatch) -> None:
    monkeypatch.delenv(DEV_ENV_VAR, raising=False)
    client = _client(nexy_project, 'useBasePath = "/app"\nuseDocs = True')

    assert client.get("/app/docs").status_code == 200


def test_the_app_points_docs_at_the_prefixed_schema(nexy_project, monkeypatch) -> None:
    monkeypatch.delenv(DEV_ENV_VAR, raising=False)
    client = _client(nexy_project, 'useBasePath = "/app"\nuseDocs = True')

    assert "/app/openapi.json" in client.get("/app/docs").text
