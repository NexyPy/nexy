import os
import signal
import subprocess  # nosec B404
import sys
import threading
import time
import webbrowser
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Annotated, Any

import typer
from rich.markup import escape

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common import package_manager
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.common.messages import error, hint, warning
from nexy.helpers.common.pycheck import describe, report
from nexy.helpers.common.tasks import waiting
from nexy.helpers.common.vite_launch import vite_installed
from nexy.helpers.fs.packages import ensure_project_packages
from nexy.helpers.fs.vfs import VFS
from nexy.helpers.server.dev_mode import DEV_ENV_VAR
from nexy.helpers.server.listening import Endpoint, print_listening, served_docs_path
from nexy.helpers.server.port_owner import OccupiedPort
from nexy.helpers.server.server import Server
from nexy.modules.builder import Builder, BuildResult
from nexy.modules.cli.commands.guard import abort_on_invalid_config
from nexy.modules.cli.devtools.pycache import pycache
from nexy.modules.cli.devtools.watch import create_observer, purge_project_modules, stop_observer
from nexy.modules.frontend import FrontendGenerator
from nexy.modules.i18n import t
from nexy.modules.routers.actions.engine import ACTION_ENGINE

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
    error(t("dev.deps_missing", "Node.js dependencies are missing."))
    hint(t("dev.deps_run", "Run: {command}").format(command=f"[cyan]{manager} install[/cyan]"))
    hint(t("dev.deps_hint", "nexy dev does not install dependencies; nexy init and nexy new do."))
    sys.exit(1)


def _report_failures(result: BuildResult) -> None:
    for path in result.failed:
        problem = result.errors.get(path)
        error(escape(problem.format() if problem else str(path)))


def _await_compile(build: "Future[BuildResult]") -> BuildResult:
    with waiting(t("dev.compiling_status", "Compiling...")):
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
        # Before Vite: a page that imports `@nexy/actions` must find it on its first transform.
        ACTION_ENGINE.refresh_client()

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
    with waiting(t("dev.starting_vite", "Starting the dev server...")):
        ready = Server.wait_for_vite_ready(client_port, process=session.vite)
    if not ready:
        error(t("dev.vite_failed", "Vite failed to start."))
        hint(t("dev.vite_failed_hint", "Read the Vite output above for the cause."))
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
    except Exception as problem:
        cause = escape(str(problem) or type(problem).__name__)
        error(t("dev.init_error", "Could not start the dev server"), cause=cause)
        Server.stop_process(session.vite)
        sys.exit(1)
    return session


def _purge_app_modules() -> None:
    """Forget the application, the configuration and the project's modules so a restart
    serves new code, including an edited nexyconfig.py."""
    for name in list(sys.modules):
        if name.startswith("__nexy__") or name in _APP_MODULES:
            del sys.modules[name]
    purge_project_modules()
    Config.reset()


def _regenerate_client_files() -> None:
    """Rebuild the client route list after a page appeared, disappeared or moved."""
    try:
        FrontendGenerator().generate()
    except Exception as problem:
        reason = t("dev.routes_failed", "Could not update the client routes: {error}")
        warning(reason.format(error=escape(str(problem))))


def _import_app() -> None:
    """Import the application the way uvicorn will, so a broken file is reported, not fatal."""
    from uvicorn.importer import import_from_string

    import_from_string(_APP)


class _BrowserOpener:
    """`nx dev --open`: opens the local address once, when a server first answers."""

    def __init__(self, url: str | None) -> None:
        self._url = url  # None once opened
        self._lock = threading.Lock()

    def watch(self, server: Any, is_running: Callable[[], bool]) -> None:
        """Wait for *server* to listen in the background, then open the address if still due."""
        if self._url:
            threading.Thread(
                target=self.open_once_started, args=(server, is_running), daemon=True
            ).start()

    def open_once_started(self, server: Any, is_running: Callable[[], bool]) -> None:
        """A run that ends before it listens leaves the address for the next run."""
        while not server.started:
            if not is_running():
                return
            time.sleep(0.05)
        with self._lock:
            url, self._url = self._url, None
        if url:
            # False when no browser can be found (over SSH): the address is already on screen.
            webbrowser.open(url)


class _Reloader:
    """Runs uvicorn and restarts it whenever the watcher asks."""

    def __init__(self, open_url: str | None = None) -> None:
        self.restart_requested = False
        self.regenerate_requested = False
        self._started = False
        self._server: Any = None
        self._changed = threading.Event()
        self._announced = False
        self._opener = _BrowserOpener(open_url)

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
        """Serve until Ctrl+C; a server that cannot run waits for the next change."""
        while True:
            if not self._start(endpoint):
                self._wait_for_change()
            elif not self.restart_requested:
                return

    def _start(self, endpoint: Endpoint) -> bool:
        """True once the server has run; False when it could not start, whatever the reason."""
        try:
            self._prepare()
            if not self._load():
                return False
            self._run(endpoint)
        except SystemExit as stop:
            return stop.code in (0, None) or self._failed(f"exit code {stop.code}")
        except Exception as error:
            return self._failed(str(error) or type(error).__name__)
        return True

    @staticmethod
    def _failed(reason: str) -> bool:
        message = t("dev.server_failed", "The server stopped ({reason}): waiting for a fix.")
        error(message.format(reason=escape(reason)))
        return False

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

        self._server = server = uvicorn.Server(
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
        self._opener.watch(server, lambda: self._server is server)
        server.run()
        self._server = None


def _watch(config: Config, reloader: _Reloader) -> Any:
    return create_observer(
        path=".",
        patterns=config.WATCH_EXTENSIONS_GLOB,
        ignore_patterns=config.WATCH_EXCLUDE_PATTERNS,
        on_reload_api=reloader.request_restart,
        on_routes_changed=reloader.request_routes_restart,
    )


def _release(observer: Any, session: _Session, occupied: OccupiedPort) -> None:
    """Stop what `nx dev` started: the watcher, Vite and the port another process held."""
    console.print(f"  [dim]{t('dev.cleaning', 'Cleaning up...')}[/dim]")
    stop_observer(observer)
    Server.stop_process(session.vite)
    freed = occupied.free()
    if freed is not None:
        message = t("dev.port_freed", "Freed port {port}: stopped process {pid}.")
        console.print(tagged("nexy", message.format(port=occupied.asked, pid=freed), "yellow"))
    console.print(tagged("nexy", t("dev.exited", "exited"), "red"))


def _serve(
    config: Config,
    endpoint: Endpoint,
    session: _Session,
    started: float,
    occupied: OccupiedPort,
    open_browser: bool = False,
) -> None:
    """Watch the project and serve it until Ctrl+C; always release what was started."""
    reloader = _Reloader(endpoint.url("localhost") if open_browser else None)
    observer = None
    try:
        observer = _watch(config, reloader)
        elapsed = time.perf_counter() - started
        docs = served_docs_path(config.useDocs, config.useDocsUrl, dev=True)
        print_listening("dev", __version__, endpoint, elapsed, Server.get_network_ip, docs)
        reloader.serve(endpoint)
    except KeyboardInterrupt:
        console.print(f"\n  [dim]{t('dev.stopping', 'Stopping servers...')}[/dim]")
    except SystemExit:
        pass
    except Exception as problem:
        error(escape(str(problem) or type(problem).__name__))
    finally:
        _release(observer, session, occupied)


def _interrupt(_signum: int, _frame: Any) -> None:
    """A SIGTERM stops `nx dev` the way Ctrl+C does, so Vite is stopped with it."""
    raise KeyboardInterrupt


def _announce_port(asked: int, used: int) -> None:
    if used != asked:
        message = t("dev.port_in_use", "Port {asked} is in use, using {port} instead.")
        warning(message.format(asked=asked, port=used))


def dev(
    port: int | None = None,
    host: str | None = None,
    open_browser: Annotated[
        bool,
        typer.Option(
            "--open",
            "-o",
            help=t("dev.help_open", "Open the browser once the server answers"),
        ),
    ] = False,
) -> None:
    # uvicorn raises a SIGTERM again once it has stopped: without this, the process would end
    # there, before the clean-up that stops Vite.
    previous = signal.signal(signal.SIGTERM, _interrupt)
    try:
        _dev(port, host, open_browser)
    finally:
        signal.signal(signal.SIGTERM, previous)


def _prepare_endpoint(
    config: Config, host: str | None, port: int | None
) -> tuple[Endpoint, int, OccupiedPort]:
    """Where dev listens, and the occupied port to free when it stops."""
    run_host = host or config.useHost
    asked = port or config.usePort
    run_port, client_port = Server.resolve_ports(run_host, asked)
    _announce_port(asked, run_port)
    ssl_keyfile, ssl_certfile = Server.get_ssl_config(config)
    endpoint = Endpoint(run_host, run_port, ssl_keyfile, ssl_certfile)
    return endpoint, client_port, OccupiedPort(asked, run_port)


def _dev(port: int | None, host: str | None, open_browser: bool) -> None:
    pycache()
    ensure_project_packages()
    abort_on_invalid_config()
    # Mark this process tree as the dev server so the application proxies Vite's
    # endpoints through its own origin instead of exposing Vite's port.
    os.environ[DEV_ENV_VAR] = "1"
    config = Config()
    if config.useVite:
        _require_vite_install()
    endpoint, client_port, occupied = _prepare_endpoint(config, host, port)
    Server.check_nexy_prod(delete=True)

    started = time.perf_counter()
    session = _initialise(config, client_port, endpoint.protocol == "https")
    _serve(config, endpoint, session, started, occupied, open_browser)
