"""The port Nexy gave up is freed by stopping the process that held it."""

from __future__ import annotations

import os
import signal
import subprocess

import pytest

from nexy.helpers.server import port_owner


def _done(stdout: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], 0, stdout)


def test_windows_owner_comes_from_netstat(monkeypatch):
    monkeypatch.setattr(
        port_owner.subprocess,
        "run",
        lambda *_a, **_k: _done("  TCP    0.0.0.0:3000    0.0.0.0:0    LISTENING    4242\n"),
    )
    assert port_owner._windows_pid(3000) == 4242


def test_windows_owner_when_no_line_matches(monkeypatch):
    monkeypatch.setattr(
        port_owner.subprocess,
        "run",
        lambda *_a, **_k: _done("  TCP    0.0.0.0:3001    0.0.0.0:0    LISTENING    4242\n"),
    )
    assert port_owner._windows_pid(3000) is None


def test_windows_owner_when_netstat_fails(monkeypatch):
    def fail(*_args, **_kwargs):
        raise OSError("netstat missing")

    monkeypatch.setattr(port_owner.subprocess, "run", fail)
    assert port_owner._windows_pid(3000) is None


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
    def fail(*_args, **_kwargs):
        raise OSError("lsof missing")

    monkeypatch.setattr(port_owner.shutil, "which", lambda _name: "/usr/bin/lsof")
    monkeypatch.setattr(port_owner.subprocess, "run", fail)
    assert port_owner._unix_pid(3000) is None


def test_owner_uses_netstat_on_windows(monkeypatch):
    monkeypatch.setattr(port_owner.sys, "platform", "win32")
    monkeypatch.setattr(port_owner, "_windows_pid", lambda _port: 7)
    assert port_owner.owner_pid(3000) == 7


def test_owner_uses_lsof_on_unix(monkeypatch):
    monkeypatch.setattr(port_owner.sys, "platform", "linux")
    monkeypatch.setattr(port_owner, "_unix_pid", lambda _port: 8)
    assert port_owner.owner_pid(3000) == 8


def test_terminate_leaves_protected_pids_alone(monkeypatch):
    called = []
    monkeypatch.setattr(port_owner.os, "kill", lambda pid, _sig: called.append(pid))
    port_owner._terminate(1)
    port_owner._terminate(os.getpid())
    assert called == []


def test_terminate_uses_taskkill_on_windows(monkeypatch):
    called = []
    monkeypatch.setattr(port_owner.sys, "platform", "win32")
    monkeypatch.setattr(port_owner.shutil, "which", lambda _name: "C:/bin/taskkill.exe")
    monkeypatch.setattr(port_owner.subprocess, "run", lambda argv, **_k: called.append(argv))
    port_owner._terminate(42)
    assert called == [["C:/bin/taskkill.exe", "/F", "/PID", "42"]]


def test_terminate_falls_back_to_the_taskkill_name(monkeypatch):
    called = []
    monkeypatch.setattr(port_owner.sys, "platform", "win32")
    monkeypatch.setattr(port_owner.shutil, "which", lambda _name: None)
    monkeypatch.setattr(port_owner.subprocess, "run", lambda argv, **_k: called.append(argv))
    port_owner._terminate(42)
    assert called == [["taskkill", "/F", "/PID", "42"]]


def test_terminate_sends_sigterm_on_unix(monkeypatch):
    called = []
    monkeypatch.setattr(port_owner.sys, "platform", "linux")
    monkeypatch.setattr(port_owner.os, "kill", lambda pid, sig: called.append((pid, sig)))
    port_owner._terminate(42)
    assert called == [(42, signal.SIGTERM)]


def test_terminate_ignores_a_process_that_is_gone(monkeypatch):
    attempts = []

    def gone(pid, _sig):
        attempts.append(pid)
        raise ProcessLookupError

    monkeypatch.setattr(port_owner.sys, "platform", "linux")
    monkeypatch.setattr(port_owner.os, "kill", gone)
    port_owner._terminate(42)
    assert attempts == [42]


def test_occupied_port_has_no_owner_when_it_was_free(monkeypatch):
    monkeypatch.setattr(port_owner, "owner_pid", lambda _port: pytest.fail("must not look"))
    assert port_owner.OccupiedPort(3000, 3000).pid is None


def test_occupied_port_remembers_the_owner_when_it_was_taken(monkeypatch):
    monkeypatch.setattr(port_owner, "owner_pid", lambda _port: 42)
    assert port_owner.OccupiedPort(3000, 3002).pid == 42


def test_free_does_nothing_without_a_recorded_owner(monkeypatch):
    monkeypatch.setattr(port_owner, "_terminate", lambda _pid: pytest.fail("must not stop"))
    assert port_owner.OccupiedPort(3000, 3000).free() is None


def test_free_does_nothing_when_the_owner_changed(monkeypatch):
    seen = []

    def owner(_port):
        seen.append(1)
        return 42 if len(seen) == 1 else 99

    monkeypatch.setattr(port_owner, "owner_pid", owner)
    monkeypatch.setattr(port_owner, "_terminate", lambda _pid: pytest.fail("must not stop"))
    assert port_owner.OccupiedPort(3000, 3002).free() is None


def test_free_stops_the_recorded_owner(monkeypatch):
    stopped = []
    monkeypatch.setattr(port_owner, "owner_pid", lambda _port: 42)
    monkeypatch.setattr(port_owner, "_terminate", stopped.append)
    occupied = port_owner.OccupiedPort(3000, 3002)
    assert (occupied.free(), stopped) == (42, [42])
