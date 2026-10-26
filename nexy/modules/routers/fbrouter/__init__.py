"""File-based routing: every file of `src/routes` is a route."""

from fastapi import APIRouter, FastAPI

from nexy.modules.routers.fbrouter.discovery import RouteDiscovery
from nexy.modules.routers.fbrouter.error_pages import ErrorPages
from nexy.modules.routers.fbrouter.registrar import RouteRegistrar
from nexy.modules.routers.fbrouter.scanner import LOAD_FAILURES, RouteScanner, ScanResult


class FBRouter:
    """Scans the route files, registers them on a router, and installs their error pages."""

    def __init__(self, router: APIRouter | None = None) -> None:
        self.discovery = RouteDiscovery()
        # Registering on the application's own router keeps routes flat: a nested
        # include_router adds a routing level to every request.
        self.router = router if router is not None else APIRouter()
        self._flat = router is not None
        self.scan: ScanResult = RouteScanner(self.discovery).scan()
        RouteRegistrar(self.router).register(self.scan.routes)

    def register_on(self, app: FastAPI) -> None:
        if not self._flat:
            app.include_router(self.router)
        ErrorPages(self.scan.notfound, self.scan.errors).register(app)


__all__ = ["LOAD_FAILURES", "FBRouter"]
