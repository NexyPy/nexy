"""The pages under /docs: a moved page answers with a 301, a translated one in its language."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

from src.content import localize, redirect_of, slug_of


async def _localized(response: Response, address: str) -> Response:
    """The same page with the words of the site in the language of its address."""
    if not response.headers.get("content-type", "").startswith("text/html"):
        return response
    body = b"".join([chunk async for chunk in response.body_iterator])  # type: ignore[attr-defined]
    headers = {k: v for k, v in response.headers.items() if k.lower() != "content-length"}
    html = localize(body.decode("utf-8"), address)
    return HTMLResponse(html, status_code=response.status_code, headers=headers)


async def middleware(request: Request, call_next) -> Response:
    address = slug_of(request.url.path)
    destination = redirect_of(address)
    if destination:
        return RedirectResponse(destination, status_code=301)
    return await _localized(await call_next(request), address)
