"""`nx routes`: list every route and its source file."""

from typing import Any

from rich.table import Table

from nexy.helpers.common.console import console
from nexy.helpers.server.devtools.state import routes_of
from nexy.modules.i18n import t

_FRAMEWORK_PATHS = {
    "/favicon.ico",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/docs/oauth2-redirect",
}


def _get_routes() -> list[dict[str, Any]]:
    """Get and sort application routes."""
    from nexy.modules.routers.app import AppServer

    application = AppServer()
    application.run()

    if application.server is None:
        return []

    return sorted(
        (
            route
            for route in routes_of(application.server)
            if route["path"] not in _FRAMEWORK_PATHS and not route["path"].startswith("/_nx_")
        ),
        key=lambda route: route["path"],
    )


def _build_table(found: list[dict[str, Any]]) -> Table:
    """Build a table containing the discovered routes."""
    table = Table(title=t("routes.title", "Routes"))
    table.add_column(t("routes.methods", "Methods"))
    table.add_column(t("routes.path", "Path"))
    table.add_column(t("routes.source", "Source file"))

    for route in found:
        methods = ", ".join(route["methods"])
        source = route.get("source") or t("routes.unknown", "Unknown")
        table.add_row(methods, route["path"], source)

    return table


def routes() -> None:
    """Print every application route and the file that answers it."""
    found = _get_routes()

    if not found:
        console.print(t("routes.empty", "No routes found."))
        return

    console.print(_build_table(found))
