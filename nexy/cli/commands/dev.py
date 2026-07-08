import subprocess
import sys
import time

from nexy.__version__ import __version__
from nexy.builder import Builder
from nexy.core.config import Config
from nexy.frontend import FrontendGenerator
from nexy.i18n import t
from nexy.utils.common.console import console
from nexy.utils.dev.pycache import pycache
from nexy.utils.dev.watcher import create_observer
from nexy.utils.fs.vfs import VFS
from nexy.utils.server.server import Server


def _stop_observer(observer) -> None:
    """Arrête proprement le watcher watchdog."""
    if not observer:
        return
    try:
        observer.stop()
        observer.join(timeout=2)
    except Exception as e:
        console.print(f"  [dim]Warning: Could not stop watcher cleanly: {e}[/dim]")


def dev(port: int | None = None, host: str | None = None) -> None:
    pycache()
    config = Config()
    version = __version__
    run_host = host or config.useHost
    if port:
        run_port = port
    else:
        run_port = port or config.usePort
    run_port, client_port = Server.resolve_ports(run_host, run_port)
    Server.check_nexy_prod(delete=True)

    vite_proc: subprocess.Popen | None = None
    ssl_keyfile, ssl_certfile = Server.get_ssl_config(config)
    ssl_enabled = bool(ssl_keyfile and ssl_certfile)
    protocol = "https" if ssl_enabled else "http"

    startup_start = time.perf_counter()

    try:
        with console.status("\n[green]nsc[/green] » compile ...", spinner="dots"):
            build_start = time.perf_counter()
            VFS.set_dev_mode(True)
            result = Builder().build(showlog=False)
            build_elapsed = time.perf_counter() - build_start
            build_timer = f"{build_elapsed:.2f}s"
            console.print(
                f"\n[green]nsc[/green] » [green]{t('dev.compiling', 'compiling')}[/green]"
                f" in [reset][dim]{build_timer}[/dim]"
            )
            if result.failed:
                for p in result.failed:
                    console.print(f"  [red]x {p}[/red]")

        if not result.failed:
            FrontendGenerator().generate()

            if config.useVite:
                vite_proc = Server.vite(port=client_port, ssl=ssl_enabled)
                with console.status("[dim]  starting dev server...[/dim]", spinner="dots"):
                    if not Server.wait_for_vite_ready(client_port, ssl=ssl_enabled):
                        console.print("[yellow]  warning: Vite took too long to start[/yellow]")
    except Exception as e:
        console.print(f"\n[red]{t('dev.init_error', 'Error during initialization:')}[/red] {e}")
        Server.stop_process(vite_proc)
        sys.exit(1)

    _restart_requested = False
    _server_instance = None
    observer = None

    def _reload_uvicorn() -> None:
        nonlocal _restart_requested, _server_instance
        _restart_requested = True
        if _server_instance is not None:
            _server_instance.should_exit = True

    try:
        observer = create_observer(
            path=".",
            patterns=config.WATCH_EXTENSIONS_GLOB,
            ignore_patterns=config.WATCH_EXCLUDE_PATTERNS,
            on_reload_api=_reload_uvicorn,
        )

        startup_elapsed = time.perf_counter() - startup_start
        startup_timer = f"{startup_elapsed:.2f}s"

        network_ip = Server.get_network_ip() if run_host == "0.0.0.0" else run_host

        console.print(t("dev.banner", "nexy@{version} dev using :").format(version=version))
        console.print(
            f"  [dim]\u00bb\u00bb[/dim] [green]Uvicorn[/green]  {'and [green]Vite[/green]' if vite_proc else ''}"
        )
        console.print(
            f"  [dim]\u00bb\u00bb[/dim] {t('dev.local', 'Local:')} [green]{protocol}://localhost:{run_port}[/green]"
        )
        if network_ip != "127.0.0.1" and network_ip != "localhost":
            console.print(
                f"  [dim]\u00bb\u00bb[/dim] {t('dev.network', 'Network:')} [green]{protocol}://{network_ip}:{run_port}[/green]"
            )
        console.print(
            f"  [dim]\u00bb\u00bb[/dim] {t('dev.ready', 'ready in')} [green]{startup_timer}[/green]"
        )
        console.print(f"  [dim]\u00bb\u00bb[/dim] {t('dev.stop', 'press Ctrl+C to stop')}")

        import uvicorn as _uvicorn

        from nexy.utils.server.uvicorn_config import NEXY_LOG_CONFIG

        while True:
            _restart_requested = False
            for _name in list(sys.modules.keys()):
                if _name.startswith("__nexy__") or _name in (
                    "nexy.routers.app",
                    "nexy.routers.fbrouter",
                ):
                    del sys.modules[_name]
            _uvicorn_config = _uvicorn.Config(
                "nexy.routers.app:_server",
                host=run_host,
                port=run_port,
                log_config=NEXY_LOG_CONFIG,
                log_level="info",
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile,
            )
            _server_instance = _uvicorn.Server(_uvicorn_config)
            _server_instance.run()
            _server_instance = None
            if not _restart_requested:
                break

    except KeyboardInterrupt:
        console.print("\n  [dim]Stopping servers...[/dim]")
    except SystemExit:
        pass
    except Exception as e:
        console.print(f"\n  [red]Error: {e}[/red]")
    finally:
        console.print("  [dim]Cleaning up...[/dim]")
        _server_instance = None
        _stop_observer(observer)
        Server.stop_process(vite_proc)
        console.print(f"[red]nexy \u00bb {t('dev.exited', 'exited')} [reset]")
