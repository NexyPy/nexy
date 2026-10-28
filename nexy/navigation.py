"""Leave a page, or answer 404, 401 and 403, from anywhere in a request.

Each call raises an HTTP exception, so it works the same in a page, an API handler, a modular
controller, an action and a dependency: the router turns it into the answer. The names are the
ones of the client router (`redirect`, `notFound`), so the vocabulary is the same on both sides.

Example:
    >>> from nexy import notFound, redirect
    >>> def GET(slug: str):
    ...     post = find(slug) or notFound("No such post")
"""

from __future__ import annotations

from typing import NoReturn

from fastapi import HTTPException

__all__ = ["forbidden", "notFound", "permanentRedirect", "redirect", "unauthorized"]

_REDIRECT_STATUSES = (301, 302, 303, 307, 308)


def redirect(url: str, status: int = 307) -> NoReturn:
    """Send the visitor to *url* and stop handling the request.

    Args:
        url: Where to go: a path (`/login`) or a full address. Never build it from an input you
            did not check: an open redirect sends visitors wherever the input says.
        status: A redirect status. `307` keeps the method of the request, `303` turns a POST
            into a GET (after a form), `301` and `308` are permanent.

    Raises:
        ValueError: If *status* is not a redirect status or *url* holds a line break.
        HTTPException: Always, with the status and the `Location` header.
    """
    if status not in _REDIRECT_STATUSES:
        raise ValueError(f"{status} is not a redirect status: use one of {_REDIRECT_STATUSES}")
    if "\r" in url or "\n" in url:
        raise ValueError("a line break in the destination of a redirect is refused")
    raise HTTPException(status_code=status, headers={"Location": url})


def permanentRedirect(url: str) -> NoReturn:
    """Send the visitor to *url* for good (308): browsers and search engines remember it."""
    redirect(url, status=308)


def notFound(detail: str | None = None) -> NoReturn:
    """Answer 404: the page of the folder for a browser, JSON for an API client.

    Args:
        detail: What is missing, for the API client; the default is "Not Found".
    """
    raise HTTPException(status_code=404, detail=detail)


def forbidden(detail: str | None = None) -> NoReturn:
    """Answer 403: the visitor is known but may not see this."""
    raise HTTPException(status_code=403, detail=detail)


def unauthorized(detail: str | None = None, scheme: str | None = None) -> NoReturn:
    """Answer 401: the visitor must identify themselves first.

    Args:
        detail: Why, for the API client.
        scheme: The authentication scheme to offer (`Bearer`, `Basic`), sent as
            `WWW-Authenticate` as the HTTP specification asks of a 401.
    """
    headers = {"WWW-Authenticate": scheme} if scheme else None
    raise HTTPException(status_code=401, detail=detail, headers=headers)
