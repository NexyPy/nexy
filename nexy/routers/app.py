import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference
from starlette.exceptions import HTTPException

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.i18n import L as LocaleManager
from nexy.i18n.middleware import LocaleMiddleware
from nexy.routers.actions.engine import ACTION_ENGINE
from nexy.routers.error_handlers import handle_http_exception, register_validation_error_handler
from nexy.routers.fbrouter import FBRouter
from nexy.routers.hmr import setup_hmr
from nexy.routers.middlewares import PathMiddleware, setup_middlewares
from nexy.routers.router_resolver import resolve_router
from nexy.routers.static_assets import setup_favicon, setup_static_files
from nexy.runtime.importer import install_vfs_importer
from nexy.utils.common.console import console


class AppServer:
    """Assembles the FastAPI application from config, routers, middleware and routes."""

    _docs_disabled_printed = False

    def __init__(self) -> None:
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

    def run(self) -> FastAPI:
        """Main entry point to assemble the application."""
        self.server = FastAPI(title="Nexy", version=self.version, docs_url=None, redoc_url=None)
        server = self.server

        LocaleManager.configure(
            available=self.config.useLocales or ["en"],
            default=self.config.useDefaultLocale or "en",
            project_locales_dir=str(Path(os.getcwd()) / (self.config.useLocalesDir or "locales")),
        )
        loc_count = len(self.config.useLocales or ["en"])
        console.print(
            f"[dim][nexy][/dim] Translations preloaded for [bold]{loc_count}[/bold] locales"
        )
        server.add_middleware(LocaleMiddleware)
        server.add_middleware(PathMiddleware)
        setup_favicon(server, self.config.ROUTER_PATH)
        setup_static_files(server)
        setup_middlewares(server, self.config)
        ACTION_ENGINE.discover()
        self.fb_router = resolve_router(server, self.config, self.scalar_html, self._docs_url)
        setup_hmr(server)
        server.exception_handler(HTTPException)(handle_http_exception)
        register_validation_error_handler(server)
        return server


_server = AppServer().run()
