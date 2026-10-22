import contextlib
import os
import shutil
import socket
import subprocess  # nosec B404
import sys
import time
import traceback
from pathlib import Path
from subprocess import Popen  # nosec B404 - type only, no invocation
from typing import Any

import uvicorn as _uvicorn

from nexy.core.config import Config
from nexy.helpers.common.console import console as print_console
from nexy.helpers.fs.vfs import VFS
from nexy.helpers.server.ports import find_available_port
from nexy.helpers.server.uvicorn_config import NEXY_LOG_CONFIG

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

_NEXY_DIR = Path("__nexy__")


def _write_port_file(name: str, port: int) -> None:
    """Saves the port used for inter-process communication."""
    vfs = VFS()
    vfs.write(f"__nexy__/{name}.port", str(port))


def _detect_pm() -> tuple[str, bool]:
    """Detects the package manager (pnpm, bun, yarn, npm)."""
    for candidate in ("pnpm", "bun", "yarn", "npm"):
        binary = shutil.which(candidate) or shutil.which(candidate + ".cmd")
        if binary:
            return binary, candidate == "npm"
    return "npm", True


class Server:
    @staticmethod
    def check_nexy_prod(delete: bool = False) -> None:
        path = _NEXY_DIR / "nexy.prod"
        if delete:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("1", encoding="utf-8")

    @staticmethod
    def resolve_ports(
        host: str | None = None,
        port: int | None = None,
        with_client: bool = True,
    ) -> tuple[int, int]:
        """
        Calculates server and client ports in cascade.
        Returns (server_port, client_port).
        """
        cfg = Config()
        run_host: str = host or cfg.useHost
        base_port: int = port or cfg.usePort

        server_port = find_available_port(base_port, run_host)

        client_port = find_available_port(server_port + 1, run_host) if with_client else 0

        return server_port, client_port

    @staticmethod
    def get_network_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return str(s.getsockname()[0])
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()

    @staticmethod
    def get_ssl_config(config: Config) -> tuple[str | None, str | None]:
        if config.useSslKeyfile and config.useSslCertfile:
            return config.useSslKeyfile, config.useSslCertfile
        return None, None

    @staticmethod
    def stop_process(proc: Popen[Any] | None, timeout: int = 5) -> None:
        """Stops a child process cleanly (Windows or Unix)."""
        if not proc or proc.poll() is not None:
            return
        try:
            if sys.platform == "win32":
                taskkill_exe = shutil.which("taskkill") or "taskkill"
                subprocess.run(
                    [taskkill_exe, "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True,
                    timeout=timeout,
                    check=False,
                )  # nosec B603/B607 - resolved via shutil.which, fixed argv with proc.pid
            else:
                proc.terminate()
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=timeout)
        except (OSError, subprocess.SubprocessError):
            # Best-effort teardown: the caller proceeds either way.
            pass

    @staticmethod
    def uvicorn(
        host: str | None = None,
        port: int = 3000,
        as_process: bool = False,
        ssl_keyfile: str | None = None,
        ssl_certfile: str | None = None,
        workers: int | None = None,
    ) -> Popen[Any] | bool | None:
        """Starts the FastAPI/Uvicorn server with optional workers.

        Returns the spawned process when ``as_process`` is true, ``True`` when the
        foreground server stopped normally, and ``None`` when the launch failed.
        """
        cfg = Config()
        run_host = host or "127.0.0.1"

        if workers is not None:
            num_workers = workers
        elif hasattr(cfg, "useWorkers") and cfg.useWorkers:
            num_workers = cfg.useWorkers
        elif sys.platform == "win32":
            num_workers = 1
        else:
            num_workers = os.cpu_count() or 1

        _write_port_file("server", port)

        ssl_args: dict[str, Any] = {}
        if ssl_keyfile and ssl_certfile:
            ssl_args = {"ssl_keyfile": ssl_keyfile, "ssl_certfile": ssl_certfile}

        try:
            if as_process:
                ssl_kw = ", ".join(f"{k}='{v}'" for k, v in ssl_args.items())
                ssl_part = f", {ssl_kw}" if ssl_kw else ""
                workers_part = f", workers={num_workers}" if num_workers and num_workers > 1 else ""
                launcher_code = (
                    "import uvicorn\n"
                    "import sys\n"
                    "try:\n"
                    "    from nexy.helpers.server.uvicorn_config import NEXY_LOG_CONFIG\n"
                    f"    uvicorn.run('nexy.modules.routers.app:_server', host='{run_host}',"
                    f" port={port}, log_config=NEXY_LOG_CONFIG,"
                    f" log_level='info'{ssl_part}{workers_part})\n"
                    "except Exception as e:\n"
                    "    print(f'Critical error in Nexy subprocess: {e}')\n"
                    "    sys.exit(1)\n"
                )

                return subprocess.Popen(
                    [sys.executable, "-c", launcher_code],
                    stdout=None,
                    stderr=subprocess.STDOUT,
                )  # nosec B603 - argv is sys.executable plus a launcher built from config values
            else:
                workers_kwargs: dict[str, Any] = (
                    {"workers": num_workers} if num_workers and num_workers > 1 else {}
                )
                _uvicorn.run(
                    "nexy.modules.routers.app:_server",
                    host=run_host,
                    port=port,
                    log_config=NEXY_LOG_CONFIG,
                    log_level="info",
                    **ssl_args,
                    **workers_kwargs,
                )
                return True

        except Exception as exc:
            traceback.print_exc()
            print_console.print(f"[red]✘ Server launch failed:[/red] {exc}")
            return None

    @staticmethod
    def wait_for_vite_ready(port: int, host: str = "localhost", timeout: int = 30) -> bool:
        """Waits until the Vite dev server answers the readiness probe.

        The probe is a TCP connect, not an HTTP request: it only reports that
        the port accepts connections, which is what readiness means here.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                with socket.create_connection((host, port), timeout=1):
                    return True
            except OSError:
                time.sleep(0.2)
        return False

    @staticmethod
    def vite(
        port: int = 5173,
        build: bool = False,
        ssl: bool = False,
        suppress_output: bool | None = None,
        capture_stderr: bool = False,
    ) -> Popen[Any]:
        """Launches the Vite client."""
        pm, is_npm = _detect_pm()

        if suppress_output is None:
            suppress_output = build

        if build:
            args = [pm]
            args += ["exec", "--", "vite", "build"] if is_npm else ["exec", "vite", "build"]
        else:
            args = [pm]
            args += ["run", "dev"] if is_npm else ["dev"]
            _write_port_file("client", port)
            if is_npm:
                args.append("--")
            args += ["--port", str(port), "--host"]
            if ssl:
                args.append("--https")

        if capture_stderr:
            stderr = subprocess.PIPE
        elif suppress_output:
            stderr = subprocess.DEVNULL
        else:
            stderr = subprocess.STDOUT

        if suppress_output:
            stdout = subprocess.DEVNULL
        elif capture_stderr:
            stdout = subprocess.PIPE
        else:
            stdout = None

        return subprocess.Popen(args, stdout=stdout, stderr=stderr)  # nosec B603 - resolved devtool argv via _detect_pm
