import time

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.i18n import t
from nexy.utils.common.console import console
from nexy.utils.dev.pycache import pycache
from nexy.utils.server.server import Server


def start(port: int | None = None, host: str | None = None) -> None:
    # pycache()
    startup_start = time.perf_counter()
    version = __version__

    config = Config()
    run_host = host or config.useHost
    run_port, _ = Server.resolve_ports(run_host, port or config.usePort)
    ssl_keyfile, ssl_certfile = Server.get_ssl_config(config)
    ssl_enabled = bool(ssl_keyfile and ssl_certfile)
    protocol = "https" if ssl_enabled else "http"

    startup_elapsed = time.perf_counter() - startup_start
    startup_timer = f"{startup_elapsed:.2f}s"

    network_ip = Server.get_network_ip() if run_host == "0.0.0.0" else run_host

    try:
        console.print(
            t("start.banner", "nexy@{version} starting in production...").format(version=version)
        )

        console.print(
            f"  [dim]\u00bb\u00bb[/dim] [green]{t('start.uvicorn', 'Uvicorn')}[/green]"
            f" {t('start.uvicorn_on', 'running on port')} [yellow]{run_port}[/yellow]"
        )
        console.print(
            f"  [dim]\u00bb\u00bb[/dim] {t('start.local', 'Local:')} [green]{protocol}://localhost:{run_port}[/green]"
        )
        if network_ip != "127.0.0.1" and network_ip != "localhost":
            console.print(
                f"  [dim]\u00bb\u00bb[/dim] {t('start.network', 'Network:')} [green]{protocol}://{network_ip}:{run_port}[/green]"
            )

        console.print(
            f"  [dim]\u00bb\u00bb[/dim] {t('start.ready', 'ready in')} [green]{startup_timer}[/green]"
        )
        console.print(f"  [dim]\u00bb\u00bb[/dim] {t('start.stop', 'Press Ctrl+C to stop')}\n")

        Server.check_nexy_prod(delete=False)

        Server.uvicorn(
            host=run_host,
            port=run_port,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
        )

    except (KeyboardInterrupt, SystemExit):
        console.print(f"[red]nexy \u00bb {t('start.exited', 'exited')} [reset]")
    finally:
        Server.check_nexy_prod(delete=True)
        console.print(f"[red]nexy \u00bb {t('start.exited', 'exited')} [reset]")
