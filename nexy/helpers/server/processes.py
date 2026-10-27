"""Stopping a child process, the same way on Windows and Unix."""

from __future__ import annotations

import contextlib
import shutil
import subprocess  # nosec B404
import sys
from subprocess import Popen  # nosec B404 - type only, no invocation
from typing import Any


def _kill_tree_windows(process: Popen[Any], timeout: int) -> None:
    """`taskkill /T` ends the process and the children it started (Vite starts some)."""
    taskkill = shutil.which("taskkill") or "taskkill"
    subprocess.run(
        [taskkill, "/F", "/T", "/PID", str(process.pid)],
        capture_output=True,
        timeout=timeout,
        check=False,
    )  # nosec B603/B607 - resolved via shutil.which, fixed argv with process.pid


def _terminate_unix(process: Popen[Any], timeout: int) -> None:
    """Ask politely, then insist."""
    process.terminate()
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=timeout)


def stop_process(process: Popen[Any] | None, timeout: int = 5) -> None:
    """Stop *process* if it is still running; a failure to stop it is not the caller's problem."""
    if not process or process.poll() is not None:
        return
    stop = _kill_tree_windows if sys.platform == "win32" else _terminate_unix
    # Best-effort teardown: the caller proceeds either way.
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        stop(process, timeout)
