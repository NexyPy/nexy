"""The request log of `nx dev` and `nx start`: one line per request, with its duration."""

# ruff: noqa: ARG001 - ASGI callables take (scope, receive, send) whether they use them or not

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from rich.text import Text

from nexy.helpers.server.access_log import AccessLogMiddleware, format_duration, format_request


def _plain(markup: str) -> str:
    return Text.from_markup(markup).plain


class TestFormat:
    def test_a_request_line_reads_method_path_status_and_duration(self):
        assert _plain(format_request("GET", "/users", 200, 0.012)) == " GET /users 200 in 12ms"

    @pytest.mark.parametrize(
        ("seconds", "text"),
        [(0.0004, "0ms"), (0.012, "12ms"), (0.9996, "1000ms"), (1.0, "1.0s"), (12.34, "12.3s")],
    )
    def test_durations_switch_to_seconds_from_one_second(self, seconds, text):
        assert format_duration(seconds) == text

    @pytest.mark.parametrize(
        ("status", "colour"),
        [(200, "green"), (304, "cyan"), (404, "yellow"), (422, "yellow"), (500, "red")],
    )
    def test_the_status_colour_follows_its_class(self, status, colour):
        assert f"[{colour}]{status}[/{colour}]" in format_request("GET", "/", status, 0.001)

    def test_a_slow_request_is_flagged(self):
        assert "[yellow]1.5s[/yellow]" in format_request("GET", "/", 200, 1.5)
        assert "[dim]12ms[/dim]" in format_request("GET", "/", 200, 0.012)

    def test_markup_in_a_path_is_not_interpreted(self):
        line = format_request("GET", "/[bold]x[/bold]", 200, 0.001)
        assert "/[bold]x[/bold]" in _plain(line)


async def _call(app: Any, path: str = "/", method: str = "GET", scope_type: str = "http"):
    scope = {"type": scope_type, "method": method, "path": path, "query_string": b"", "headers": []}
    sent: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(scope, receive, send)
    return sent


def _responder(status: int = 200):
    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": status, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    return app


class TestMiddleware:
    def test_each_request_is_logged_once_with_its_status(self):
        lines: list[str] = []
        asyncio.run(_call(AccessLogMiddleware(_responder(404), log=lines.append), "/missing"))
        assert len(lines) == 1
        assert _plain(lines[0]).startswith(" GET /missing 404 in ")

    def test_the_response_goes_through_unchanged(self):
        sent = asyncio.run(_call(AccessLogMiddleware(_responder(), log=lambda _l: None)))
        assert [m["type"] for m in sent] == ["http.response.start", "http.response.body"]

    @pytest.mark.parametrize(
        "path",
        ["/_nexy/hmr", "/__nexy__/main.ts", "/@vite/client", "/@id/x", "/node_modules/.vite/a.js"],
    )
    def test_framework_urls_are_not_logged(self, path):
        lines: list[str] = []
        asyncio.run(_call(AccessLogMiddleware(_responder(), log=lines.append), path))
        assert lines == []

    def test_a_crash_is_logged_as_a_500_and_raised(self):
        async def failing(scope, receive, send):
            raise RuntimeError("boom")

        lines: list[str] = []
        with pytest.raises(RuntimeError):
            asyncio.run(_call(AccessLogMiddleware(failing, log=lines.append), "/x"))
        assert _plain(lines[0]).startswith(" GET /x 500 in ")

    def test_other_scopes_pass_through_unlogged(self):
        reached: list[str] = []

        async def app(scope, receive, send):
            reached.append(scope["type"])

        lines: list[str] = []
        asyncio.run(
            _call(AccessLogMiddleware(app, log=lines.append), "/ws", scope_type="websocket")
        )
        assert reached == ["websocket"] and lines == []
