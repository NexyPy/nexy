"""The request log of `nx dev` and `nx start`: one line per request, with its duration."""

# ruff: noqa: ARG001 - ASGI callables take (scope, receive, send) whether they use them or not

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from rich.text import Text

from nexy.helpers.server import access_log
from nexy.helpers.server.access_log import (
    DEVTOOLS_PROBE,
    AccessLogMiddleware,
    format_duration,
    format_request,
    paint_ansi,
    paint_plain,
)


def _plain(markup: str) -> str:
    return Text.from_markup(markup).plain


class TestFormat:
    def test_a_request_line_reads_method_path_status_and_duration(self):
        assert _plain(format_request("GET", "/users", 200, 0.012)) == "GET » /users 200 in 12ms"

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

    @pytest.mark.parametrize(
        ("status", "colour"), [(200, "green"), (302, "cyan"), (404, "yellow"), (500, "red")]
    )
    def test_the_verb_has_the_colour_of_the_status(self, status, colour):
        assert f"[{colour}]GET[/{colour}]" in format_request("GET", "/", status, 0.001)

    def test_a_slow_request_is_flagged(self):
        assert "[yellow]1.5s[/yellow]" in format_request("GET", "/", 200, 1.5)
        assert "[dim]12ms[/dim]" in format_request("GET", "/", 200, 0.012)

    def test_an_escape_in_a_path_is_written_percent_encoded(self):
        # uvicorn decodes the path: `/%1b[2J` arrives with a real escape, which clears a terminal.
        assert "/a%1B[2J" in format_request("GET", "/a\x1b[2J", 200, 0.0, paint_plain)

    def test_a_newline_in_a_path_cannot_start_a_forged_log_line(self):
        line = format_request("GET", "/a\nGET /admin 200 in 1ms", 200, 0.0, paint_plain)
        assert "\n" not in line

    def test_a_carriage_return_in_a_path_cannot_overwrite_the_line(self):
        assert "\r" not in format_request("GET", "/a\rGET /", 200, 0.0, paint_ansi)

    def test_a_c1_control_in_a_path_is_written_percent_encoded(self):
        assert "/a%9B" in format_request("GET", "/a\x9b", 200, 0.0, paint_plain)

    def test_a_path_in_another_script_is_kept_as_it_is(self):
        path = "/caf\u00e9/\u4e2d"
        assert path in format_request("GET", path, 200, 0.0, paint_plain)

    def test_a_separator_that_is_not_a_control_is_kept_as_it_is(self):
        path = "/a\u2028b"
        assert path in format_request("GET", path, 200, 0.0, paint_plain)

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
        assert _plain(lines[0]).startswith("GET » /missing 404 in ")

    def test_an_action_is_logged_by_its_name(self):
        lines: list[str] = []
        app = AccessLogMiddleware(_responder(), log=lines.append, names={"/_nx_1": "ping"}.get)
        asyncio.run(_call(app, "/_nx_1", method="POST"))
        assert _plain(lines[0]).startswith("ACTION » ping 200 in ")

    def test_a_path_with_no_action_keeps_its_verb_and_path(self):
        lines: list[str] = []
        app = AccessLogMiddleware(_responder(), log=lines.append, names={"/_nx_1": "ping"}.get)
        asyncio.run(_call(app, "/users"))
        assert _plain(lines[0]).startswith("GET » /users 200 in ")

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

    def test_a_path_given_as_quiet_is_not_logged(self):
        lines: list[str] = []
        app = AccessLogMiddleware(_responder(404), log=lines.append, quiet=(DEVTOOLS_PROBE,))
        asyncio.run(_call(app, DEVTOOLS_PROBE))
        assert lines == []

    def test_a_path_given_as_quiet_still_gets_its_answer(self):
        app = AccessLogMiddleware(_responder(404), log=lambda _l: None, quiet=(DEVTOOLS_PROBE,))
        sent = asyncio.run(_call(app, DEVTOOLS_PROBE))
        assert sent[0]["status"] == 404

    def test_the_devtools_probe_is_logged_without_the_quiet_list(self):
        lines: list[str] = []
        asyncio.run(_call(AccessLogMiddleware(_responder(404), log=lines.append), DEVTOOLS_PROBE))
        assert len(lines) == 1

    def test_a_crash_is_logged_as_a_500_and_raised(self):
        async def failing(scope, receive, send):
            raise RuntimeError("boom")

        lines: list[str] = []
        with pytest.raises(RuntimeError):
            asyncio.run(_call(AccessLogMiddleware(failing, log=lines.append), "/x"))
        assert _plain(lines[0]).startswith("GET » /x 500 in ")

    def test_other_scopes_pass_through_unlogged(self):
        reached: list[str] = []

        async def app(scope, receive, send):
            reached.append(scope["type"])

        lines: list[str] = []
        asyncio.run(_call(AccessLogMiddleware(app, log=lines.append), "/", scope_type="lifespan"))
        assert reached == ["lifespan"] and lines == []


def _socket(accepts: bool = True):
    async def app(scope, receive, send):
        if accepts:
            await send({"type": "websocket.accept"})
        else:
            await send({"type": "websocket.close", "code": 1008})

    return app


class TestSockets:
    def test_an_accepted_socket_is_logged_as_socket_with_status_101(self):
        lines: list[str] = []
        app = AccessLogMiddleware(_socket(), log=lines.append)
        asyncio.run(_call(app, "/chat", scope_type="websocket"))
        assert _plain(lines[0]).startswith("SOCKET » /chat 101 in ")

    def test_a_refused_socket_is_logged_as_403(self):
        lines: list[str] = []
        app = AccessLogMiddleware(_socket(accepts=False), log=lines.append)
        asyncio.run(_call(app, "/chat", scope_type="websocket"))
        assert _plain(lines[0]).startswith("SOCKET » /chat 403 in ")

    def test_a_socket_is_logged_once(self):
        lines: list[str] = []
        app = AccessLogMiddleware(_socket(), log=lines.append)
        asyncio.run(_call(app, "/chat", scope_type="websocket"))
        assert len(lines) == 1

    def test_the_framework_socket_is_not_logged(self):
        lines: list[str] = []
        app = AccessLogMiddleware(_socket(), log=lines.append)
        asyncio.run(_call(app, "/_nexy/hmr", scope_type="websocket"))
        assert lines == []

    def test_a_socket_that_crashes_before_accepting_is_a_500(self):
        async def failing(scope, receive, send):
            raise RuntimeError("boom")

        lines: list[str] = []
        with pytest.raises(RuntimeError):
            asyncio.run(
                _call(AccessLogMiddleware(failing, log=lines.append), "/c", scope_type="websocket")
            )
        assert _plain(lines[0]).startswith("SOCKET » /c 500 in ")


class TestWithoutRich:
    """The line a terminal shows, written without parsing markup: Rich costs most of a request."""

    def test_the_plain_line_reads_like_the_markup_line(self):
        line = format_request("GET", "/users", 200, 0.012, paint=paint_plain)
        assert line == "GET \u00bb /users 200 in 12ms"

    def test_the_ansi_line_colours_the_status(self):
        line = format_request("GET", "/", 200, 0.012, paint=paint_ansi)
        assert "\033[32m200\033[0m" in line

    def test_the_ansi_line_keeps_a_path_as_it_is(self):
        line = format_request("GET", "/[bold]x", 200, 0.012, paint=paint_ansi)
        assert " /[bold]x " in line

    def test_the_default_log_never_parses_markup(self, monkeypatch, capsys):
        def refuse(*_args, **_kwargs):
            raise AssertionError("console.print parses markup on every request")

        monkeypatch.setattr(access_log.console, "print", refuse)
        asyncio.run(_call(AccessLogMiddleware(_responder()), "/users"))
        assert "/users 200 in " in capsys.readouterr().out


class _Stream:
    """A console file that remembers each write."""

    def __init__(self) -> None:
        self.writes: list[str] = []

    def write(self, text: str) -> None:
        self.writes.append(text)

    def flush(self) -> None:
        return None


@pytest.fixture
def stream(monkeypatch):
    fake = _Stream()
    # Rich reads `_file`, else sys.stdout: replacing `file` would pin this test's stdout for good.
    monkeypatch.setattr(access_log.console, "_file", fake)
    return fake


class TestBatchedWrites:
    """A busy server writes the lines of one turn of the event loop at once, not one by one."""

    def test_the_lines_of_one_loop_turn_are_one_write(self, stream):
        async def two_lines() -> None:
            access_log._write_line("a")
            access_log._write_line("b")
            await asyncio.sleep(0)

        asyncio.run(two_lines())
        assert stream.writes == ["a\nb\n"]

    def test_a_line_is_written_by_the_next_loop_turn(self, stream):
        async def one_line() -> list[str]:
            access_log._write_line("a")
            await asyncio.sleep(0)
            return list(stream.writes)

        assert asyncio.run(one_line()) == ["a\n"]

    def test_a_line_outside_an_event_loop_is_written_at_once(self, stream):
        access_log._write_line("a")
        assert stream.writes == ["a\n"]

    def test_a_line_left_by_a_stopped_loop_is_written_with_the_next(self, stream, monkeypatch):
        stopped = asyncio.new_event_loop()
        stopped.close()
        monkeypatch.setattr(access_log, "_pending", ["a\n"])
        monkeypatch.setattr(access_log, "_flushing", {"loop": stopped})

        async def one_line() -> None:
            access_log._write_line("b")
            await asyncio.sleep(0)

        asyncio.run(one_line())
        assert stream.writes == ["a\nb\n"]
