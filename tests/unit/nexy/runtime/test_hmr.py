"""The hot-reload channel: browsers connect, get reload and error messages, and are bounded."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from nexy.modules.routers.hmr import setup_hmr
from nexy.modules.runtime.hmr import HMR_MANAGER, MAX_CONNECTIONS, HMRManager


class FakeSocket:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.accepted = False
        self.closed_with: int | None = None
        self.sent: list[dict[str, Any]] = []

    async def accept(self) -> None:
        self.accepted = True

    async def close(self, code: int = 1000) -> None:
        self.closed_with = code

    async def send_json(self, data: dict[str, Any]) -> None:
        if self.fail:
            raise RuntimeError("gone")
        self.sent.append(data)


@pytest.fixture(autouse=True)
def _no_connections():
    HMR_MANAGER._connections.clear()
    yield
    HMR_MANAGER._connections.clear()


def _run(coroutine):
    return asyncio.run(coroutine)


def test_the_manager_is_a_singleton():
    assert HMRManager() is HMR_MANAGER


def test_a_browser_is_accepted_and_kept():
    socket = FakeSocket()
    assert _run(HMR_MANAGER.connect(socket)) is True
    assert socket.accepted and socket in HMR_MANAGER._connections


def test_a_browser_over_the_limit_is_turned_away():
    for _ in range(MAX_CONNECTIONS):
        _run(HMR_MANAGER.connect(FakeSocket()))
    extra = FakeSocket()
    assert _run(HMR_MANAGER.connect(extra)) is False
    assert extra.closed_with == 1013 and not extra.accepted


def test_disconnecting_frees_a_place():
    sockets = [FakeSocket() for _ in range(MAX_CONNECTIONS)]
    for socket in sockets:
        _run(HMR_MANAGER.connect(socket))
    HMR_MANAGER.disconnect(sockets[0])
    assert _run(HMR_MANAGER.connect(FakeSocket())) is True


def test_disconnecting_an_unknown_browser_is_harmless():
    HMR_MANAGER.disconnect(FakeSocket())


def test_a_reload_reaches_every_browser():
    first, second = FakeSocket(), FakeSocket()
    _run(HMR_MANAGER.connect(first))
    _run(HMR_MANAGER.connect(second))
    _run(HMR_MANAGER.broadcast_reload("/about"))
    assert first.sent == second.sent == [{"type": "nexy:reload", "path": "/about"}]


def test_errors_reach_every_browser():
    socket = FakeSocket()
    _run(HMR_MANAGER.connect(socket))
    _run(HMR_MANAGER.broadcast_error([{"file": "a.nexy"}]))
    assert socket.sent == [{"type": "nexy:error", "errors": [{"file": "a.nexy"}]}]


def test_a_browser_that_cannot_be_reached_is_dropped():
    dead = FakeSocket(fail=True)
    _run(HMR_MANAGER.connect(dead))
    _run(HMR_MANAGER.broadcast_reload())
    assert dead not in HMR_MANAGER._connections


def test_a_failing_error_message_drops_the_browser_too():
    dead = FakeSocket(fail=True)
    _run(HMR_MANAGER.connect(dead))
    _run(HMR_MANAGER.broadcast_error([]))
    assert dead not in HMR_MANAGER._connections


def test_the_socket_endpoint_accepts_a_browser_and_forgets_it_on_close():
    app = FastAPI()
    setup_hmr(app)
    with TestClient(app).websocket_connect("/_nexy/hmr") as socket:
        assert len(HMR_MANAGER._connections) == 1
        socket.send_text("ping")
    assert HMR_MANAGER._connections == []
