"""Refuse the actions that another website makes the visitor's browser send."""

from __future__ import annotations

import os
from urllib.parse import urlparse

from starlette.requests import Request


def _allowed() -> set[str]:
    listed = os.environ.get("NEXY_ALLOWED_ORIGINS", "")
    return {urlparse(item.strip()).netloc or item.strip() for item in listed.split(",") if item}


def _host(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-host", "")
    return forwarded.split(",")[0].strip() or request.headers.get("host", "")


def is_same_origin(request: Request) -> bool:
    """True for a request from this site, a listed origin, or a client that sends no Origin."""
    if request.headers.get("sec-fetch-site") == "cross-site":
        return _origin_is_allowed(request)
    origin = request.headers.get("origin")
    if origin is None:
        return True
    return _origin_is_allowed(request)


def _origin_is_allowed(request: Request) -> bool:
    origin = request.headers.get("origin", "")
    netloc = urlparse(origin).netloc
    return bool(netloc) and (netloc == _host(request) or netloc in _allowed())
