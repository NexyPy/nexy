"""Adds the routes the scanner found to a router: API handlers, sockets and pages."""

from __future__ import annotations

import re
from contextlib import suppress
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from nexy.core.http_methods import HTTP_METHODS
from nexy.helpers.common.console import console
from nexy.modules.routers.fbrouter.dependencies import RouteDependencies
from nexy.modules.routers.fbrouter.handlers import (
    lazy_component,
    make_isr_handler,
    make_request_handler,
)
from nexy.modules.routers.fbrouter.middleware import RouteMiddleware
from nexy.modules.routers.fbrouter.scanner import RouteModule
from nexy.modules.routers.fbrouter.validator import RouteValidator


def path_sort_key(path: str) -> tuple[int, int]:
    """Static paths first, then dynamic ones with the most fixed segments, catch-alls last."""
    if re.search(r"\{[^}]+:path\}", path):
        return 2, 0
    if "{" in path:
        literals = sum(1 for segment in path.split("/") if segment and not segment.startswith("{"))
        return 1, -literals
    return 0, 0


def revalidate_window(module: Any) -> int | None:
    """The per-route ISR window, in seconds, from the module's frontmatter."""
    value = getattr(module, "revalidate", None)
    return value if isinstance(value, int) and value > 0 else None


def _remember_source(handler: Any, source: str) -> None:
    """The file a handler comes from, for the dev toolbar's "open in editor"."""
    with suppress(AttributeError, TypeError):
        handler.__nexy_source__ = source


def _page_handler(route: RouteModule, component: Any) -> Any:
    """The request handler of a page: incremental when the module revalidates, plain otherwise."""
    window = revalidate_window(route.module)
    if window is None:
        return make_request_handler(component)
    return make_isr_handler(component, window)


class RouteRegistrar:
    """Registers `RouteModule`s on *router*, the more specific paths first."""

    def __init__(self, router: APIRouter) -> None:
        self._router = router

    def register(self, routes: list[RouteModule]) -> None:
        for route in sorted(routes, key=lambda item: path_sort_key(item.pathname)):
            folder = [Depends(dep) for dep in RouteDependencies.collect(route.source)]
            if route.type == "api":
                self._api(route, folder)
            else:
                self._page(route, folder)

    def _api(self, route: RouteModule, folder: list[Any]) -> None:
        for method in HTTP_METHODS:
            if handler := getattr(route.module, method, None):
                self._api_method(route, method, handler, folder)
        if socket_handler := getattr(route.module, "SOCKET", None):
            self._router.websocket(route.pathname)(socket_handler)

    def _api_method(self, route: RouteModule, method: str, handler: Any, folder: list[Any]) -> None:
        RouteValidator.validate_sig(handler, route.pathname, method)
        _remember_source(handler, route.source)
        # Outermost first: routes root down to the directory, then the handler.
        dependencies = folder + RouteMiddleware.resolve(handler)
        meta = getattr(handler, "__nexy_response_meta__", None)
        self._router.add_api_route(
            path=route.pathname,
            endpoint=handler,
            methods=[method],
            dependencies=dependencies or None,
            name=method,
            tags=[route.pathname],
            status_code=meta.status_code if meta else None,
        )

    def _page(self, route: RouteModule, folder: list[Any]) -> None:
        component = getattr(route.module, route.comp_name, None)
        if not component:
            console.print(
                f"  [yellow]WARN[/yellow] Route '{route.pathname}' skipped - "
                f"component '{route.comp_name}' not found in {route.source}"
            )
            return
        component = lazy_component(route.import_path, route.comp_name, component)
        handler = _page_handler(route, component)
        _remember_source(handler, route.source)
        self._router.get(
            route.pathname,
            response_class=HTMLResponse,
            dependencies=(folder + RouteMiddleware.resolve(component)) or None,
            name=handler.__name__,
            description=component.__doc__ or "",
            tags=[route.pathname],
        )(handler)
