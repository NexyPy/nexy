"""E2E harness: boots a real `nexy` dev stack (uvicorn + Vite) once per session.

The stack runs against a temp copy of ``tests/fixtures/client_router`` so tests
can exercise client-side routing in a real browser without touching the repo.

Order matters and mirrors `nexy dev`: generate + build write ``__nexy__`` to
disk first, then Vite starts (it resolves ``./__nexy__/vite`` from disk), then
uvicorn serves the generated routes.
"""

import shutil
import socket
import subprocess  # nosec B404
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "client_router"


def _wait_for_port(port: int, host: str = "127.0.0.1", timeout: float = 60.0) -> bool:
    """Wait until *port* accepts TCP connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _run(project: Path, *args: str) -> None:
    subprocess.run(  # nosec B603 - fixed argv, no shell
        list(args),
        cwd=project,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _install_node_modules(project: Path) -> None:
    pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd") or "pnpm"
    _run(project, pnpm, "install", "--allow-build=esbuild")


def _generate(project: Path) -> None:
    """Generate + build the project, writing ``__nexy__`` to disk."""
    launcher = (
        "from nexy.modules.frontend import FrontendGenerator\n"
        "from nexy.modules.builder import Builder\n"
        "FrontendGenerator().generate()\n"
        "result = Builder().build(showlog=False)\n"
        "raise SystemExit(1 if result.failed else 0)\n"
    )
    _run(project, sys.executable, "-c", launcher)


def _start_vite(project: Path, port: int) -> subprocess.Popen[bytes]:
    pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd") or "pnpm"
    return subprocess.Popen(  # nosec B603 - resolved package manager, fixed args
        [pnpm, "dev", "--port", str(port), "--host", "127.0.0.1"],
        cwd=project,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _start_uvicorn(project: Path, port: int) -> subprocess.Popen[bytes]:
    launcher = (
        "import uvicorn\n"
        "from nexy.helpers.server.uvicorn_config import NEXY_LOG_CONFIG\n"
        "uvicorn.run('nexy.modules.routers.app:_server', host='127.0.0.1',"
        f" port={port}, log_config=NEXY_LOG_CONFIG, log_level='warning')\n"
    )
    return subprocess.Popen(  # nosec B603 - argv is sys.executable plus a fixed launcher
        [sys.executable, "-c", launcher],
        cwd=project,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class DevStack:
    """Handle to the running dev stack used by the browser tests."""

    def __init__(self, server_port: int) -> None:
        self.server_port = server_port

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"


@pytest.fixture(scope="session")
def dev_stack(tmp_path_factory: pytest.TempPathFactory) -> Iterator[DevStack]:
    """Boot one dev stack for the whole E2E session."""
    project = tmp_path_factory.mktemp("nexy_e2e") / "app"
    shutil.copytree(FIXTURE_DIR, project)

    _install_node_modules(project)
    _generate(project)

    server_port = _free_port()
    client_port = _free_port()

    nexy_dir = project / "__nexy__"
    (nexy_dir / "client.port").write_text(str(client_port), encoding="utf-8")
    (nexy_dir / "server.port").write_text(str(server_port), encoding="utf-8")

    vite_proc = _start_vite(project, client_port)
    server_proc = _start_uvicorn(project, server_port)

    from nexy.helpers.server.server import Server

    try:
        if not _wait_for_port(client_port):
            raise RuntimeError("Vite did not start")
        if not _wait_for_port(server_port):
            raise RuntimeError("uvicorn did not start")
        yield DevStack(server_port)
    finally:
        Server.stop_process(vite_proc)
        Server.stop_process(server_proc)
