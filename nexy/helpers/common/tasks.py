"""Long-running CLI steps with uv-style feedback.

``run_task`` shows a spinner with the elapsed time and the last line the command
printed, then leaves one permanent line behind, as uv does: ``Installed zod in 1.2s``.
A failure is an ``error:`` line with its cause, and keeps the end of the command's
output instead of hiding it.
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
import time
from collections import deque
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console, RenderResult
from rich.live import Live
from rich.progress_bar import ProgressBar
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

from nexy.helpers.common.console import console as _console
from nexy.helpers.common.messages import error, took

_TAIL_LINES = 15
_LIVE_WIDTH = 78
_BAR_WIDTH = 20


def format_duration(seconds: float) -> str:
    """``42ms`` below a second, ``1.2s`` below a minute, ``1m 05s`` after."""
    if seconds < 1:
        return f"{round(seconds * 1000)}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, rest = divmod(round(seconds), 60)
    return f"{minutes}m {rest:02d}s"


@dataclass
class TaskResult:
    ok: bool
    seconds: float
    returncode: int | None = None
    output: list[str] = field(default_factory=list)


class _LiveLine:
    """One spinner row, erased when the task ends: label, elapsed time, dim last output line.

    A step of a group (``progress=(2, 5)``) also shows a bar and its count, as uv does for the
    packages it installs. A lone step has no count, so it shows the spinner alone.
    """

    def __init__(self, label: str, progress: tuple[int, int] | None = None) -> None:
        self.label = label
        self.progress = progress
        self.last = ""
        self.started = time.monotonic()
        self._spinner = Spinner("dots", style="yellow")

    def __rich_console__(self, *_: object) -> RenderResult:
        elapsed = format_duration(time.monotonic() - self.started)
        row = Table.grid(padding=(0, 1))
        row.add_column()
        row.add_column(no_wrap=True)
        row.add_column(no_wrap=True, overflow="ellipsis")
        text = Text.assemble(self.label, ("  " + elapsed, "dim"))
        if self.progress:
            text.append(f"  {self.progress[0]}/{self.progress[1]}", style="dim")
        if self.last:
            text.append("  " + self.last[:_LIVE_WIDTH], style="dim")
        if self.progress:
            done, total = self.progress
            row.add_row(self._spinner, ProgressBar(total, done, width=_BAR_WIDTH), text)
        else:
            row.add_row(self._spinner, text)
        yield row


def _resolve(argv: Sequence[str]) -> list[str]:
    # Resolve the executable (npm.cmd on Windows) instead of using shell=True.
    exe = shutil.which(argv[0]) or argv[0]
    return [exe, *argv[1:]]


def _pump(proc: subprocess.Popen[str], tail: deque[str], live: _LiveLine) -> None:
    assert proc.stdout is not None  # nosec B101 - Popen(stdout=PIPE) above
    for raw in proc.stdout:
        line = raw.rstrip()
        if line:
            tail.append(line)
            live.last = line.strip()


def _spawn(argv: Sequence[str], cwd: Path | str | None) -> subprocess.Popen[str]:
    return subprocess.Popen(  # nosec B603 - resolved executable, no shell
        _resolve(argv),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _follow(proc: subprocess.Popen[str], tail: deque[str], live: _LiveLine, out: Console) -> None:
    """Show the task until it ends: a live row on a terminal, nothing otherwise."""
    if out.is_terminal:
        with Live(live, console=out, refresh_per_second=12, transient=True):
            _pump(proc, tail, live)
            proc.wait()
        return
    # Not a terminal: nothing to animate, so only the result line is written, as uv does.
    _pump(proc, tail, live)
    proc.wait()


def _announce(
    out: Console,
    label: str,
    done: str | None,
    seconds: float,
    proc: subprocess.Popen[str],
    tail: deque[str],
) -> None:
    """The one line a task leaves behind; a failure also keeps the end of its output."""
    if proc.returncode == 0:
        out.print(took(done or label, format_duration(seconds)))
        return
    error(label, f"exit {proc.returncode} after {format_duration(seconds)}", console=out)
    for line in tail:
        out.print(f"  [dim]{_escape(line)}[/dim]")


def run_task(
    label: str,
    argv: Sequence[str],
    *,
    cwd: Path | str | None = None,
    done: str | None = None,
    progress: tuple[int, int] | None = None,
    console: Console | None = None,
) -> TaskResult:
    """Run *argv* while showing progress; print one result line when it ends.

    *done* replaces *label* on the success line (``"Installed zod"``). *progress* is the position
    of this task in a group, ``(finished, total)``, drawn as a bar next to the spinner.
    """
    out = console or _console
    tail: deque[str] = deque(maxlen=_TAIL_LINES)
    started = time.monotonic()
    try:
        proc = _spawn(argv, cwd)
    except OSError as exc:
        error(label, _escape(str(exc)), console=out)
        return TaskResult(ok=False, seconds=0.0, output=[str(exc)])
    _follow(proc, tail, _LiveLine(label, progress), out)
    seconds = time.monotonic() - started
    _announce(out, label, done, seconds, proc, tail)
    return TaskResult(
        ok=proc.returncode == 0, seconds=seconds, returncode=proc.returncode, output=list(tail)
    )


def _escape(line: str) -> str:
    return line.replace("[", "\\[")


@contextmanager
def step(label: str, *, done: str | None = None, console: Console | None = None) -> Generator[None]:
    """In-process ``run_task``: a spinner while the block runs, then one result line."""
    out = console or _console
    started = time.monotonic()
    try:
        with out.status(label, spinner="dots"):
            yield
    except BaseException:
        error(label, console=out)
        raise
    out.print(took(done or label, format_duration(time.monotonic() - started)))
