"""What the server does when a request raises: say what happened, once, and answer the client.

In development the answer is a page with the error, where it happened and the code around it, as
the dev overlays of Next.js and Django do. In production it is the plain error page, or JSON for
an API client, with a reference that matches the line in the server log: nothing about the
code or the exception reaches the visitor.
"""

from __future__ import annotations

import linecache
import os
import secrets
import traceback
from dataclasses import dataclass
from html import escape
from pathlib import Path

from fastapi.responses import JSONResponse
from rich.markup import escape as markup
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

from nexy.errors import InternalServerError
from nexy.helpers.common.console import console
from nexy.helpers.common.pycheck import project_path
from nexy.helpers.server.proxy import DEV_ENV_VAR
from nexy.helpers.server.security_headers import DEFAULT_HEADERS

_CONTEXT = 3


@dataclass(frozen=True)
class Frame:
    """One call of the traceback; ``code`` holds the lines around it for a project file."""

    location: str
    function: str
    line: int
    code: tuple[tuple[int, str], ...] = ()

    @property
    def in_project(self) -> bool:
        return bool(self.code)


@dataclass(frozen=True)
class Crash:
    """An unhandled exception, as the log and the dev page show it."""

    reference: str
    kind: str
    message: str
    frames: tuple[Frame, ...]
    text: str

    @property
    def origin(self) -> Frame | None:
        """The innermost call that is the project's own code."""
        return next((frame for frame in reversed(self.frames) if frame.in_project), None)


def is_dev() -> bool:
    return os.environ.get(DEV_ENV_VAR) == "1"


def _context(filename: str, line: int) -> tuple[tuple[int, str], ...]:
    lines = linecache.getlines(filename)
    first, last = max(1, line - _CONTEXT), min(len(lines), line + _CONTEXT)
    return tuple((number, lines[number - 1].rstrip("\n")) for number in range(first, last + 1))


def _frame(entry: traceback.FrameSummary, root: Path) -> Frame:
    inside = project_path(entry.filename, root)
    code = _context(entry.filename, entry.lineno or 0) if inside else ()
    return Frame(inside or entry.filename, entry.name, entry.lineno or 0, code)


def inspect_crash(error: BaseException, root: Path | None = None) -> Crash:
    """Read an exception into a `Crash`; the traceback text is kept for the production log."""
    root = root or Path.cwd()
    frames = tuple(_frame(entry, root) for entry in traceback.extract_tb(error.__traceback__))
    text = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    return Crash(secrets.token_hex(4), type(error).__name__, str(error), frames, text)


def log_crash(request: Request, crash: Crash, dev: bool | None = None) -> None:
    """Print the crash: its own frames in development, the whole traceback otherwise."""
    dev = is_dev() if dev is None else dev
    where = f"{request.method} {request.url.path}"
    head = f"  [red]x[/red] [bold]{markup(crash.kind)}[/bold]: {markup(crash.message)}"
    console.print(f"{head}  [dim]{markup(where)}  ref {crash.reference}[/dim]")
    if not dev:
        console.print(crash.text.rstrip(), markup=False, highlight=False, soft_wrap=True)
        return
    for frame in (item for item in crash.frames if item.in_project):
        console.print(
            f"    [dim]at {markup(frame.location)}:{frame.line} in {frame.function}[/dim]"
        )
    if crash.origin:
        _print_code(crash.origin)


def _print_code(frame: Frame) -> None:
    for number, text in frame.code:
        colour = "red" if number == frame.line else "dim"
        console.print(f"    [{colour}]{number:>4} | {markup(text)}[/{colour}]")


def _rows(frame: Frame) -> str:
    return "".join(
        f'<div class="row{" hit" if number == frame.line else ""}">'
        f"<i>{number}</i><code>{escape(text) or '&nbsp;'}</code></div>"
        for number, text in frame.code
    )


def _frame_html(frame: Frame) -> str:
    title = f"{escape(frame.location)}:{frame.line} <b>{escape(frame.function)}</b>"
    return f'<section><h3>{title}</h3><div class="code">{_rows(frame)}</div></section>'


_STYLE = (
    ":root{color-scheme:light dark;--bg:#fff;--fg:#111;--muted:#666;--line:#ddd;--bad:#c62828;"
    "--hit:#fdecea}@media(prefers-color-scheme:dark){:root{--bg:#0a0a0a;--fg:#ededed;"
    "--muted:#9a9a9a;--line:#2a2a2a;--bad:#ff6b6b;--hit:#2a1414}}"
    "*{box-sizing:border-box}body{margin:0;padding:2rem 1rem;background:var(--bg);color:var(--fg);"
    "font:15px/1.5 ui-sans-serif,system-ui,sans-serif}main{max-width:56rem;margin:auto}"
    "h1{font-size:1.4rem;margin:.2rem 0;color:var(--bad)}p{color:var(--muted);margin:.2rem 0}"
    "h3{font:500 .85rem ui-monospace,monospace;margin:1.2rem 0 .4rem}h3 b{color:var(--muted)}"
    ".code{border:1px solid var(--line);border-radius:6px;overflow:auto;"
    "font:.8rem/1.6 ui-monospace,monospace}.row{display:flex;white-space:pre}"
    ".row i{width:3.5rem;padding-right:.8rem;text-align:right;color:var(--muted);flex:none}"
    ".hit{background:var(--hit);color:var(--bad)}"
    "pre{white-space:pre-wrap;font-size:.75rem;color:var(--muted)}summary{cursor:pointer}"
)


def debug_page(request: Request, crash: Crash) -> Response:
    """The development page for a crash: error, request, project code, then the raw traceback."""
    own = (frame for frame in reversed(crash.frames) if frame.in_project)
    frames = "".join(_frame_html(frame) for frame in own)
    body = (
        f"<!DOCTYPE html><html lang=en><meta charset=utf-8><title>{escape(crash.kind)}</title>"
        f"<style>{_STYLE}</style><main><p>500 &middot; {escape(request.method)} "
        f"{escape(request.url.path)} &middot; ref {crash.reference}</p>"
        f"<h1>{escape(crash.kind)}: {escape(crash.message)}</h1>{frames}"
        f"<details><summary>Full traceback</summary><pre>{escape(crash.text)}</pre></details>"
        "<p>Shown in development only. In production visitors see a plain error page.</p></main>"
    )
    return HTMLResponse(body, status_code=500)


def _wants_json(request: Request) -> bool:
    accept = request.headers.get("accept", "").lower()
    return "application/json" in accept and "text/html" not in accept


def _json_answer(crash: Crash, dev: bool) -> Response:
    body: dict[str, object] = {"detail": "Internal Server Error", "reference": crash.reference}
    if dev:
        body["error"] = f"{crash.kind}: {crash.message}"
    return JSONResponse(body, status_code=500)


def crash_response(request: Request, crash: Crash, dev: bool | None = None) -> Response:
    """The answer for a crash: JSON for an API client, else the page that fits the mode."""
    dev = is_dev() if dev is None else dev
    if _wants_json(request):
        response = _json_answer(crash, dev)
    elif dev:
        response = debug_page(request, crash)
    else:
        response = InternalServerError(reference=crash.reference)
    if not dev:
        # The error middleware answers outside the application's own: it adds these itself.
        for name, value in DEFAULT_HEADERS.items():
            response.headers.setdefault(name, value)
    return response


async def handle_crash(request: Request, error: Exception) -> Response:
    """Starlette handler for any exception no route handled; it never raises itself."""
    try:
        crash = inspect_crash(error)
        log_crash(request, crash)
        return crash_response(request, crash)
    except Exception:
        console.print(f"  [red]x[/red] {markup(type(error).__name__)}: {markup(str(error))}")
        return InternalServerError()
