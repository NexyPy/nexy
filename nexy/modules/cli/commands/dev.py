import os
import subprocess  # nosec B404
import sys
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common import package_manager
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.common.pycheck import describe, report
from nexy.helpers.common.vite_launch import vite_installed
from nexy.helpers.fs.packages import ensure_project_packages
from nexy.helpers.fs.vfs import VFS
from nexy.helpers.server.listening import Endpoint, print_listening
from nexy.helpers.server.proxy import DEV_ENV_VAR
from nexy.helpers.server.server import Server
from nexy.modules.builder import Builder, BuildResult
from nexy.modules.cli.commands.guard import abort_on_invalid_config
from nexy.modules.cli.devtools.pycache import pycache
from nexy.modules.cli.devtools.watch import create_observer, purge_project_modules, stop_observer
from nexy.modules.frontend import FrontendGenerator
from nexy.modules.i18n import t

_APP_MODULES = ("nexy.modules.routers.app", "nexy.modules.routers.fbrouter")
_APP = "nexy.modules.routers.app:_server"


@dataclass
class _Session:
    """What `nx dev` starts and later has to stop."""

    vite: "subprocess.Popen[Any] | None" = None


def _require_vite_install() -> None:
    """Fail before compiling when the frontend dependencies are absent.

    `nexy dev` never installs: node_modules is the job of `nexy new` and
    `nexy init`. A clear command beats a 30-second wait followed by 502s.
    """
    if vite_installed():
        return

    manager = package_manager.detect() or "npm"
    console.print(f"\n[red]  ✘[/red] {t('dev.deps_missing', 'Node.js dependencies are missing.')}")
    command = f"[cyan]{manager} install[/cyan]"
    console.print("    " + t("dev.deps_run", "Run: {command}").format(command=command))
    hint = t("dev.deps_hint", "nexy dev does not install dependencies; nexy init and nexy new do.")
    console.print(f"\n    [dim]{hint}[/dim]")
    sys.exit(1)


def _report_failures(result: BuildResult) -> None:
    for path in result.failed:
        error = result.errors.get(path)
        console.print(f"  [red]x {error.format() if error else path}[/red]")


def _await_compile(build: "Future[BuildResult]") -> BuildResult:
    label = t("dev.compiling_status", "Compiling...")
    with console.status(f"\n[dim]{label}[/dim]", spinner="dots"):
        result = build.result()
        _report_failures(result)
    return result


def _generate_and_compile(
    config: Config, client_port: int, ssl: bool, session: _Session
) -> BuildResult:
    """Generate the client files and compile the routes in parallel; start Vite meanwhile."""
    with ThreadPoolExecutor(max_workers=2) as pool:
        frontend = pool.submit(FrontendGenerator().generate)
        build = pool.submit(Builder().build, showlog=False)

        frontend.result()

        if config.useVite:
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
    label = t("dev.starting_vite", "Starting the dev server...")
    with console.status(f"[dim]  {label}[/dim]", spinner="dots"):
        ready = Server.wait_for_vite_ready(client_port, process=session.vite)
    if not ready:
        console.print(f"[red]  ✘[/red] {t('dev.vite_failed', 'Vite failed to start.')}")
        cause = t("dev.vite_failed_hint", "Read the Vite output above for the cause.")
        console.print(f"    [dim]{cause}[/dim]")
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


def _regenerate_client_files() -> None:
    """Rebuild the client route list after a page appeared, disappeared or moved."""
    try:
        FrontendGenerator().generate()
    except Exception as error:
        reason = t("dev.routes_failed", "Could not update the client routes: {error}")
        console.print(f"  [red]x[/red] {reason.format(error=error)}")


def _import_app() -> None:
    """Import the application the way uvicorn will, so a broken file is reported, not fatal."""
    from uvicorn.importer import import_from_string

    import_from_string(_APP)


class _Reloader:
    """Runs uvicorn and restarts it whenever the watcher asks."""

    def __init__(self) -> None:
        self.restart_requested = False
        self.regenerate_requested = False
        self._started = False
        self._server: Any = None
        self._changed = threading.Event()
        self._announced = False

    def request_restart(self) -> None:
        """A Python file changed: the watcher already named it."""
        self._announced = True
        self.restart_requested = True
        self._changed.set()
        if self._server is not None:
            self._server.should_exit = True

    def request_routes_restart(self, _path: str) -> None:
        """The set of pages changed: the route table and the client route list are stale."""
        self.regenerate_requested = True
        self.request_restart()
        self._announced = False

    def serve(self, endpoint: Endpoint) -> None:
        """Serve until Ctrl+C; an application that cannot load waits for the next change."""
        while True:
            self._prepare()
            if self._load():
                self._run(endpoint)
                if not self.restart_requested:
                    return
            else:
                self._wait_for_change()

    def _prepare(self) -> None:
        if self._started and not self._announced:
            console.print(tagged("nexy", t("dev.updating", "update server")))
        self._started = True
        self._announced = False
        self.restart_requested = False
        self._changed.clear()
        if self.regenerate_requested:
            self.regenerate_requested = False
            _regenerate_client_files()
        ensure_project_packages()
        _purge_app_modules()

    @staticmethod
    def _load() -> bool:
        try:
            _import_app()
        except Exception as error:
            waiting = t("dev.error_waiting", "The application cannot start: waiting for a fix.")
            report(describe(error), waiting)
            return False
        return True

    def _wait_for_change(self) -> None:
        while not self._changed.wait(0.2):
            pass

    def _run(self, endpoint: Endpoint) -> None:
        import uvicorn

        from nexy.helpers.server.uvicorn_config import DEV_SERVE_LIMITS, NEXY_LOG_CONFIG

        self._server = uvicorn.Server(
            uvicorn.Config(
                _APP,
                host=endpoint.host,
                port=endpoint.port,
                log_config=NEXY_LOG_CONFIG,
                access_log=False,
                log_level="info",
                **DEV_SERVE_LIMITS,
                ssl_keyfile=endpoint.ssl_keyfile,
                ssl_certfile=endpoint.ssl_certfile,
            )
        )
        self._server.run()
        self._server = None


def _serve(config: Config, endpoint: Endpoint, session: _Session, started: float) -> None:
    """Watch the project and serve it until Ctrl+C; always release what was started."""
    reloader = _Reloader()
    observer = None
    try:
        observer = create_observer(
            path=".",
            patterns=config.WATCH_EXTENSIONS_GLOB,
            ignore_patterns=config.WATCH_EXCLUDE_PATTERNS,
            on_reload_api=reloader.request_restart,
            on_routes_changed=reloader.request_routes_restart,
        )
        print_listening(
            "dev", __version__, endpoint, time.perf_counter() - started, Server.get_network_ip
        )
        reloader.serve(endpoint)
    except KeyboardInterrupt:
        console.print(f"\n  [dim]{t('dev.stopping', 'Stopping servers...')}[/dim]")
    except SystemExit:
        pass
    except Exception as error:
        console.print(f"\n  [red]{t('dev.error', 'Error: {error}').format(error=error)}[/red]")
    finally:
        console.print(f"  [dim]{t('dev.cleaning', 'Cleaning up...')}[/dim]")
        stop_observer(observer)
        Server.stop_process(session.vite)
        console.print(tagged("nexy", t("dev.exited", "exited"), "red"))


def dev(port: int | None = None, host: str | None = None) -> None:
    pycache()
    ensure_project_packages()
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
    endpoint = Endpoint(run_host, run_port, ssl_keyfile, ssl_certfile)
    started = time.perf_counter()
    session = _initialise(config, client_port, endpoint.protocol == "https")
    _serve(config, endpoint, session, started)
