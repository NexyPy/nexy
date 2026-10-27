"""The functions FastAPI calls for a page: render it, stream it, or serve it from the ISR cache."""

from __future__ import annotations

import asyncio
import functools
import importlib
import inspect
from collections.abc import Callable
from typing import Any

from fastapi import Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, StreamingResponse

from nexy.modules.runtime.cache import REVALIDATE_CACHE

_CASTS: dict[Any, Callable[[str], Any]] = {int: int, float: float}
_INHERITED = ("__nexy_guards__", "__nexy_middlewares__")


def lazy_component(
    import_path: str, comp_name: str, original: Callable[..., str]
) -> Callable[..., str]:
    """A wrapper that imports the compiled module when the page is requested.

    After the watcher purges the module from sys.modules, the next request imports fresh code
    from the VFS: no server restart for .nexy/.md/.mdx edits.
    """

    @functools.wraps(original)
    def wrapper(**kwargs: Any) -> str:
        module = importlib.import_module(import_path)
        component = getattr(module, comp_name, None) or original
        return component(**kwargs)

    return wrapper


def _cast(value: str, annotation: Any) -> Any:
    """*value* as the declared int or float; left as text when it does not convert."""
    convert = _CASTS.get(annotation)
    if convert is None:
        return value
    try:
        return convert(value)
    except (TypeError, ValueError):
        return value


def coerce_path_params(sig: inspect.Signature, path_params: dict[str, str]) -> dict[str, Any]:
    """Cast dynamic path segments to the types the component signature declares."""
    coerced = {}
    for name, value in path_params.items():
        param = sig.parameters.get(name)
        coerced[name] = _cast(value, param.annotation if param else inspect.Parameter.empty)
    return coerced


def stream_body(result: str | Any) -> Any:
    """A streaming body: a generator component yields chunks as it makes them; a string is one."""
    if isinstance(result, str):
        return iter([result.encode("utf-8")])
    return (chunk.encode("utf-8") if isinstance(chunk, str) else chunk for chunk in result)


def _carry_over(handler: Callable[..., Any], component: Callable[..., Any]) -> None:
    handler.__name__ = component.__name__
    handler.__doc__ = component.__doc__
    for attribute in _INHERITED:
        if hasattr(component, attribute):
            setattr(handler, attribute, getattr(component, attribute))


def make_request_handler(component: Callable[..., str]) -> Callable[..., Any]:
    """A request handler with the fixed ``(request)`` signature FastAPI needs.

    Compiled components take ``**kwargs`` (props injection); FastAPI would treat ``kwargs`` as a
    required query parameter and answer 422. Reading ``request.path_params`` keeps the route free
    of signature validation and still forwards ``[slug]`` as ``slug``. The answer is streamed.
    """
    signature = inspect.signature(component)
    # A component that waits on I/O (a document rendered by Node) must not stall the event loop.
    blocking = bool(getattr(component, "__nexy_blocking__", False))

    async def handler(request: Request) -> StreamingResponse:
        params = coerce_path_params(signature, request.path_params)
        result = await run_in_threadpool(component, **params) if blocking else component(**params)
        return StreamingResponse(stream_body(result), media_type="text/html")

    _carry_over(handler, component)
    return handler


class _IncrementalPage:
    """A page served stale-while-revalidate: fresh, stale while regenerating, or rendered once."""

    def __init__(self, component: Callable[..., str], pathname: str, revalidate: int) -> None:
        self._component = component
        self._signature = inspect.signature(component)
        self._pathname = pathname
        self._revalidate = revalidate

    def _render(self) -> str:
        result = self._component(**coerce_path_params(self._signature, {}))
        return result if isinstance(result, str) else "".join(result)

    def _store(self, body: str) -> str:
        REVALIDATE_CACHE.set(self._pathname, body, self._revalidate)
        return body

    def response(self, body: str | None) -> HTMLResponse:
        window = self._revalidate
        control = f"public, s-maxage={window}, stale-while-revalidate={window}"
        return HTMLResponse(body, headers={"cache-control": control})

    async def _regenerate(self) -> None:
        self._store(self._render())

    async def handle(self) -> HTMLResponse:
        cached = REVALIDATE_CACHE.get(self._pathname)
        if cached is None:
            return self.response(self._store(self._render()))
        if REVALIDATE_CACHE.is_stale(self._pathname):
            asyncio.create_task(self._regenerate())
        return self.response(cached)


def make_isr_handler(
    component: Callable[..., str], pathname: str, revalidate: int
) -> Callable[..., Any]:
    """A handler with incremental static regeneration: see `_IncrementalPage`."""
    page = _IncrementalPage(component, pathname, revalidate)

    async def handler(request: Request) -> HTMLResponse:  # noqa: ARG001
        return await page.handle()

    handler.__name__ = component.__name__
    handler.__doc__ = component.__doc__
    return handler
