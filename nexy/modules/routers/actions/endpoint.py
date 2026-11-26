"""The HTTP side of an action: read the input, run the function, shape the answer."""

from __future__ import annotations

import contextlib
import importlib.util
import inspect
import json
from collections.abc import Awaitable, Callable
from functools import cache
from typing import Any
from urllib.parse import parse_qsl, urlparse

from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from nexy.modules.routers.actions.origin import is_same_origin
from nexy.modules.routers.actions.revalidate import HEADER, header_value, start_collecting
from nexy.modules.routers.actions.spec import ActionSpec
from nexy.modules.routers.fastpath import encode_json, mark_raw
from nexy.modules.runtime.cache import get_isr_cache


def _is_json(request: Request) -> bool:
    return "json" in request.headers.get("content-type", "")


MULTIPART_MISSING = (
    "A form was sent as multipart/form-data, which needs the python-multipart package. "
    "Run: uv add python-multipart"
)


@cache
def _multipart_available() -> bool:
    """True when Starlette finds the parser it needs for a multipart body."""
    return importlib.util.find_spec("python_multipart") is not None


async def _payload(request: Request) -> dict[str, Any]:
    """The input of the call: a JSON object, or the fields of a form (repeated names are lists)."""
    if _is_json(request):
        body = await request.body()
        data = json.loads(body) if body else {}
        if not isinstance(data, dict):
            raise ValueError("The body must be a JSON object")
        return data
    if "multipart" in request.headers.get("content-type", ""):
        if not _multipart_available():
            raise RuntimeError(MULTIPART_MISSING)
        form = await request.form()
        pairs = [(key, str(value)) for key, value in form.multi_items()]
    else:
        pairs = parse_qsl((await request.body()).decode("utf-8"), keep_blank_values=True)
    return _group(pairs)


def _group(pairs: list[tuple[str, str]]) -> dict[str, Any]:
    """Form fields by name; a name that appears more than once is a list."""
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key not in payload:
            payload[key] = value
        elif isinstance(payload[key], list):
            payload[key].append(value)
        else:
            payload[key] = [payload[key], value]
    return payload


def _is_local_path(path: str) -> bool:
    """True for `/page`; `//site` and `/\\site` are read by browsers as another site."""
    return path.startswith("/") and not path.startswith(("//", "/\\"))


def _back(request: Request) -> str:
    """Where a form without JavaScript returns to: the page it was sent from."""
    referer = urlparse(request.headers.get("referer", ""))
    same_host = referer.netloc and referer.netloc == request.headers.get("host", "")
    if same_host and _is_local_path(referer.path):
        return referer.path + (f"?{referer.query}" if referer.query else "")
    return "/"


def _problem(status: int, detail: Any) -> JSONResponse:
    return JSONResponse({"detail": detail}, status_code=status)


def _invalid(error: ValidationError) -> JSONResponse:
    return _problem(422, json.loads(error.json(include_url=False, include_context=False)))


async def _call(
    spec: ActionSpec, values: dict[str, Any], request: Request, response: Response
) -> Any:
    extras = {"request": request, "response": response}
    values.update({name: extras[name] for name in spec.injected})
    if inspect.iscoroutinefunction(spec.handler):
        return await spec.handler(**values)
    result = await run_in_threadpool(spec.handler, **values)
    return await result if inspect.isawaitable(result) else result


def _with_headers_of(answer: Response, response: Response) -> Response:
    """Keep what the action set on its `response` argument: cookies and headers."""
    for key, value in response.raw_headers:
        if key != b"content-length":
            answer.raw_headers.append((key, value))
    return answer


def _invalidate(paths: list[str], request: Request) -> None:
    """Purge the ISR entries an action made stale; a broken store never fails the call."""
    if not paths:
        return
    cache = get_isr_cache()
    for path in paths:
        with contextlib.suppress(Exception):
            cache.invalidate(urlparse(_back(request)).path if path == "*" else path)


def _answer(result: Any, request: Request, collected: Any) -> Response:
    """A redirect back for a plain form post, JSON for a script; revalidated paths in a header."""
    if _is_json(request):
        # Straight to JSON: jsonable_encoder walks only what json cannot write (models, dates).
        answer: Response = Response(encode_json(result), media_type="application/json")
    else:
        answer = RedirectResponse(_back(request), status_code=303)
    if collected:
        answer.headers[HEADER] = header_value(collected)
    return answer


def make_endpoint(spec: ActionSpec) -> Callable[[Request], Awaitable[Response]]:
    """The route function of *spec*; it takes JSON from scripts and forms from plain HTML."""

    async def endpoint(request: Request) -> Response:
        if not is_same_origin(request):
            return _problem(403, "Cross-origin action calls are refused")
        try:
            values = spec.arguments(await _payload(request))
        except ValidationError as error:
            return _invalid(error)
        except ValueError as error:
            return _problem(400, str(error))
        collected = start_collecting()
        response = Response()
        result = await _call(spec, values, request, response)
        _invalidate(collected, request)
        if isinstance(result, Response):
            return result
        answer = _answer(result, request, collected)
        return _with_headers_of(answer, response)

    # It reads the Request itself and returns a Response: the fast path serves it without FastAPI.
    return mark_raw(endpoint)
