import importlib
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from nexy.core.config import Config
from nexy.decorators import Container
from nexy.helpers.common.console import console
from nexy.modules.routers.context import current_request


class PathMiddleware:
    """Sets current_request contextvar for the request scope."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        token = current_request.set(request)
        try:
            await self.app(scope, receive, send)
        finally:
            current_request.reset(token)
            Container.clear_request_scope()


def _optional_middleware(
    module: str, name: str, options: dict[str, Any]
) -> list[tuple[Any, dict[str, Any]]]:
    """A Starlette middleware that needs `itsdangerous`; without it, say so and go without."""
    try:
        middleware = getattr(importlib.import_module(module), name)
    except ImportError:
        console.print(f"[yellow]  install 'itsdangerous' for {name}[/yellow]")
        return []
    return [(middleware, options)]


def collect_middlewares(config: Config) -> list[tuple[Any, dict[str, Any]]]:
    """Build the (class, options) list implied by the project config."""
    middlewares: list[tuple[Any, dict[str, Any]]] = []
    if config.useCORS:
        middlewares.append((CORSMiddleware, config.useCORS))
    if config.useGZip:
        middlewares.append((GZipMiddleware, config.useGZip))
    if config.useTrustedHost:
        middlewares.append((TrustedHostMiddleware, config.useTrustedHost))
    if config.useSession:
        middlewares += _optional_middleware(
            "starlette.middleware.sessions", "SessionMiddleware", config.useSession
        )
    if config.useAuth:
        middlewares += _optional_middleware(
            "starlette.middleware.authentication", "AuthenticationMiddleware", config.useAuth
        )
    middlewares += [e for e in config.useMiddlewares if isinstance(e, tuple) and len(e) == 2]
    return middlewares


def setup_middlewares(server: FastAPI, config: Config) -> None:
    """Apply every config-driven middleware to *server*."""
    for cls, kwargs in collect_middlewares(config):
        server.add_middleware(cls, **kwargs)

    if config.useHTTPSRedirect:
        server.add_middleware(HTTPSRedirectMiddleware)
