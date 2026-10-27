import sys
import time

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.fs.packages import ensure_project_packages
from nexy.helpers.server.listening import Endpoint, print_listening
from nexy.helpers.server.server import Server
from nexy.modules.cli.commands.guard import abort_on_invalid_config
from nexy.modules.cli.devtools.pycache import pycache
from nexy.modules.i18n import t


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
    console.print(f"\n  [red]x[/red] {text.format(count=len(failures))}")
    sys.exit(1)


def _endpoint(port: int | None, host: str | None) -> Endpoint:
    """Where to listen: the arguments, else the configuration, on a free port."""
    config = Config()
    run_host = host or config.useHost
    run_port, _ = Server.resolve_ports(run_host, port or config.usePort, with_client=False)
    keyfile, certfile = Server.get_ssl_config(config)
    return Endpoint(run_host, run_port, keyfile, certfile)


def _serve(endpoint: Endpoint) -> None:
    """Serve until Ctrl+C; the production marker exists only while the server runs."""
    try:
        Server.check_nexy_prod(delete=False)
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
        console.print(tagged("nexy", t("start.exited", "exited"), "red"))


def start(port: int | None = None, host: str | None = None) -> None:
    pycache()
    ensure_project_packages()
    abort_on_invalid_config()
    started = time.perf_counter()
    _refuse_broken_project(_route_failures())
    endpoint = _endpoint(port, host)
    elapsed = time.perf_counter() - started
    print_listening("start", __version__, endpoint, elapsed, Server.get_network_ip)
    _serve(endpoint)
