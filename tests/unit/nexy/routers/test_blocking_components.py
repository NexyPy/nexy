"""A component that waits on I/O must not stall the event loop that serves every other request."""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any

from nexy.modules.routers.fbrouter.handlers import make_request_handler


class _Request:
    path_params: dict[str, Any] = {}


def _handler(component):
    return make_request_handler(component)


async def _body(response) -> str:
    chunks = [chunk async for chunk in response.body_iterator]
    return b"".join(c if isinstance(c, bytes) else c.encode() for c in chunks).decode()


def test_a_blocking_component_runs_off_the_event_loop_thread():
    seen: dict[str, int] = {}

    def component(**_kwargs: Any) -> str:  # noqa: ARG001
        seen["thread"] = threading.get_ident()
        return "<p>ok</p>"

    component.__nexy_blocking__ = True  # type: ignore[attr-defined]

    async def go() -> str:
        loop_thread = threading.get_ident()
        body = await _body(await _handler(component)(_Request()))
        assert seen["thread"] != loop_thread
        return body

    assert asyncio.run(go()) == "<p>ok</p>"


def test_an_ordinary_component_still_runs_inline():
    seen: dict[str, int] = {}

    def component(**_kwargs: Any) -> str:  # noqa: ARG001
        seen["thread"] = threading.get_ident()
        return "<p>ok</p>"

    async def go() -> None:
        loop_thread = threading.get_ident()
        await _body(await _handler(component)(_Request()))
        assert seen["thread"] == loop_thread

    asyncio.run(go())


def test_the_loop_keeps_answering_while_a_blocking_component_waits():
    def slow(**_kwargs: Any) -> str:  # noqa: ARG001
        time.sleep(0.4)
        return "slow"

    slow.__nexy_blocking__ = True  # type: ignore[attr-defined]

    async def go() -> float:
        ticks: list[float] = []

        async def render() -> str:
            return await _body(await _handler(slow)(_Request()))

        async def ticker() -> None:
            for _ in range(6):
                ticks.append(time.perf_counter())
                await asyncio.sleep(0.05)

        await asyncio.gather(ticker(), render())
        return max(b - a for a, b in zip(ticks, ticks[1:], strict=False))

    assert asyncio.run(go()) < 0.3  # a stalled loop would show a gap of about 0.4 s


def test_the_lazy_wrapper_keeps_the_blocking_mark():
    from nexy.modules.routers.fbrouter.handlers import lazy_component

    def component(**_kwargs: Any) -> str:  # noqa: ARG001
        return ""

    component.__nexy_blocking__ = True  # type: ignore[attr-defined]
    wrapped = lazy_component("os", "component", component)
    assert wrapped.__nexy_blocking__ is True  # type: ignore[attr-defined]


def test_a_generated_document_component_is_marked_blocking():
    from nexy.modules.compiler.frontend_route import _document_module

    source = _document_module(
        "Home",
        page_file="/src/routes/home.tsx",
        layouts=[],
        static_stem="/src/routes/home",
        dynamic=False,
    )
    assert "Home.__nexy_blocking__ = True" in source
    compile(source, "home.py", "exec")
