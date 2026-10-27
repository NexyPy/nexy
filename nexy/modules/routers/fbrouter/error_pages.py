"""`notfound.nexy` and `errors.nexy`: the pages of a folder for its 404 and 500 answers."""

from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse

from nexy.modules.routers.crash import inspect_crash, log_crash


@dataclass(frozen=True)
class SpecialPage:
    """A special page found in the routes: the folder it speaks for and its component."""

    scope: str
    module: ModuleType
    comp: str


def pick(pages: list[SpecialPage], path: str) -> SpecialPage | None:
    """The page of the deepest folder that contains *path*."""
    candidates = [page for page in pages if path.startswith(page.scope)]
    return max(candidates, key=lambda page: len(page.scope), default=None)


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
    """Installs the 404 and 500 pages of the routes as exception handlers.

    A page at the routes root answers every request; one in a deeper folder only the requests
    under that folder, and the deepest wins.
    """

    def __init__(self, notfound: list[SpecialPage], errors: list[SpecialPage]) -> None:
        self._notfound = notfound
        self._errors = errors

    def register(self, app: FastAPI) -> None:
        root_notfound = next((page for page in self._notfound if page.scope == "/"), None)
        root_error = next((page for page in self._errors if page.scope == "/"), None)
        if root_notfound:
            self._handle(app, status.HTTP_404_NOT_FOUND, self._notfound, root_notfound)
        if root_error:
            self._handle(app, status.HTTP_500_INTERNAL_SERVER_ERROR, self._errors, root_error)

    @staticmethod
    def _handle(app: FastAPI, code: int, pages: list[SpecialPage], fallback: SpecialPage) -> None:
        async def handler(request: Request, exc: HTTPException | Exception) -> HTMLResponse:
            if code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                log_crash(request, inspect_crash(exc))
            return render(pick(pages, str(request.url.path)) or fallback, code)

        app.add_exception_handler(code, handler)
