"""Long-running CLI steps with uv-style feedback.

``run_task`` shows a spinner with the elapsed time and the last line the command
printed, then leaves one permanent line behind: ``✔ label  1.2s``. A failure keeps
the command's output instead of hiding it.
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

_TAIL_LINES = 15
_LIVE_WIDTH = 78
_BAR_WIDTH = 20


def _symbols(out: Console) -> tuple[str, str, str]:
    """(ok, fail, pending) marks; ASCII when the console cannot encode Unicode."""
    if (out.encoding or "").lower().startswith("utf"):
        return "✔", "✘", "…"
    return "+", "x", "..."


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
    """One spinner row: label, a bar, elapsed time, dim last output line.

    The bar counts the finished steps of a group (``progress=(2, 5)``). A lone step has no count
    to show, so its bar only pulses to say it is alive.
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
        row.add_row(self._spinner, self._bar(), text)
        yield row

    def _bar(self) -> ProgressBar:
        if self.progress:
            done, total = self.progress
            return ProgressBar(total=total, completed=done, width=_BAR_WIDTH)
        pulse_time = time.monotonic() - self.started
        return ProgressBar(pulse=True, animation_time=pulse_time, width=_BAR_WIDTH)


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
    ok_mark, fail_mark, wait_mark = _symbols(out)
    tail: deque[str] = deque(maxlen=_TAIL_LINES)
    live = _LiveLine(label, progress)
    started = time.monotonic()

    try:
        proc = subprocess.Popen(  # nosec B603 - resolved executable, no shell
            _resolve(argv),
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        out.print(f"[red]{fail_mark}[/red] {label}  [dim]{exc}[/dim]")
        return TaskResult(ok=False, seconds=0.0, output=[str(exc)])

    if out.is_terminal:
        with Live(live, console=out, refresh_per_second=12, transient=True):
            _pump(proc, tail, live)
            proc.wait()
    else:
        out.print(f"[yellow]{wait_mark}[/yellow] {label}")
        _pump(proc, tail, live)
        proc.wait()

    seconds = time.monotonic() - started
    ok = proc.returncode == 0
    if ok:
        out.print(
            f"[green]{ok_mark}[/green] {done or label}  [dim]{format_duration(seconds)}[/dim]"
        )
    else:
        detail = f"exit {proc.returncode}, {format_duration(seconds)}"
        out.print(f"[red]{fail_mark}[/red] {label}  [dim]{detail}[/dim]")
        for line in tail:
            out.print(f"  [dim]{_escape(line)}[/dim]")
    return TaskResult(ok=ok, seconds=seconds, returncode=proc.returncode, output=list(tail))


def _escape(line: str) -> str:
    return line.replace("[", "\\[")


class Timer:
    """Total duration for a closing ``Done in 8.4s`` line."""

    def __init__(self) -> None:
        self.started = time.monotonic()

    def elapsed(self) -> float:
        return time.monotonic() - self.started

    def summary(self, text: str = "Done", console: Console | None = None) -> None:
        (console or _console).print(f"\n[bold]{text}[/bold] in {format_duration(self.elapsed())}")


@contextmanager
def step(label: str, *, done: str | None = None, console: Console | None = None) -> Generator[None]:
    """In-process ``run_task``: a spinner while the block runs, then one result line."""
    out = console or _console
    ok_mark, fail_mark, _ = _symbols(out)
    started = time.monotonic()
    try:
        with out.status(label, spinner="dots"):
            yield
    except BaseException:
        out.print(f"[red]{fail_mark}[/red] {label}")
        raise
    shown = format_duration(time.monotonic() - started)
    out.print(f"[green]{ok_mark}[/green] {done or label}  [dim]{shown}[/dim]")
