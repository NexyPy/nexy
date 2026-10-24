import os
import subprocess  # nosec B404
import sys
import time
from pathlib import Path
from typing import Any

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common import launcher, package_manager
from nexy.helpers.common.console import console
from nexy.helpers.fs.vfs import VFS
from nexy.helpers.server.proxy import DEV_ENV_VAR
from nexy.helpers.server.server import Server
from nexy.modules.builder import Builder
from nexy.modules.cli.commands.guard import abort_on_invalid_config
from nexy.modules.cli.devtools.pycache import pycache
from nexy.modules.cli.devtools.watcher import create_observer, purge_project_modules, stop_observer
from nexy.modules.frontend import FrontendGenerator
from nexy.modules.i18n import t


def _require_vite_install() -> None:
    """Fail before compiling when the frontend dependencies are absent.

    `nexy dev` never installs: node_modules is the job of `nexy new` and
    `nexy init`. A clear command beats a 30-second wait followed by 502s.
    """
    if (Path("node_modules") / "vite" / "bin" / "vite.js").is_file():
        return

    manager = package_manager.detect() or "npm"
    console.print("\n[red]  \u2718[/red] Node.js dependencies are missing.")
    console.print(f"    Run: [cyan]{manager} install[/cyan]")
    console.print(
        "\n    [dim]nexy dev does not install dependencies; nexy init and nexy new do.[/dim]"
    )
    sys.exit(1)


def dev(port: int | None = None, host: str | None = None) -> None:
    pycache()
    abort_on_invalid_config()
    # Mark this process tree as the dev server so the application proxies Vite's
    # endpoints through its own origin instead of exposing Vite's port.
    os.environ[DEV_ENV_VAR] = "1"
    config = Config()
    if config.useVite:
        _require_vite_install()
    version = __version__
    run_host = host or config.useHost
    run_port = port or config.usePort
    run_port, client_port = Server.resolve_ports(run_host, run_port)
    Server.check_nexy_prod(delete=True)

    vite_proc: subprocess.Popen[Any] | None = None
    ssl_keyfile, ssl_certfile = Server.get_ssl_config(config)
    ssl_enabled = bool(ssl_keyfile and ssl_certfile)
    protocol = "https" if ssl_enabled else "http"

    startup_start = time.perf_counter()

    try:
        VFS.set_dev_mode(True)

        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=2) as pool:
            fe_future = pool.submit(FrontendGenerator().generate)
            build_future = pool.submit(Builder().build, showlog=False)

            fe_start = time.perf_counter()
            fe_future.result()
            fe_elapsed = time.perf_counter() - fe_start

            if config.useVite:
                vite_start = time.perf_counter()
                vite_proc = Server.vite(port=client_port, ssl=ssl_enabled)

            with console.status("\n[green]nsc[/green] » compile ...", spinner="dots"):
                build_start = time.perf_counter()
                result = build_future.result()
                build_elapsed = time.perf_counter() - build_start
                build_timer = f"{build_elapsed:.2f}s"
                launcher.success(f"{t('dev.compiling', 'compiled')} in {build_timer}")
                if result.failed:
                    for p in result.failed:
                        err = result.errors.get(p)
                        if err:
                            console.print(f"  [red]x {err.format()}[/red]")
                        else:
                            console.print(f"  [red]x {p}[/red]")

        if config.useVite:
            if result.failed:
                Server.stop_process(vite_proc)
                vite_proc = None
            else:
                with console.status("[dim]  starting dev server...[/dim]", spinner="dots"):
                    vite_ready = Server.wait_for_vite_ready(client_port, process=vite_proc)
                    vite_elapsed = time.perf_counter() - vite_start
                console.print(
                    f"  [dim]frontend[/dim] [dim]{fe_elapsed:.2f}s[/dim] ·"
                    f" [dim]vite[/dim] [dim]{vite_elapsed:.2f}s[/dim]\n"
                )
                if not vite_ready:
                    console.print("[red]  \u2718[/red] Vite failed to start.")
                    console.print("    [dim]Read the Vite output above for the cause.[/dim]")
                    Server.stop_process(vite_proc)
                    vite_proc = None
                    sys.exit(1)
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

        network_ip = Server.get_network_ip() if run_host == "0.0.0.0" else run_host  # nosec B104

        launcher.banner("dev", version)
        launcher.entry(t("dev.local", "Local:"), f"{protocol}://localhost:{run_port}")
        if network_ip != "127.0.0.1" and network_ip != "localhost":
            launcher.entry(t("dev.network", "Network:"), f"{protocol}://{network_ip}:{run_port}")
        launcher.entry(t("dev.ready", "Ready:"), startup_timer)
        console.print(f"  [dim]{t('dev.stop', 'press Ctrl+C to stop')}[/dim]")

        import uvicorn as _uvicorn

        from nexy.helpers.server.uvicorn_config import NEXY_LOG_CONFIG

        while True:
            _restart_requested = False
            for _name in list(sys.modules.keys()):
                if _name.startswith("__nexy__") or _name in (
                    "nexy.modules.routers.app",
                    "nexy.modules.routers.fbrouter",
                ):
                    del sys.modules[_name]
            # Project modules (src/routes/*.py, dependencies.py, ...) stay cached
            # across uvicorn restarts; drop them so the reload serves new code.
            purge_project_modules()
            _uvicorn_config = _uvicorn.Config(
                "nexy.modules.routers.app:_server",
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
        stop_observer(observer)
        Server.stop_process(vite_proc)
        console.print(f"[red]nexy \u00bb {t('dev.exited', 'exited')} [reset]")
