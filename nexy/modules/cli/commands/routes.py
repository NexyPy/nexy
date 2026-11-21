"""`nx routes`: list every route and its source file."""

from rich.table import Table

from nexy.helpers.common.console import console
from nexy.helpers.server.devtools.state import routes_of
from nexy.modules.i18n import t


def routes() -> None:
    """Print every application route and the file that answers it."""
    from nexy.modules.routers.app import AppServer

    application = AppServer()
    application.run()

    if application.server is None:
        return

    found = sorted(
        (
            route
            for route in routes_of(application.server)
            if route["path"] != "/favicon.ico"
        ),
        key=lambda route: route["path"],
    )

    if not found:
        console.print(t("routes.empty", "No routes found."))
        return

    table = Table(title=t("routes.title", "Routes"))
    table.add_column(t("routes.methods", "Methods"))
    table.add_column(t("routes.path", "Path"))
    table.add_column(t("routes.source", "Source file"))

    for route in found:
        methods = ", ".join(route["methods"])
        source = route.get("source") or t("routes.unknown", "Unknown")
        table.add_row(methods, route["path"], source)

    console.print(table)