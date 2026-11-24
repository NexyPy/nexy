"""The port Nexy gave up is freed by stopping the process that held it."""

from __future__ import annotations

import ctypes
import os
import signal
import socket
import struct
import subprocess
from ctypes import wintypes
from types import SimpleNamespace
from typing import Any

import pytest

from nexy.helpers.server import port_owner


def _done(stdout: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], 0, stdout)


def test_windll_uses_last_error(monkeypatch):
    seen = []

    def fake(name: str, **kwargs: Any) -> object:
        seen.append((name, kwargs))
        return object()

    monkeypatch.setattr(port_owner.ctypes, "WinDLL", fake, raising=False)
    port_owner._windll("kernel32")
    assert seen == [("kernel32", {"use_last_error": True})]


def test_tcp_api_is_none_outside_windows(monkeypatch):
    monkeypatch.setattr(port_owner.sys, "platform", "linux")
    assert port_owner._tcp_api() is None


def test_tcp_api_returns_the_windows_call(monkeypatch):
    class Dll:
        GetExtendedTcpTable = object()

    dll = Dll()
    monkeypatch.setattr(port_owner.sys, "platform", "win32")
    monkeypatch.setattr(port_owner, "_windll", lambda _name: dll)
    assert port_owner._tcp_api() is dll.GetExtendedTcpTable


def test_windows_owner_is_none_without_the_tcp_api(monkeypatch):
    monkeypatch.setattr(port_owner, "_tcp_api", lambda: None)
    assert port_owner._windows_pid(3000) is None


def test_windows_owner_comes_from_the_tcp_table(monkeypatch):
    row = port_owner._TcpRow(state=2, local_port=socket.htons(3000), pid=4242)
    row_size = ctypes.sizeof(row)

    def api(buffer: Any, size: Any, *_args: Any) -> int:
        size.contents.value = 4 + row_size
        if buffer is None:
            return port_owner._INSUFFICIENT_BUFFER
        ctypes.memmove(buffer, struct.pack("I", 1), 4)
        ctypes.memmove(ctypes.byref(buffer, 4), ctypes.byref(row), row_size)
        return 0

    monkeypatch.setattr(port_owner, "_tcp_api", lambda: api)
    assert port_owner._windows_pid(3000) == 4242


def test_windows_owner_ignores_another_port(monkeypatch):
    row = port_owner._TcpRow(state=2, local_port=socket.htons(3001), pid=4242)
    row_size = ctypes.sizeof(row)

    def api(buffer: Any, size: Any, *_args: Any) -> int:
        size.contents.value = 4 + row_size
        if buffer is None:
            return port_owner._INSUFFICIENT_BUFFER
        ctypes.memmove(buffer, struct.pack("I", 1), 4)
        ctypes.memmove(ctypes.byref(buffer, 4), ctypes.byref(row), row_size)
        return 0

    monkeypatch.setattr(port_owner, "_tcp_api", lambda: api)
    assert port_owner._windows_pid(3000) is None


def test_windows_owner_when_table_size_is_unavailable(monkeypatch):
    def api(_buffer: Any, _size: Any, *_args: Any) -> int:
        return 1

    monkeypatch.setattr(port_owner, "_tcp_api", lambda: api)
    assert port_owner._windows_pid(3000) is None


def test_windows_owner_when_table_read_fails(monkeypatch):
    def api(buffer: Any, size: Any, *_args: Any) -> int:
        size.contents.value = 4
        return port_owner._INSUFFICIENT_BUFFER if buffer is None else 1

    monkeypatch.setattr(port_owner, "_tcp_api", lambda: api)
    assert port_owner._windows_pid(3000) is None


def test_hex_port_ignores_a_malformed_address():
    assert port_owner._hex_port("nope") is None


def test_linux_owner_comes_from_proc(monkeypatch, tmp_path):
    tcp = tmp_path / "tcp"
    tcp.write_text(
        "header\n"
        "0: 0100007F:0BB8 00000000:0000 0A 00000000:00000000 "
        "00:00000000 00000000 42 1 12345\n"
    )
    (tmp_path / "tcp6").write_text("header\n")
    monkeypatch.setattr(port_owner, "_PROC_TCP_FILES", (tcp, tmp_path / "tcp6"))
    monkeypatch.setattr(
        port_owner, "_pid_for_inode", lambda inode: 42 if inode == "12345" else None
    )
    assert port_owner._proc_pid(3000) == 42


def test_linux_owner_ignores_non_listening_rows(monkeypatch, tmp_path):
    tcp = tmp_path / "tcp"
    tcp.write_text(
        "header\n"
        "0: 0100007F:0BB8 00000000:0000 01 00000000:00000000 "
        "00:00000000 00000000 42 1 12345\n"
    )
    monkeypatch.setattr(port_owner, "_PROC_TCP_FILES", (tcp,))
    assert port_owner._proc_pid(3000) is None


def test_linux_owner_when_proc_files_are_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(port_owner, "_PROC_TCP_FILES", (tmp_path / "missing",))
    assert port_owner._proc_pid(3000) is None


def test_pid_for_inode_finds_the_matching_socket(monkeypatch):
    entries = [
        SimpleNamespace(name="42", path="/proc/42"),
        SimpleNamespace(name="self", path="/proc/self"),
    ]
    descriptors = [SimpleNamespace(path="/proc/42/fd/3")]
    monkeypatch.setattr(port_owner, "_PROC_ROOT", "/proc")
    monkeypatch.setattr(
        port_owner.os, "scandir", lambda path: entries if path == "/proc" else descriptors
    )
    monkeypatch.setattr(port_owner.os, "readlink", lambda _path: "socket:[12345]")
    assert port_owner._pid_for_inode("12345") == 42


def test_pid_for_inode_skips_non_process_entries(monkeypatch):
    entries = [SimpleNamespace(name="self", path="/proc/self")]
    monkeypatch.setattr(port_owner.os, "scandir", lambda path: entries if path == "/proc" else [])
    assert port_owner._pid_for_inode("12345") is None


def test_pid_for_inode_ignores_another_socket(monkeypatch):
    entries = [SimpleNamespace(name="42", path="/proc/42")]
    descriptors = [SimpleNamespace(path="/proc/42/fd/3")]
    monkeypatch.setattr(
        port_owner.os,
        "scandir",
        lambda path: entries if path == "/proc" else descriptors,
    )
    monkeypatch.setattr(port_owner.os, "readlink", lambda _path: "socket:[99]")
    assert port_owner._pid_for_inode("12345") is None


def test_pid_for_inode_when_nobody_holds_the_socket(monkeypatch):
    entries = [SimpleNamespace(name="42", path="/proc/42")]
    monkeypatch.setattr(port_owner.os, "scandir", lambda path: entries if path == "/proc" else [])
    monkeypatch.setattr(port_owner.os, "readlink", lambda _path: "pipe:[7]")
    assert port_owner._pid_for_inode("12345") is None


def test_pid_for_inode_when_readlink_is_denied(monkeypatch):
    def denied(_path: str) -> str:
        raise OSError("permission denied")

    monkeypatch.setattr(
        port_owner.os,
        "scandir",
        lambda path: (
            [SimpleNamespace(name="42", path=f"{path}/fd/3")]
            if path == "/proc"
            else [SimpleNamespace(path=f"{path}/3")]
        ),
    )
    monkeypatch.setattr(port_owner.os, "readlink", denied)
    assert port_owner._pid_for_inode("12345") is None


def test_unix_owner_comes_from_lsof(monkeypatch):
    monkeypatch.setattr(port_owner.shutil, "which", lambda _name: "/usr/bin/lsof")
    monkeypatch.setattr(port_owner.subprocess, "run", lambda *_a, **_k: _done("4242\n"))
    assert port_owner._unix_pid(3000) == 4242


def test_unix_owner_ignores_lines_that_are_not_pids(monkeypatch):
    monkeypatch.setattr(port_owner.shutil, "which", lambda _name: "/usr/bin/lsof")
    monkeypatch.setattr(port_owner.subprocess, "run", lambda *_a, **_k: _done("banner\n4242\n"))
    assert port_owner._unix_pid(3000) == 4242


def test_unix_owner_when_lsof_is_missing(monkeypatch):
    monkeypatch.setattr(port_owner.shutil, "which", lambda _name: None)
    assert port_owner._unix_pid(3000) is None


def test_unix_owner_when_lsof_fails(monkeypatch):
    def fail(*_args: Any, **_kwargs: Any) -> None:
        raise OSError("lsof missing")

    monkeypatch.setattr(port_owner.shutil, "which", lambda _name: "/usr/bin/lsof")
    monkeypatch.setattr(port_owner.subprocess, "run", fail)
    assert port_owner._unix_pid(3000) is None


def test_owner_uses_tcp_table_on_windows(monkeypatch):
    monkeypatch.setattr(port_owner.sys, "platform", "win32")
    monkeypatch.setattr(port_owner, "_windows_pid", lambda _port: 7)
    assert port_owner.owner_pid(3000) == 7


def test_owner_uses_proc_on_linux(monkeypatch):
    monkeypatch.setattr(port_owner.sys, "platform", "linux")
    monkeypatch.setattr(port_owner, "_proc_pid", lambda _port: 8)
    assert port_owner.owner_pid(3000) == 8


def test_owner_uses_lsof_on_other_unix(monkeypatch):
    monkeypatch.setattr(port_owner.sys, "platform", "darwin")
    monkeypatch.setattr(port_owner, "_unix_pid", lambda _port: 9)
    assert port_owner.owner_pid(3000) == 9


def test_kernel32_is_none_outside_windows(monkeypatch):
    monkeypatch.setattr(port_owner.sys, "platform", "linux")
    assert port_owner._kernel32() is None


def test_kernel32_configures_the_handle_type(monkeypatch):
    kernel = SimpleNamespace(OpenProcess=lambda *_args: None)
    monkeypatch.setattr(port_owner.sys, "platform", "win32")
    monkeypatch.setattr(port_owner, "_windll", lambda _name: kernel)
    result = port_owner._kernel32()
    assert (result is kernel, kernel.OpenProcess.restype) == (True, wintypes.HANDLE)


def test_terminate_windows_is_none_without_kernel32(monkeypatch):
    monkeypatch.setattr(port_owner, "_kernel32", lambda: None)
    assert port_owner._terminate_windows(42) is None


def test_terminate_windows_closes_the_handle(monkeypatch):
    called = []
    kernel = SimpleNamespace(
        OpenProcess=lambda *_args: 99,
        TerminateProcess=lambda *_args: called.append(("terminate",)),
        CloseHandle=lambda *_args: called.append(("close",)),
    )
    monkeypatch.setattr(port_owner, "_kernel32", lambda: kernel)
    port_owner._terminate_windows(42)
    assert called == [("terminate",), ("close",)]


def test_terminate_windows_when_open_fails(monkeypatch):
    called = []
    kernel = SimpleNamespace(
        OpenProcess=lambda *_args: 0,
        TerminateProcess=lambda *_args: called.append(("terminate",)),
        CloseHandle=lambda *_args: called.append(("close",)),
    )
    monkeypatch.setattr(port_owner, "_kernel32", lambda: kernel)
    port_owner._terminate_windows(42)
    assert called == []


def test_terminate_leaves_protected_pids_alone(monkeypatch):
    called = []
    monkeypatch.setattr(port_owner.os, "kill", lambda pid, _sig: called.append(pid))
    port_owner._terminate(1, 3000)
    port_owner._terminate(os.getpid(), 3000)
    assert called == []


def test_terminate_uses_windows_api(monkeypatch):
    called = []
    monkeypatch.setattr(port_owner.sys, "platform", "win32")
    monkeypatch.setattr(port_owner, "_terminate_windows", called.append)
    port_owner._terminate(42, 3000)
    assert called == [42]


def test_terminate_sends_sigterm_on_unix(monkeypatch):
    called = []
    monkeypatch.setattr(port_owner.sys, "platform", "linux")
    monkeypatch.setattr(port_owner.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(port_owner, "owner_pid", lambda _port: None)
    monkeypatch.setattr(port_owner.os, "kill", lambda pid, sig: called.append((pid, sig)))
    port_owner._terminate(42, 3000)
    assert called == [(42, signal.SIGTERM)]


def test_terminate_sends_sigkill_when_the_owner_holds_on(monkeypatch):
    called = []
    monkeypatch.setattr(port_owner.sys, "platform", "linux")
    monkeypatch.setattr(port_owner.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(port_owner, "owner_pid", lambda _port: 42)
    monkeypatch.setattr(port_owner.os, "kill", lambda pid, sig: called.append((pid, sig)))
    port_owner._terminate(42, 3000)
    assert called == [(42, signal.SIGTERM), (42, signal.SIGKILL)]


def test_terminate_ignores_a_process_that_is_gone(monkeypatch):
    attempts = []

    def gone(pid: int, _sig: int) -> None:
        attempts.append(pid)
        raise ProcessLookupError

    monkeypatch.setattr(port_owner.sys, "platform", "linux")
    monkeypatch.setattr(port_owner.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(port_owner, "owner_pid", lambda _port: 42)
    monkeypatch.setattr(port_owner.os, "kill", gone)
    port_owner._terminate(42, 3000)
    assert attempts == [42, 42]


def test_occupied_port_has_no_owner_when_it_was_free(monkeypatch):
    monkeypatch.setattr(port_owner, "owner_pid", lambda _port: pytest.fail("must not look"))
    assert port_owner.OccupiedPort(3000, 3000).pid is None


def test_occupied_port_remembers_the_owner_when_it_was_taken(monkeypatch):
    monkeypatch.setattr(port_owner, "owner_pid", lambda _port: 42)
    assert port_owner.OccupiedPort(3000, 3002).pid == 42


def test_free_does_nothing_without_a_recorded_owner(monkeypatch):
    monkeypatch.setattr(port_owner, "_terminate", lambda *_args: pytest.fail("must not stop"))
    assert port_owner.OccupiedPort(3000, 3000).free() is None


def test_free_does_nothing_when_the_owner_changed(monkeypatch):
    seen = []

    def owner(_port: int) -> int:
        seen.append(1)
        return 42 if len(seen) == 1 else 99

    monkeypatch.setattr(port_owner, "owner_pid", owner)
    monkeypatch.setattr(port_owner, "_terminate", lambda *_args: pytest.fail("must not stop"))
    assert port_owner.OccupiedPort(3000, 3002).free() is None


def test_free_stops_the_recorded_owner(monkeypatch):
    stopped = []
    monkeypatch.setattr(port_owner, "owner_pid", lambda _port: 42)
    monkeypatch.setattr(port_owner, "_terminate", lambda pid, port: stopped.append((pid, port)))
    occupied = port_owner.OccupiedPort(3000, 3002)
    assert (occupied.free(), stopped) == (42, [(42, 3000)])
