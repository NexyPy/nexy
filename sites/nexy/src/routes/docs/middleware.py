"""The old addresses of the docs: a moved page answers with a 301, never a 404."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from src.content import redirect_of, slug_of


async def middleware(request: Request, call_next) -> Response:
    destination = redirect_of(slug_of(request.url.path))
    if destination:
        return RedirectResponse(destination, status_code=301)
    return await call_next(request)
