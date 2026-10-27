"""The one name the CLI uses to run and stop the servers of a project.

Each method hands over to the module that owns the work: ports, processes, uvicorn, Vite and
the small marker files. This class holds no logic of its own.
"""

from __future__ import annotations

import contextlib
import sys
from subprocess import Popen  # nosec B404 - type only, no invocation
from typing import Any

from nexy.core.config import Config
from nexy.helpers.common.vite_launch import vite_argv
from nexy.helpers.server import ports, processes, vite_process
from nexy.helpers.server.markers import set_production
from nexy.helpers.server.uvicorn_run import run_uvicorn

_WIN_ASYNCIO_PATCHED = False


def _patch_win_asyncio() -> None:
    """Suppress ConnectionResetError in asyncio proactor on Windows."""
    global _WIN_ASYNCIO_PATCHED
    if sys.platform != "win32" or _WIN_ASYNCIO_PATCHED:
        return
    try:
        import asyncio.proactor_events as _pe

        transport_cls: Any = _pe._ProactorBasePipeTransport
        orig = transport_cls._call_connection_lost

        def _safe_call_connection_lost(self: Any, exc: BaseException | None = None) -> None:
            with contextlib.suppress(ConnectionResetError):
                orig(self, exc)

        transport_cls._call_connection_lost = _safe_call_connection_lost
        _WIN_ASYNCIO_PATCHED = True
    except (AttributeError, ImportError):
        pass


_patch_win_asyncio()


class Server:
    """Facade over the server helpers; see the module docstring."""

    @staticmethod
    def check_nexy_prod(delete: bool = False) -> None:
        set_production(not delete)

    @staticmethod
    def resolve_ports(
        host: str | None = None, port: int | None = None, with_client: bool = True
    ) -> tuple[int, int]:
        """Server and client ports, found in cascade from the config or the arguments."""
        config = Config()
        return ports.resolve_ports(host or config.useHost, port or config.usePort, with_client)

    @staticmethod
    def get_network_ip() -> str:
        return ports.network_ip()

    @staticmethod
    def get_ssl_config(config: Config) -> tuple[str | None, str | None]:
        if config.useSslKeyfile and config.useSslCertfile:
            return config.useSslKeyfile, config.useSslCertfile
        return None, None

    @staticmethod
    def stop_process(proc: Popen[Any] | None, timeout: int = 5) -> None:
        processes.stop_process(proc, timeout)

    @staticmethod
    def uvicorn(
        host: str | None = None,
        port: int = 3000,
        ssl_keyfile: str | None = None,
        ssl_certfile: str | None = None,
        workers: int | None = None,
    ) -> bool | None:
        """Serve in the foreground: True when it stopped normally, None when it failed to start."""
        return run_uvicorn(host, port, ssl_keyfile, ssl_certfile, workers)

    @staticmethod
    def wait_for_vite_ready(
        port: int,
        host: str = "localhost",
        timeout: float = 30,
        process: Popen[Any] | None = None,
    ) -> bool:
        return vite_process.wait_for_vite_ready(port, host, timeout, process)

    @staticmethod
    def _vite_argv(build: bool, port: int, ssl: bool = False) -> list[str]:
        """The argv that starts the project's Vite.

        *ssl* is accepted for callers but unused: Uvicorn terminates TLS and the dev proxy
        reaches Vite over loopback HTTP, so Vite never runs in HTTPS mode.

        Raises:
            RuntimeError: Node.js or the project's Vite install is missing.
        """
        del ssl
        return vite_argv(build, port)

    @staticmethod
    def vite(
        port: int = 5173,
        build: bool = False,
        ssl: bool = False,
        suppress_output: bool | None = None,
        capture_stderr: bool = False,
    ) -> Popen[Any]:
        """Launch the project's local Vite client."""
        del ssl
        return vite_process.launch_vite(port, build, suppress_output, capture_stderr)
