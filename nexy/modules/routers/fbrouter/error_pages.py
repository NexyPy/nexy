"""``notfound.nexy``, ``errors.nexy``, ``forbidden.nexy`` and ``unauthorized.nexy``:

The pages of a folder for its error answers.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from types import ModuleType

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response

from nexy.modules.routers.crash import inspect_crash, log_crash, wants_json


@dataclass(frozen=True)
class SpecialPage:
    """A special page found in the routes: the folder it speaks for and its component."""

    scope: str
    module: ModuleType
    comp: str


def _contains(scope: str, path: str) -> bool:
    """Whether *path* is the folder *scope* or below it: `/blog` holds `/blog/x`, not `/blogger`."""
    return scope == "/" or path == scope or path.startswith(scope.rstrip("/") + "/")


def pick(pages: list[SpecialPage], path: str) -> SpecialPage | None:
    """The page of the deepest folder that contains *path*."""
    candidates = [page for page in pages if _contains(page.scope, path)]
    return max(candidates, key=lambda page: len(page.scope), default=None)


_ERROR_TEXT = {
    status.HTTP_404_NOT_FOUND: "Not Found",
    status.HTTP_403_FORBIDDEN: "Forbidden",
    status.HTTP_401_UNAUTHORIZED: "Unauthorized",
}


def _json_answer(code: int, exc: Exception) -> JSONResponse | None:
    """The answer for a JSON client, or None when this code has no JSON form (500)."""
    if code not in _ERROR_TEXT:
        return None
    detail = getattr(exc, "detail", _ERROR_TEXT[code])
    # Only 401 carries a header to build on: `WWW-Authenticate`.
    headers = getattr(exc, "headers", None) if code == status.HTTP_401_UNAUTHORIZED else None
    return JSONResponse({"detail": detail}, status_code=code, headers=headers)


def _default_response(code: int, exc: Exception) -> Response:
    """The built-in answer when the folder has no page for this code."""
    if code == status.HTTP_404_NOT_FOUND:
        from nexy.errors import NotFound

        return NotFound()
    if code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        from nexy.errors import InternalServerError

        return InternalServerError()
    from nexy.errors import error_page

    phrase = _ERROR_TEXT.get(code, "Error")
    response = error_page(code, phrase, str(getattr(exc, "detail", phrase)))
    response.headers.update(getattr(exc, "headers", None) or {})
    return response


def render(page: SpecialPage, status_code: int) -> HTMLResponse:
    """The page as an answer; the page itself failing never shows its exception to the client."""
    component = getattr(page.module, page.comp, None)
    if component is None:
        return HTMLResponse(f"<h1>{status_code}</h1>", status_code=status_code)
    from nexy.modules.runtime.importer import install_vfs_importer

    install_vfs_importer()
    try:
        body = component()
    except Exception:
        body = f"<h1>{status_code}</h1>"
    return HTMLResponse(body, status_code=status_code)


class ErrorPages:
    """Installs the 404, 403, 401 and 500 pages of the routes as exception handlers.

    A page at the routes root answers every request; one in a deeper folder only the requests
    under that folder, and the deepest wins.
    """

    def __init__(
        self,
        notfound: list[SpecialPage],
        errors: list[SpecialPage],
        forbidden: list[SpecialPage] | None = None,
        unauthorized: list[SpecialPage] | None = None,
    ) -> None:
        self._notfound = notfound
        self._errors = errors
        self._forbidden = forbidden or []
        self._unauthorized = unauthorized or []

    def register(self, app: FastAPI) -> None:
        root_notfound = next((page for page in self._notfound if page.scope == "/"), None)
        root_error = next((page for page in self._errors if page.scope == "/"), None)
        root_forbidden = next((page for page in self._forbidden if page.scope == "/"), None)
        root_unauthorized = next((page for page in self._unauthorized if page.scope == "/"), None)
        if root_notfound or self._notfound:
            self._handle(app, status.HTTP_404_NOT_FOUND, self._notfound, root_notfound)
        if root_error or self._errors:
            self._handle(app, status.HTTP_500_INTERNAL_SERVER_ERROR, self._errors, root_error)
        if root_forbidden or self._forbidden:
            self._handle(app, status.HTTP_403_FORBIDDEN, self._forbidden, root_forbidden)
        if root_unauthorized or self._unauthorized:
            self._handle(app, status.HTTP_401_UNAUTHORIZED, self._unauthorized, root_unauthorized)

    def _handle(
        self, app: FastAPI, code: int, pages: list[SpecialPage], fallback: SpecialPage | None
    ) -> None:
        app.add_exception_handler(code, _handler_for(code, pages, fallback))


def _handler_for(
    code: int, pages: list[SpecialPage], fallback: SpecialPage | None
) -> Callable[[Request, Exception], Awaitable[Response]]:
    """The exception handler answering *code* with the page of the deepest folder."""

    async def handler(request: Request, exc: HTTPException | Exception) -> Response:
        if code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            log_crash(request, inspect_crash(exc))
        if wants_json(request) and (answer := _json_answer(code, exc)) is not None:
            return answer
        page = pick(pages, str(request.url.path)) or fallback
        if page is None:
            return _default_response(code, exc)
        response = render(page, code)
        response.headers.update(getattr(exc, "headers", None) or {})
        return response

    return handler
