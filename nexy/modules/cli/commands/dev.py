import os
import subprocess  # nosec B404
import sys
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common import launcher, package_manager
from nexy.helpers.common.console import console
from nexy.helpers.common.vite_launch import vite_installed
from nexy.helpers.fs.vfs import VFS
from nexy.helpers.server.proxy import DEV_ENV_VAR
from nexy.helpers.server.server import Server
from nexy.modules.builder import Builder, BuildResult
from nexy.modules.cli.commands.guard import abort_on_invalid_config
from nexy.modules.cli.devtools.pycache import pycache
from nexy.modules.cli.devtools.watcher import create_observer, purge_project_modules, stop_observer
from nexy.modules.frontend import FrontendGenerator
from nexy.modules.i18n import t

_APP_MODULES = ("nexy.modules.routers.app", "nexy.modules.routers.fbrouter")


@dataclass(frozen=True)
class _Endpoint:
    """Where the application listens."""

    host: str
    port: int
    ssl_keyfile: str | None = None
    ssl_certfile: str | None = None

    @property
    def protocol(self) -> str:
        return "https" if self.ssl_keyfile and self.ssl_certfile else "http"


@dataclass
class _Session:
    """What `nx dev` starts and later has to stop."""

    vite: "subprocess.Popen[Any] | None" = None
    frontend_seconds: float = 0.0
    vite_started_at: float = field(default=0.0)


def _require_vite_install() -> None:
    """Fail before compiling when the frontend dependencies are absent.

    `nexy dev` never installs: node_modules is the job of `nexy new` and
    `nexy init`. A clear command beats a 30-second wait followed by 502s.
    """
    if vite_installed():
        return

    manager = package_manager.detect() or "npm"
    console.print("\n[red]  ✘[/red] Node.js dependencies are missing.")
    console.print(f"    Run: [cyan]{manager} install[/cyan]")
    console.print(
        "\n    [dim]nexy dev does not install dependencies; nexy init and nexy new do.[/dim]"
    )
    sys.exit(1)


def _report_failures(result: BuildResult) -> None:
    for path in result.failed:
        error = result.errors.get(path)
        console.print(f"  [red]x {error.format() if error else path}[/red]")


def _await_compile(build: "Future[BuildResult]") -> BuildResult:
    with console.status("\n[green]nsc[/green] » compile ...", spinner="dots"):
        started = time.perf_counter()
        result = build.result()
        launcher.success(
            f"{t('dev.compiling', 'compiled')} in {time.perf_counter() - started:.2f}s"
        )
        _report_failures(result)
    return result


def _generate_and_compile(
    config: Config, client_port: int, ssl: bool, session: _Session
) -> BuildResult:
    """Generate the client files and compile the routes in parallel; start Vite meanwhile."""
    with ThreadPoolExecutor(max_workers=2) as pool:
        frontend = pool.submit(FrontendGenerator().generate)
        build = pool.submit(Builder().build, showlog=False)

        started = time.perf_counter()
        frontend.result()
        session.frontend_seconds = time.perf_counter() - started

        if config.useVite:
            session.vite_started_at = time.perf_counter()
            session.vite = Server.vite(port=client_port, ssl=ssl)
        return _await_compile(build)


def _drop_vite(session: _Session) -> None:
    Server.stop_process(session.vite)
    session.vite = None


def _settle_vite(session: _Session, result: BuildResult, client_port: int) -> None:
    """Keep Vite only when the routes compiled and it answers; otherwise stop it."""
    if result.failed:
        _drop_vite(session)
        return
    with console.status("[dim]  starting dev server...[/dim]", spinner="dots"):
        ready = Server.wait_for_vite_ready(client_port, process=session.vite)
        vite_seconds = time.perf_counter() - session.vite_started_at
    console.print(
        f"  [dim]frontend[/dim] [dim]{session.frontend_seconds:.2f}s[/dim] ·"
        f" [dim]vite[/dim] [dim]{vite_seconds:.2f}s[/dim]\n"
    )
    if not ready:
        console.print("[red]  ✘[/red] Vite failed to start.")
        console.print("    [dim]Read the Vite output above for the cause.[/dim]")
        _drop_vite(session)
        sys.exit(1)


def _initialise(config: Config, client_port: int, ssl: bool) -> _Session:
    """Compile, start Vite and wait for it. Exit with code 1 when that is impossible."""
    session = _Session()
    try:
        VFS.set_dev_mode(True)
        result = _generate_and_compile(config, client_port, ssl, session)
        if config.useVite:
            _settle_vite(session, result, client_port)
    except Exception as error:
        console.print(f"\n[red]{t('dev.init_error', 'Error during initialization:')}[/red] {error}")
        Server.stop_process(session.vite)
        sys.exit(1)
    return session


def _purge_app_modules() -> None:
    """Forget the application and the project's modules so a restart serves new code."""
    for name in list(sys.modules):
        if name.startswith("__nexy__") or name in _APP_MODULES:
            del sys.modules[name]
    purge_project_modules()


class _Reloader:
    """Runs uvicorn and restarts it whenever the watcher asks."""

    def __init__(self) -> None:
        self.restart_requested = False
        self._server: Any = None

    def request_restart(self) -> None:
        self.restart_requested = True
        if self._server is not None:
            self._server.should_exit = True

    def serve(self, endpoint: _Endpoint) -> None:
        import uvicorn

        from nexy.helpers.server.uvicorn_config import NEXY_LOG_CONFIG

        while True:
            self.restart_requested = False
            _purge_app_modules()
            self._server = uvicorn.Server(
                uvicorn.Config(
                    "nexy.modules.routers.app:_server",
                    host=endpoint.host,
                    port=endpoint.port,
                    log_config=NEXY_LOG_CONFIG,
                    access_log=False,
                    log_level="info",
                    ssl_keyfile=endpoint.ssl_keyfile,
                    ssl_certfile=endpoint.ssl_certfile,
                )
            )
            self._server.run()
            self._server = None
            if not self.restart_requested:
                return


def _print_banner(endpoint: _Endpoint, startup_seconds: float) -> None:
    network_ip = Server.get_network_ip() if endpoint.host == "0.0.0.0" else endpoint.host  # nosec B104
    launcher.banner("dev", __version__)
    launcher.entry(t("dev.local", "Local:"), f"{endpoint.protocol}://localhost:{endpoint.port}")
    if network_ip not in ("127.0.0.1", "localhost"):
        launcher.entry(
            t("dev.network", "Network:"), f"{endpoint.protocol}://{network_ip}:{endpoint.port}"
        )
    launcher.entry(t("dev.ready", "Ready:"), f"{startup_seconds:.2f}s")
    console.print(f"  [dim]{t('dev.stop', 'press Ctrl+C to stop')}[/dim]")


def _serve(config: Config, endpoint: _Endpoint, session: _Session, started: float) -> None:
    """Watch the project and serve it until Ctrl+C; always release what was started."""
    reloader = _Reloader()
    observer = None
    try:
        observer = create_observer(
            path=".",
            patterns=config.WATCH_EXTENSIONS_GLOB,
            ignore_patterns=config.WATCH_EXCLUDE_PATTERNS,
            on_reload_api=reloader.request_restart,
        )
        _print_banner(endpoint, time.perf_counter() - started)
        reloader.serve(endpoint)
    except KeyboardInterrupt:
        console.print("\n  [dim]Stopping servers...[/dim]")
    except SystemExit:
        pass
    except Exception as error:
        console.print(f"\n  [red]Error: {error}[/red]")
    finally:
        console.print("  [dim]Cleaning up...[/dim]")
        stop_observer(observer)
        Server.stop_process(session.vite)
        console.print(f"[red]nexy » {t('dev.exited', 'exited')} [reset]")


def dev(port: int | None = None, host: str | None = None) -> None:
    pycache()
    abort_on_invalid_config()
    # Mark this process tree as the dev server so the application proxies Vite's
    # endpoints through its own origin instead of exposing Vite's port.
    os.environ[DEV_ENV_VAR] = "1"
    config = Config()
    if config.useVite:
        _require_vite_install()
    run_host = host or config.useHost
    run_port, client_port = Server.resolve_ports(run_host, port or config.usePort)
    Server.check_nexy_prod(delete=True)

    ssl_keyfile, ssl_certfile = Server.get_ssl_config(config)
    endpoint = _Endpoint(run_host, run_port, ssl_keyfile, ssl_certfile)
    started = time.perf_counter()
    session = _initialise(config, client_port, endpoint.protocol == "https")
    _serve(config, endpoint, session, started)
