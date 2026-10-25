import time

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common import launcher
from nexy.helpers.common.console import console
from nexy.helpers.fs.packages import ensure_project_packages
from nexy.helpers.server.server import Server
from nexy.modules.cli.commands.guard import abort_on_invalid_config
from nexy.modules.cli.devtools.pycache import pycache
from nexy.modules.i18n import t


def start(port: int | None = None, host: str | None = None) -> None:
    pycache()
    ensure_project_packages()
    abort_on_invalid_config()
    startup_start = time.perf_counter()
    version = __version__

    config = Config()
    run_host = host or config.useHost
    run_port, _ = Server.resolve_ports(run_host, port or config.usePort, with_client=False)
    ssl_keyfile, ssl_certfile = Server.get_ssl_config(config)
    ssl_enabled = bool(ssl_keyfile and ssl_certfile)
    protocol = "https" if ssl_enabled else "http"

    startup_elapsed = time.perf_counter() - startup_start
    startup_timer = f"{startup_elapsed:.2f}s"

    network_ip = Server.get_network_ip() if run_host == "0.0.0.0" else run_host  # nosec B104

    try:
        launcher.banner("start", version)

        launcher.entry(t("start.local", "Local:"), f"{protocol}://localhost:{run_port}")
        if network_ip != "127.0.0.1" and network_ip != "localhost":
            launcher.entry(t("start.network", "Network:"), f"{protocol}://{network_ip}:{run_port}")
        launcher.entry(t("start.ready", "Ready:"), startup_timer)
        console.print(f"  [dim]{t('start.stop', 'Press Ctrl+C to stop')}[/dim]\n")

        Server.check_nexy_prod(delete=False)

        Server.uvicorn(
            host=run_host,
            port=run_port,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            as_process=False,
        )

    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        Server.check_nexy_prod(delete=True)
        console.print(f"[red]nexy \u00bb {t('start.exited', 'exited')} [reset]")
