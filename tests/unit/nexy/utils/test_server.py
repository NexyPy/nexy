import subprocess
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from nexy.helpers.server import server as server_module
from nexy.helpers.server.server import Server, _write_port_file


@pytest.fixture(autouse=True)
def _isolated_vfs() -> Any:
    """Starts each test from an empty in-memory VFS and restores it afterwards."""
    vfs = server_module.VFS()
    saved_files = dict(vfs._files)
    vfs.clear()
    yield vfs
    vfs.clear()
    vfs._files.update(saved_files)


def test_write_port_file_stores_port_in_vfs() -> None:
    _write_port_file("server", 4000)

    assert server_module.VFS().read("__nexy__/server.port") == "4000"


def test_check_nexy_prod_creates_marker(tmp_path: Any) -> None:
    import os

    orig = os.getcwd()
    try:
        os.chdir(tmp_path)
        Server.check_nexy_prod(delete=False)

        marker = tmp_path / "__nexy__" / "nexy.prod"
        assert marker.read_text(encoding="utf-8") == "1"
    finally:
        os.chdir(orig)


def test_check_nexy_prod_delete_removes_marker(tmp_path: Any) -> None:
    import os

    orig = os.getcwd()
    try:
        os.chdir(tmp_path)
        Server.check_nexy_prod(delete=False)
        Server.check_nexy_prod(delete=True)

        marker = tmp_path / "__nexy__" / "nexy.prod"
        assert not marker.exists()
    finally:
        os.chdir(orig)


def test_get_network_ip_returns_dotted_quad() -> None:
    assert Server.get_network_ip().count(".") == 3


def test_get_ssl_config_returns_both_files_when_set() -> None:
    cfg = MagicMock()
    cfg.useSslKeyfile = "key.pem"
    cfg.useSslCertfile = "cert.pem"

    assert Server.get_ssl_config(cfg) == ("key.pem", "cert.pem")


def test_get_ssl_config_returns_none_when_certfile_missing() -> None:
    cfg = MagicMock()
    cfg.useSslKeyfile = "key.pem"
    cfg.useSslCertfile = None

    assert Server.get_ssl_config(cfg) == (None, None)


def test_stop_process_is_noop_for_none() -> None:
    assert Server.stop_process(None) is None


def test_stop_process_is_noop_for_finished_process() -> None:
    proc = MagicMock()
    proc.poll.return_value = 0

    assert Server.stop_process(proc) is None


def test_stop_process_terminates_live_unix_child() -> None:
    proc = MagicMock()
    proc.poll.return_value = None

    with patch.object(sys, "platform", "linux"):
        Server.stop_process(proc)

    proc.terminate.assert_called_once()


def test_wait_for_vite_ready_connects_to_specified_port() -> None:
    probed: list[tuple[str, int]] = []

    def _capture(address: tuple[str, int], timeout: float | None = None) -> MagicMock:
        del timeout  # signature must match socket.create_connection callers
        probed.append(address)
        return MagicMock()

    with (
        patch("socket.create_connection", side_effect=_capture),
        patch.object(server_module.time, "sleep"),
    ):
        ready = Server.wait_for_vite_ready(5173, timeout=1)

    assert ready is True
    assert probed[0][1] == 5173


def test_wait_for_vite_ready_returns_false_when_never_ready() -> None:
    with (
        patch("socket.create_connection", side_effect=OSError),
        patch.object(server_module.time, "sleep"),
    ):
        ready = Server.wait_for_vite_ready(5173, timeout=0.3)

    assert ready is False


def test_uvicorn_as_process_returns_spawned_popen(tmp_path: Any) -> None:
    import os

    proc = MagicMock(spec=subprocess.Popen)
    orig = os.getcwd()
    try:
        os.chdir(tmp_path)
        with patch.object(subprocess, "Popen", return_value=proc):
            result = Server.uvicorn(host="127.0.0.1", port=3999, as_process=True)
    finally:
        os.chdir(orig)

    assert result is proc


def test_uvicorn_foreground_returns_true(tmp_path: Any) -> None:
    import os

    orig = os.getcwd()
    try:
        os.chdir(tmp_path)
        with patch.object(server_module._uvicorn, "run", return_value=None):
            result = Server.uvicorn(host="127.0.0.1", port=3998, as_process=False)
    finally:
        os.chdir(orig)

    assert result is True


def test_uvicorn_returns_none_when_launch_fails(tmp_path: Any) -> None:
    import os

    orig = os.getcwd()
    try:
        os.chdir(tmp_path)
        with patch.object(server_module._uvicorn, "run", side_effect=OSError("boom")):
            result = Server.uvicorn(host="127.0.0.1", port=3997, as_process=False)
    finally:
        os.chdir(orig)

    assert result is None


def test_uvicorn_passes_explicit_workers_to_uvicorn(tmp_path: Any) -> None:
    import os

    captured: dict[str, Any] = {}

    def _fake_run(*_args: Any, **kwargs: Any) -> None:
        captured.update(kwargs)

    orig = os.getcwd()
    try:
        os.chdir(tmp_path)
        with patch.object(server_module._uvicorn, "run", side_effect=_fake_run):
            Server.uvicorn(host="127.0.0.1", port=3996, workers=4)
    finally:
        os.chdir(orig)

    assert captured["workers"] == 4


def test_resolve_ports_skips_client_port_when_disabled() -> None:
    server_port, client_port = Server.resolve_ports("127.0.0.1", 3995, with_client=False)

    assert client_port == 0
    assert server_port == 3995


def test_vite_argv_build_runs_local_vite(tmp_path: Any, monkeypatch: Any) -> None:
    from pathlib import Path

    vite = Path("node_modules") / "vite" / "bin" / "vite.js"
    (tmp_path / vite).parent.mkdir(parents=True)
    (tmp_path / vite).write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        server_module.shutil, "which", lambda name: "C:/node.exe" if name == "node" else None
    )

    argv = Server._vite_argv(build=True, port=5173, ssl=False)

    assert argv == ["C:/node.exe", str(vite), "build"]


def test_vite_argv_dev_passes_port_and_host(tmp_path: Any, monkeypatch: Any) -> None:
    from pathlib import Path

    vite = Path("node_modules") / "vite" / "bin" / "vite.js"
    (tmp_path / vite).parent.mkdir(parents=True)
    (tmp_path / vite).write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        server_module.shutil, "which", lambda name: "C:/node.exe" if name == "node" else None
    )

    argv = Server._vite_argv(build=False, port=3456, ssl=False)

    assert argv[-3:] == ["--port", "3456", "--host"]


def test_vite_argv_dev_appends_https(tmp_path: Any, monkeypatch: Any) -> None:
    from pathlib import Path

    vite = Path("node_modules") / "vite" / "bin" / "vite.js"
    (tmp_path / vite).parent.mkdir(parents=True)
    (tmp_path / vite).write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        server_module.shutil, "which", lambda name: "C:/node.exe" if name == "node" else None
    )

    assert Server._vite_argv(build=False, port=3456, ssl=True)[-1] == "--https"


def test_vite_argv_raises_when_node_is_missing(monkeypatch: Any) -> None:
    monkeypatch.setattr(server_module.shutil, "which", lambda *_: None)

    with pytest.raises(RuntimeError, match="Node.js"):
        Server._vite_argv(build=True, port=5173, ssl=False)


def test_vite_argv_raises_when_vite_is_missing(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        server_module.shutil, "which", lambda name: "C:/node.exe" if name == "node" else None
    )

    with pytest.raises(RuntimeError, match="Vite is not installed"):
        Server._vite_argv(build=True, port=5173, ssl=False)


def test_wait_for_vite_ready_stops_when_process_exited() -> None:
    process = MagicMock()
    process.poll.return_value = 1

    assert Server.wait_for_vite_ready(5173, timeout=30, process=process) is False
