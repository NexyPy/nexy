"""Find and stop the process listening on a port Nexy had to give up, quickly.

The owner is looked up when the port is found busy, then stopped when Nexy stops. The lookup
reads the OS TCP table on Linux and Windows, without spawning a process, and the same owner is
checked again before anything is killed. When the owner cannot be identified, or has changed
by then, nothing is killed.
"""

from __future__ import annotations

import contextlib
import ctypes
import os
import shutil
import signal
import socket
import struct
import subprocess  # nosec B404
import sys
import time
from ctypes import wintypes
from typing import Any

_LISTEN = "0A"
_TCP_LISTEN = 2
_AF_INET = 2
_TCP_TABLE_OWNER_PID_LISTENER = 3
_INSUFFICIENT_BUFFER = 122
_PROCESS_TERMINATE = 0x0001
_KILL_GRACE = 0.1
_PROC_TCP_FILES = ("/proc/net/tcp", "/proc/net/tcp6")
_PROC_ROOT = "/proc"


class _TcpRow(ctypes.Structure):
    """One row of the Windows TCP table with the owning PID."""

    _fields_ = [
        ("state", wintypes.DWORD),
        ("local_addr", wintypes.DWORD),
        ("local_port", wintypes.DWORD),
        ("remote_addr", wintypes.DWORD),
        ("remote_port", wintypes.DWORD),
        ("pid", wintypes.DWORD),
    ]


def _windll(name: str) -> Any:
    """Load a Windows DLL with the error state kept for ctypes calls."""
    return ctypes.WinDLL(name, use_last_error=True)  # type: ignore[attr-defined]


def _tcp_api() -> Any | None:
    """The Windows TCP table call, or None outside Windows."""
    if sys.platform != "win32":
        return None
    return _windll("iphlpapi").GetExtendedTcpTable


def _windows_pid(port: int) -> int | None:
    """The PID listening on *port*, from the TCP table without a subprocess."""
    api = _tcp_api()
    if api is None:
        return None
    size = wintypes.DWORD()
    first = api(None, ctypes.pointer(size), False, _AF_INET, _TCP_TABLE_OWNER_PID_LISTENER, 0)
    if first != _INSUFFICIENT_BUFFER:
        return None
    table = ctypes.create_string_buffer(size.value)
    if api(table, ctypes.pointer(size), False, _AF_INET, _TCP_TABLE_OWNER_PID_LISTENER, 0):
        return None
    count = struct.unpack_from("I", table, 0)[0]
    row_size = ctypes.sizeof(_TcpRow)
    for index in range(count):
        row = ctypes.cast(ctypes.byref(table, 4 + index * row_size), ctypes.POINTER(_TcpRow))
        if row.contents.state == _TCP_LISTEN and socket.ntohs(row.contents.local_port) == port:
            return int(row.contents.pid)
    return None


def _hex_port(address: str) -> int | None:
    """The port at the end of a /proc/net/tcp local address."""
    try:
        return int(address.rsplit(":", 1)[-1], 16)
    except ValueError:
        return None


def _listen_inode(port: int) -> str | None:
    """The socket inode listening on *port*, from /proc."""
    for path in _PROC_TCP_FILES:
        try:
            with open(path, encoding="utf-8") as stream:
                next(stream, None)
                for line in stream:
                    fields = line.split()
                    if len(fields) > 9 and fields[3] == _LISTEN and _hex_port(fields[1]) == port:
                        return fields[9]
        except OSError:
            continue
    return None


def _pid_for_inode(inode: str) -> int | None:
    """The PID holding the socket inode, from /proc."""
    target = f"socket:[{inode}]"
    for entry in os.scandir(_PROC_ROOT):
        if not entry.name.isdigit():
            continue
        with contextlib.suppress(OSError):
            for descriptor in os.scandir(f"{entry.path}/fd"):
                if os.readlink(descriptor.path) == target:
                    return int(entry.name)
    return None


def _proc_pid(port: int) -> int | None:
    """The PID listening on *port*, read from /proc without a subprocess."""
    inode = _listen_inode(port)
    return _pid_for_inode(inode) if inode is not None else None


def _unix_pid(port: int) -> int | None:
    """The PID lsof reports as listening on *port*, on systems without /proc."""
    lsof = shutil.which("lsof")
    if not lsof:
        return None
    try:
        done = subprocess.run(
            [lsof, "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )  # nosec B603 - resolved via shutil.which, no shell
    except (OSError, subprocess.SubprocessError):
        return None
    pids = [int(line) for line in done.stdout.split() if line.isdigit()]
    return pids[0] if pids else None


def owner_pid(port: int) -> int | None:
    """The PID listening on *port*, or None when the system cannot tell."""
    if sys.platform == "win32":
        return _windows_pid(port)
    if sys.platform.startswith("linux"):
        return _proc_pid(port)
    return _unix_pid(port)


def _kernel32() -> Any | None:
    """The Windows kernel API, with a handle type wide enough on 64-bit systems."""
    if sys.platform != "win32":
        return None
    kernel = _windll("kernel32")
    kernel.OpenProcess.restype = wintypes.HANDLE
    return kernel


def _terminate_windows(pid: int) -> None:
    """Ask Windows to stop the recorded process, without spawning taskkill."""
    kernel = _kernel32()
    if kernel is None:
        return
    handle = kernel.OpenProcess(_PROCESS_TERMINATE, False, pid)
    if not handle:
        return
    try:
        kernel.TerminateProcess(handle, 1)
    finally:
        kernel.CloseHandle(handle)


def _still_listening(pid: int, port: int) -> bool:
    """Whether the same process still owns the port after a short grace period."""
    time.sleep(_KILL_GRACE)
    return owner_pid(port) == pid


def _terminate(pid: int, port: int) -> None:
    """Stop the recorded process; leave it alone when it is gone or protected."""
    if pid in (0, 1, os.getpid()):
        return
    if sys.platform == "win32":
        _terminate_windows(pid)
        return
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.kill(pid, signal.SIGTERM)
    if _still_listening(pid, port):
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.kill(pid, signal.SIGKILL)


class OccupiedPort:
    """The port Nexy wanted but another process held, freed when Nexy stops."""

    def __init__(self, asked: int, used: int) -> None:
        self.asked = asked
        self.pid = owner_pid(asked) if asked != used else None

    def free(self) -> int | None:
        """Stop the recorded owner if it still holds the port; return its PID."""
        if self.pid is None:
            return None
        if owner_pid(self.asked) != self.pid:
            return None
        _terminate(self.pid, self.asked)
        return self.pid
