"""The pieces `Server` hands over to: each does one thing and is tested alone."""

from __future__ import annotations

import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from nexy.helpers.server import ports, processes, uvicorn_run, vite_process
from nexy.helpers.server.markers import set_production


class TestWorkerCount:
    def test_a_request_wins(self):
        assert uvicorn_run.worker_count(SimpleNamespace(useWorkers=4), 2) == 2

    def test_the_config_comes_next(self):
        assert uvicorn_run.worker_count(SimpleNamespace(useWorkers=4), None) == 4

    def test_windows_defaults_to_one(self):
        with patch.object(sys, "platform", "win32"):
            assert uvicorn_run.worker_count(SimpleNamespace(useWorkers=0), None) == 1

    def test_unix_defaults_to_one_per_cpu(self):
        with patch.object(sys, "platform", "linux"), patch("os.cpu_count", return_value=6):
            assert uvicorn_run.worker_count(SimpleNamespace(useWorkers=0), None) == 6


class TestUvicornOptions:
    def test_tls_needs_both_files(self):
        options = uvicorn_run._options("h", 1, "key.pem", None, 1)
        assert "ssl_keyfile" not in options

    def test_tls_is_passed_when_both_are_given(self):
        options = uvicorn_run._options("h", 1, "key.pem", "cert.pem", 1)
        assert (options["ssl_keyfile"], options["ssl_certfile"]) == ("key.pem", "cert.pem")

    def test_one_worker_is_not_a_worker_option(self):
        assert "workers" not in uvicorn_run._options("h", 1, None, None, 1)

    def test_several_workers_are_passed(self):
        assert uvicorn_run._options("h", 1, None, None, 3)["workers"] == 3

    def test_the_server_header_is_off_and_shutdown_is_bounded(self):
        options = uvicorn_run._options("h", 1, None, None, 1)
        assert options["server_header"] is False and options["timeout_graceful_shutdown"] == 10


class TestStopProcess:
    def test_windows_stops_a_process_with_taskkill(self):
        # Only the choice depends on the platform. Nothing of the standard library runs while it is
        # patched: on Linux, `shutil.which` would look for `_winapi`.
        process = MagicMock(pid=42)
        process.poll.return_value = None
        with (
            patch.object(sys, "platform", "win32"),
            patch.object(processes, "_kill_tree_windows") as kill_tree,
        ):
            processes.stop_process(process, timeout=3)
        kill_tree.assert_called_once_with(process, 3)

    def test_taskkill_ends_the_whole_tree_of_the_process(self):
        process = MagicMock(pid=42)
        with (
            patch.object(processes.shutil, "which", return_value="C:/Windows/taskkill.exe"),
            patch.object(subprocess, "run") as run,
        ):
            processes._kill_tree_windows(process, 5)
        assert run.call_args.args[0] == ["C:/Windows/taskkill.exe", "/F", "/T", "/PID", "42"]

    def test_taskkill_is_found_by_name_when_it_is_not_on_the_path(self):
        process = MagicMock(pid=7)
        with (
            patch.object(processes.shutil, "which", return_value=None),
            patch.object(subprocess, "run") as run,
        ):
            processes._kill_tree_windows(process, 5)
        assert run.call_args.args[0][0] == "taskkill"

    def test_unix_kills_a_process_that_ignores_terminate(self):
        process = MagicMock()
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("x", 1), None]
        with patch.object(sys, "platform", "linux"):
            processes.stop_process(process)
        process.kill.assert_called_once()

    def test_a_failure_to_stop_is_swallowed(self):
        process = MagicMock()
        process.poll.return_value = None
        process.terminate.side_effect = OSError("gone")
        with patch.object(sys, "platform", "linux"):
            processes.stop_process(process)


class TestViteStreams:
    @pytest.mark.parametrize(
        ("suppress", "capture", "expected"),
        [
            (False, False, (None, subprocess.STDOUT)),
            (True, False, (subprocess.DEVNULL, subprocess.DEVNULL)),
            (False, True, (subprocess.PIPE, subprocess.PIPE)),
            (True, True, (subprocess.DEVNULL, subprocess.PIPE)),
        ],
    )
    def test_the_streams_follow_the_flags(self, suppress, capture, expected):
        assert vite_process._streams(suppress, capture) == expected


class TestPorts:
    def test_the_client_port_comes_after_the_server_port(self):
        server, client = ports.resolve_ports("127.0.0.1", 41230)
        assert client > server

    def test_no_client_means_port_zero(self):
        assert ports.resolve_ports("127.0.0.1", 41240, with_client=False)[1] == 0

    def test_the_network_address_is_loopback_when_there_is_no_network(self):
        with patch("socket.socket") as sock:
            sock.return_value.connect.side_effect = OSError
            assert ports.network_ip() == "127.0.0.1"


def test_the_production_marker_is_created_then_removed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("nexy.helpers.server.markers._PRODUCTION_MARKER", tmp_path / "m" / "prod")
    set_production(True)
    assert (tmp_path / "m" / "prod").read_text(encoding="utf-8") == "1"
    set_production(False)
    assert not (tmp_path / "m" / "prod").exists()
