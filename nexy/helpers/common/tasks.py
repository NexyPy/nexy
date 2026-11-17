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

from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.text import Text

from nexy.helpers.common.console import console as _console
from nexy.helpers.common.messages import error, took

_TAIL_LINES = 15
_BAR_WIDTH = 20
_REFRESH = 12


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


# uv's own spinner: the ten braille frames it gives indicatif, one every 200 ms.
_FRAMES = "\u280b\u2819\u2839\u2838\u283c\u2834\u2826\u2827\u2807\u280f"
_FRAME_SECONDS = 0.2


def _bar(done: int, total: int) -> str:
    """uv's 20-cell bar: full cells for the finished steps, light ones for the rest."""
    full = _BAR_WIDTH * done // total if total else 0
    return "\u2588" * full + "\u2591" * (_BAR_WIDTH - full)


class _LiveLine:
    """The row shown while a task runs, erased when it ends, drawn as uv draws its progress.

    A lone task is ``{spinner:.white} {wide_msg:.dim}``: a white spinner, then the label and the
    last line the command printed, dim. A step of a group (``progress=(2, 5)``) is
    ``{bar:20} [{pos}/{len}] {wide_msg:.dim}``, the bar and count that uv shows for the packages
    it installs.
    """

    def __init__(self, label: str, progress: tuple[int, int] | None = None) -> None:
        self.label = label
        self.progress = progress
        self.last = ""
        self.started = time.monotonic()

    def __rich_console__(self, _console: Console, options: ConsoleOptions) -> RenderResult:
        row = self._head()
        row.append(self.label + (f"  {self.last}" if self.last else ""), style="dim")
        row.truncate(options.max_width, overflow="crop")
        yield row

    def _head(self) -> Text:
        if self.progress is None:
            frame = int((time.monotonic() - self.started) / _FRAME_SECONDS) % len(_FRAMES)
            return Text.assemble((_FRAMES[frame], "white"), " ", no_wrap=True)
        done, total = self.progress
        return Text(f"{_bar(done, total)} [{done}/{total}] ", no_wrap=True)


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
    # Not a terminal: nothing is drawn, so only the result line is written, as uv does.
    with _showing(live, out):
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
    """The one line a task leaves behind; a failure also keeps its output, dim when cut short."""
    if proc.returncode == 0:
        out.print(took(done or label, format_duration(seconds)))
        return
    error(label, f"exit {proc.returncode} after {format_duration(seconds)}", console=out)
    style = "dim" if tail.maxlen else "none"
    for line in tail:
        out.print(f"  [{style}]{_escape(line)}[/{style}]")


def run_task(
    label: str,
    argv: Sequence[str],
    *,
    cwd: Path | str | None = None,
    done: str | None = None,
    progress: tuple[int, int] | None = None,
    console: Console | None = None,
    full_output: bool = False,
) -> TaskResult:
    """Run *argv* while showing progress; print one result line when it ends.

    *done* replaces *label* on the success line (``"Installed zod"``). *progress* is the position
    of this task in a group, ``(finished, total)``, drawn as a bar next to the spinner. A failure
    keeps the last lines of the output, or with *full_output* every line (a type checker's report).
    """
    out = console or _console
    tail: deque[str] = deque(maxlen=None if full_output else _TAIL_LINES)
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
def _showing(live: _LiveLine, out: Console) -> Generator[None]:
    """Draw *live* until the block ends, then erase it; outside a terminal, draw nothing."""
    if not out.is_terminal:
        yield
        return
    with Live(live, console=out, refresh_per_second=_REFRESH, transient=True):
        yield


@contextmanager
def step(label: str, *, done: str | None = None, console: Console | None = None) -> Generator[None]:
    """In-process ``run_task``: a spinner while the block runs, then one result line."""
    out = console or _console
    started = time.monotonic()
    try:
        with _showing(_LiveLine(label), out):
            yield
    except BaseException:
        error(label, console=out)
        raise
    out.print(took(done or label, format_duration(time.monotonic() - started)))
