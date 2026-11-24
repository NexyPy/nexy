import socket
import sys
import threading
import time
import webbrowser
from typing import Annotated

import typer

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.common.messages import error
from nexy.helpers.fs.packages import ensure_project_packages
from nexy.helpers.server.listening import Endpoint, print_listening, served_docs_path
from nexy.helpers.server.markers import has_build
from nexy.helpers.server.port_owner import OccupiedPort
from nexy.helpers.server.server import Server
from nexy.modules.cli.commands.guard import abort_on_invalid_config
from nexy.modules.cli.devtools.pycache import pycache
from nexy.modules.i18n import t


def _refuse_unbuilt_project() -> None:
    """Production serves what `nexy build` made: without it, pages would lose their layout."""
    if has_build():
        return
    text = t("start.no_build", "No production build: run `nexy build`, then `nexy start`.")
    error(text)
    sys.exit(1)


def _route_failures() -> list[str]:
    """Build the application, which loads the routes, and list the ones that failed."""
    from nexy.modules.routers import app  # noqa: F401  (importing builds it)
    from nexy.modules.routers.fbrouter import LOAD_FAILURES

    return list(LOAD_FAILURES)


def _refuse_broken_project(failures: list[str]) -> None:
    """A project with a route that cannot load must not go live."""
    if not failures:
        return
    text = t("start.broken", "{count} route file(s) failed to load: the server was not started.")
    error(text.format(count=len(failures)))
    sys.exit(1)


def _endpoint(port: int | None, host: str | None) -> Endpoint:
    """Where to listen: the arguments, else the configuration, on a free port."""
    config = Config()
    run_host = host or config.useHost
    run_port, _ = Server.resolve_ports(run_host, port or config.usePort, with_client=False)
    keyfile, certfile = Server.get_ssl_config(config)
    return Endpoint(run_host, run_port, keyfile, certfile)


def _open_once_listening(endpoint: Endpoint, url: str) -> None:
    """Open the browser once the server accepts connections."""
    while True:
        try:
            with socket.create_connection((endpoint.host, endpoint.port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.05)
    # False when no browser can be found: the address is already on screen.
    webbrowser.open(url)


def _serve(endpoint: Endpoint, occupied: OccupiedPort, open_browser: bool = False) -> None:
    """Serve until Ctrl+C; the production marker exists only while the server runs."""
    try:
        Server.check_nexy_prod(delete=False)
        if open_browser:
            threading.Thread(
                target=_open_once_listening,
                args=(endpoint, endpoint.url("localhost")),
                daemon=True,
            ).start()
        Server.uvicorn(
            host=endpoint.host,
            port=endpoint.port,
            ssl_keyfile=endpoint.ssl_keyfile,
            ssl_certfile=endpoint.ssl_certfile,
        )
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        Server.check_nexy_prod(delete=True)
        freed = occupied.free()
        if freed is not None:
            message = t("start.port_freed", "Freed port {port}: stopped process {pid}.")
            console.print(tagged("nexy", message.format(port=occupied.asked, pid=freed), "yellow"))
        console.print(tagged("nexy", t("start.exited", "exited"), "red"))


def start(
    port: int | None = None,
    host: str | None = None,
    open_browser: Annotated[
        bool,
        typer.Option(
            "--open",
            "-o",
            help=t("start.help_open", "Open the browser once the server answers"),
        ),
    ] = False,
) -> None:
    pycache()
    ensure_project_packages()
    abort_on_invalid_config()
    _refuse_unbuilt_project()
    started = time.perf_counter()
    _refuse_broken_project(_route_failures())
    endpoint = _endpoint(port, host)
    elapsed = time.perf_counter() - started
    config = Config()
    asked = port or config.usePort
    occupied = OccupiedPort(asked, endpoint.port)
    docs = served_docs_path(config.useDocs, config.useDocsUrl, dev=False)
    print_listening("start", __version__, endpoint, elapsed, Server.get_network_ip, docs)
    _serve(endpoint, occupied, open_browser)
