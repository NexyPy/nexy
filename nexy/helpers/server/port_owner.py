"""Find the process listening on a port Nexy had to give up, so stopping Nexy frees it.

The owner is looked up when the port is found busy, then stopped when Nexy stops. When the owner
cannot be identified, or has changed by then, nothing is killed.
"""

from __future__ import annotations

import contextlib
import os
import re
import shutil
import signal
import subprocess  # nosec B404
import sys


def _windows_pid(port: int) -> int | None:
    """The PID netstat reports as listening on *port*."""
    netstat = shutil.which("netstat") or "netstat"
    try:
        done = subprocess.run(
            [netstat, "-ano", "-p", "tcp"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )  # nosec B603/B607 - resolved via shutil.which, fixed argv, no shell
    except (OSError, subprocess.SubprocessError):
        return None
    listening = re.compile(rf"\s*TCP\s+\S+:{port}\s+\S+\s+LISTENING\s+(\d+)")
    for line in done.stdout.splitlines():
        match = listening.match(line)
        if match:
            return int(match.group(1))
    return None


def _unix_pid(port: int) -> int | None:
    """The PID lsof reports as listening on *port*."""
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
    return _unix_pid(port)


def _terminate(pid: int) -> None:
    """Ask the recorded process to stop; leave it alone when it is gone or protected."""
    if pid in (0, 1, os.getpid()):
        return
    if sys.platform == "win32":
        taskkill = shutil.which("taskkill") or "taskkill"
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(
                [taskkill, "/F", "/PID", str(pid)],
                capture_output=True,
                timeout=5,
                check=False,
            )  # nosec B603 - resolved via shutil.which, no shell
        return
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.kill(pid, signal.SIGTERM)


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
        _terminate(self.pid)
        return self.pid
