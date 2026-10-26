import importlib.util
import inspect
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference
from starlette.exceptions import HTTPException
from starlette.types import ASGIApp

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common.console import console
from nexy.helpers.fs.packages import ensure_project_packages
from nexy.helpers.server.access_log import AccessLogMiddleware
from nexy.helpers.server.badge import BadgeMiddleware
from nexy.helpers.server.proxy import ViteProxyMiddleware, vite_proxy_port
from nexy.helpers.server.security_headers import SecurityHeadersMiddleware
from nexy.modules.routers.actions.engine import ACTION_ENGINE
from nexy.modules.routers.crash import handle_crash, is_dev
from nexy.modules.routers.error_handlers import (
    handle_http_exception,
    register_validation_error_handler,
)
from nexy.modules.routers.fastpath import install as install_fast_path
from nexy.modules.routers.fbrouter import FBRouter
from nexy.modules.routers.fbrouter.directory_middleware import (
    DirectoryMiddleware,
    Routes,
)
from nexy.modules.routers.fbrouter.directory_middleware import (
    discover as discover_middleware_files,
)
from nexy.modules.routers.hmr import setup_hmr
from nexy.modules.routers.middlewares import PathMiddleware, setup_middlewares
from nexy.modules.routers.router_resolver import resolve_router
from nexy.modules.routers.static_assets import setup_favicon, setup_static_files
from nexy.modules.runtime.importer import install_vfs_importer


def install_directory_middleware(server: FastAPI, routes: Routes = lambda: ()) -> None:
    """Mount the ``middleware.py`` files of ``src/routes`` (nothing is added without any)."""
    root = Path(Config.ROUTER_PATH)
    if root.is_dir():
        entries = discover_middleware_files(root)
        if entries:
            server.add_middleware(DirectoryMiddleware, entries=entries, routes=routes)


def _otel_sdk_installed() -> bool:
    return importlib.util.find_spec("opentelemetry.sdk") is not None


def _telemetry_options() -> dict[str, Any]:
    """FastAPI's native telemetry is a per-request cost with nothing to export to.

    It can only report to an OpenTelemetry SDK. Without the SDK installed (and no
    auto-configuration requested) the check always answers "disabled", so skip it.
    Older FastAPI versions have no such parameter.
    """
    if "telemetry" not in inspect.signature(FastAPI.__init__).parameters:
        return {}
    if _otel_sdk_installed():
        return {}
    if os.environ.get("FASTAPI_OTEL_AUTO_CONFIGURE", "").lower() in {"1", "true", "yes"}:
        return {}
    return {
        "telemetry": {"tracing": False, "metrics": False, "logs": False, "operation_spans": False}
    }


class AppServer:
    """Assembles the FastAPI application from config, routers, middleware and routes."""

    _docs_disabled_printed = False

    def __init__(self) -> None:
        # Also when the app is loaded without the CLI (`uvicorn nexy.app:app`).
        ensure_project_packages()
        install_vfs_importer()
        self.config = Config()
        self.version = __version__
        self.server: FastAPI | None = None
        self.fb_router: FBRouter | None = None

        self._docs_url, self._redocs_url = self._resolve_docs_settings()

    async def scalar_html(self) -> HTMLResponse:
        openapi_url: str | None = self.server.openapi_url if self.server else None
        return get_scalar_api_reference(
            scalar_favicon_url="/favicon.ico",
            openapi_url=openapi_url,
            title="Nexy - scalar API",
            telemetry=True,
            dark_mode=True,
            hide_models=True,
            scalar_proxy_url="https://proxy.scalar.com",
        )

    def _resolve_docs_settings(self) -> tuple[str | None, str | None]:
        """KISS: Logic extracted to a single specialized method."""
        conf = self.config
        if not conf.useDocs:
            if not AppServer._docs_disabled_printed:
                console.print("[yellow]API documentation is disabled[/yellow]")
                AppServer._docs_disabled_printed = True
            return None, None

        d_url = conf.useDocsUrl
        r_url = conf.useRedocsUrl
        return d_url, r_url

    def _file_routes(self) -> list[tuple[str, tuple[str, ...]]]:
        """``(url, source directory parts)`` of every file route, for ``middleware.py`` scoping."""
        if self.fb_router is None:
            return []
        depth = len(Path(Config.ROUTER_PATH).parts)
        return [
            (route.pathname, Path(route.source).parent.parts[depth:])
            for route in self.fb_router.scan.routes
        ]

    def _new_application(self) -> FastAPI:
        return FastAPI(
            title="Nexy",
            version=self.version,
            docs_url=None,
            redoc_url=None,
            **_telemetry_options(),
        )

    def _add_middlewares(self, server: FastAPI) -> None:
        """The middlewares, innermost first: each one added wraps the ones before it."""
        install_directory_middleware(server, routes=self._file_routes)
        server.add_middleware(PathMiddleware)
        if self.config.useBadge:
            server.add_middleware(BadgeMiddleware, version=self.version)
        setup_favicon(server, self.config.ROUTER_PATH)
        setup_static_files(server)
        setup_middlewares(server, self.config)
        # Added last, so outermost: it times everything below it.
        server.add_middleware(AccessLogMiddleware)
        if not is_dev():
            server.add_middleware(SecurityHeadersMiddleware)

    def _add_error_handlers(self, server: FastAPI) -> None:
        server.exception_handler(HTTPException)(handle_http_exception)
        server.add_exception_handler(Exception, handle_crash)
        register_validation_error_handler(server)

    def run(self) -> ASGIApp:
        """Main entry point to assemble the application."""
        self.server = server = self._new_application()
        self._add_middlewares(server)
        ACTION_ENGINE.discover()
        ACTION_ENGINE.generate_client()
        self.fb_router = resolve_router(server, self.config, self.scalar_html, self._docs_url)
        if is_dev():
            setup_hmr(server)
        self._add_error_handlers(server)
        # FastAPI's telemetry reports the matched route; the fast path skips that step, so it
        # is only used when no OpenTelemetry SDK can be listening.
        if not _otel_sdk_installed():
            install_fast_path(server.router)
        return self._with_vite_proxy(server)

    @staticmethod
    def _with_vite_proxy(server: FastAPI) -> ASGIApp:
        """Wrap the app so Vite's dev endpoints share the Nexy origin.

        In development Vite listens on an internal loopback port; forwarding its
        paths keeps the whole application on one public origin without exposing
        that port. Outside dev mode nothing is wrapped.
        """
        port = vite_proxy_port()
        if port is None:
            return server
        return ViteProxyMiddleware(server, port=port)


def create_app() -> ASGIApp:
    """Assemble a new application from the project in the working directory."""
    return AppServer().run()


def __getattr__(name: str) -> Any:
    """``_server``, the uvicorn target, is built on first use and kept: importing this module
    must not scan the project."""
    if name != "_server":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    application = create_app()
    globals()["_server"] = application
    return application
