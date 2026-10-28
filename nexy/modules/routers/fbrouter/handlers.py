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

    def __init__(self, component: Callable[..., str], revalidate: int) -> None:
        self._component = component
        self._signature = inspect.signature(component)
        self._revalidate = revalidate

    def _render(self, params: dict[str, str]) -> str:
        result = self._component(**coerce_path_params(self._signature, params))
        return result if isinstance(result, str) else "".join(result)

    def _store(self, key: str, body: str) -> str:
        REVALIDATE_CACHE.set(key, body, self._revalidate)
        return body

    def response(self, body: str | None) -> HTMLResponse:
        window = self._revalidate
        control = f"public, s-maxage={window}, stale-while-revalidate={window}"
        return HTMLResponse(body, headers={"cache-control": control})

    async def _regenerate(self, key: str, params: dict[str, str]) -> None:
        self._store(key, self._render(params))

    async def handle(self, request: Request) -> HTMLResponse:
        """Serve the page of this URL: each URL of a dynamic route is cached on its own."""
        key, params = request.scope["path"], dict(request.path_params)
        cached = REVALIDATE_CACHE.get(key)
        if cached is None:
            return self.response(self._store(key, self._render(params)))
        if REVALIDATE_CACHE.is_stale(key):
            asyncio.create_task(self._regenerate(key, params))
        return self.response(cached)


def make_isr_handler(component: Callable[..., str], revalidate: int) -> Callable[..., Any]:
    """A handler with incremental static regeneration: see `_IncrementalPage`."""
    page = _IncrementalPage(component, revalidate)

    async def handler(request: Request) -> HTMLResponse:
        return await page.handle(request)

    handler.__name__ = component.__name__
    handler.__doc__ = component.__doc__
    return handler
