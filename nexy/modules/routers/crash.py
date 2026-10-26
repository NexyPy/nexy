"""What the server does when a request raises: say what happened, once, and answer the client.

In development the answer is a page with the error, where it happened and the code around it, as
the dev overlays of Next.js and Django do. In production it is the plain error page, or JSON for
an API client, with a reference that matches the line in the server log: nothing about the
code or the exception reaches the visitor.
"""

from __future__ import annotations

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
from nexy.helpers.common.code_frame import print_frame, rows_of_file
from nexy.helpers.common.console import console
from nexy.helpers.common.pycheck import project_path
from nexy.helpers.server.devtools.state import record_error
from nexy.helpers.server.proxy import DEV_ENV_VAR
from nexy.helpers.server.security_headers import DEFAULT_HEADERS


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


def _frame(entry: traceback.FrameSummary, root: Path) -> Frame:
    inside = project_path(entry.filename, root)
    code = rows_of_file(entry.filename, entry.lineno or 0) if inside else ()
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
        console.print()
        print_frame(crash.origin.code, crash.origin.line)
        console.print()


def _rows(frame: Frame) -> str:
    return "".join(
        f'<div class="row{" hit" if number == frame.line else ""}">'
        f"<i>{number}</i><code>{escape(text) or '&nbsp;'}</code></div>"
        for number, text in frame.code
    )


def _frame_html(frame: Frame) -> str:
    title = f"{escape(frame.location)}:{frame.line} <b>{escape(frame.function)}</b>"
    return f'<section><h3>{title}</h3><div class="code">{_rows(frame)}</div></section>'


# The look of the Next.js error overlay: the error in a dialog over a dimmed page.
_STYLE = (
    "*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;"
    "padding:16px;background:#050505;color:#ededed;font:14px/1.5 system-ui,sans-serif}"
    ".dialog{width:min(860px,100%);border-radius:12px;background:#0a0a0a;border:1px solid #2e2e2e;"
    "border-top:3px solid #ff5c5c;overflow:hidden}"
    "header{display:flex;align-items:center;gap:10px;padding:14px 18px;color:#a1a1a1}"
    ".pill{padding:2px 8px;border-radius:999px;background:#3a1414;color:#ff9a9a;font-size:12px;"
    "font-weight:600}.spacer{flex:1}"
    "h1{margin:0;padding:0 18px 4px;font-size:20px;line-height:1.3;word-break:break-word}"
    ".where{padding:0 18px 14px;color:#a1a1a1}"
    "h3{margin:0;padding:10px 18px;border-top:1px solid #2e2e2e;font:500 12px ui-monospace,"
    "monospace;color:#cfcfcf}h3 b{color:#8a8a8a}"
    ".code{background:#111;overflow:auto;font:12px/1.6 ui-monospace,monospace;padding:6px 0}"
    ".row{display:flex;white-space:pre}.row i{width:3.5rem;padding-right:.8rem;text-align:right;"
    "color:#6b6b6b;flex:none}.hit{background:#2a1414;color:#ff9a9a}"
    "details{border-top:1px solid #2e2e2e}summary{cursor:pointer;padding:10px 18px;color:#a1a1a1}"
    "pre{margin:0;padding:0 18px 14px;white-space:pre-wrap;font:12px/1.6 ui-monospace,monospace;"
    "color:#9a9a9a}footer{padding:10px 18px;border-top:1px solid #2e2e2e;color:#8a8a8a;"
    "font-size:12px}"
)


def debug_page(request: Request, crash: Crash) -> Response:
    """The development page for a crash: error, where, project code, then the raw traceback."""
    own = (frame for frame in reversed(crash.frames) if frame.in_project)
    frames = "".join(_frame_html(frame) for frame in own)
    where = f"{escape(request.method)} {escape(request.url.path)}"
    body = (
        f"<!DOCTYPE html><html lang=en><meta charset=utf-8><title>{escape(crash.kind)}</title>"
        f"<style>{_STYLE}</style><div class=dialog><header><span class=pill>Server Error</span>"
        f"<span>500</span><span class=spacer></span><span>ref {crash.reference}</span></header>"
        f"<h1>{escape(crash.kind)}: {escape(crash.message)}</h1><div class=where>{where}</div>"
        f"{frames}<details><summary>Full traceback</summary><pre>{escape(crash.text)}</pre>"
        "</details><footer>Shown by nexy dev only. Visitors see a plain error page in production."
        "</footer></div>"
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
        if is_dev():
            where = f"{request.method} {request.url.path}"
            record_error(crash.kind, crash.message, where, crash.reference)
        return crash_response(request, crash)
    except Exception:
        console.print(f"  [red]x[/red] {markup(type(error).__name__)}: {markup(str(error))}")
        return InternalServerError()
