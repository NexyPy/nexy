"""Starting the project's Vite and waiting until it answers."""

from __future__ import annotations

import socket
import subprocess  # nosec B404
import time
from subprocess import Popen  # nosec B404 - type only, no invocation
from typing import Any

from nexy.helpers.common.vite_launch import vite_argv
from nexy.helpers.server.markers import write_port_file


def _streams(suppress_output: bool, capture_stderr: bool) -> tuple[int | None, int | None]:
    """(stdout, stderr) of the child: swallowed, piped back to the caller, or shown."""
    if capture_stderr:
        return (subprocess.DEVNULL if suppress_output else subprocess.PIPE), subprocess.PIPE
    if suppress_output:
        return subprocess.DEVNULL, subprocess.DEVNULL
    return None, subprocess.STDOUT


def launch_vite(
    port: int = 5173,
    build: bool = False,
    suppress_output: bool | None = None,
    capture_stderr: bool = False,
) -> Popen[Any]:
    """Start the project's Vite, as a build or as the dev server on *port*."""
    quiet = build if suppress_output is None else suppress_output
    args = vite_argv(build, port)
    if not build:
        write_port_file("client", port)
    stdout, stderr = _streams(quiet, capture_stderr)
    return subprocess.Popen(args, stdout=stdout, stderr=stderr)  # nosec B603 - fixed argv


def wait_for_vite_ready(
    port: int,
    host: str = "localhost",
    timeout: float = 30,
    process: Popen[Any] | None = None,
) -> bool:
    """Wait until the Vite dev server accepts connections.

    The probe is a TCP connect, not an HTTP request: it only reports that the port is open, which
    is what readiness means here. When *process* is given, an early exit is a failure instead of
    a wait for a server that will never listen.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process is not None and process.poll() is not None:
            return False
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False
