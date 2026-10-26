from __future__ import annotations

from dataclasses import dataclass
from html import escape

from fastapi import Response
from fastapi.responses import HTMLResponse


@dataclass(frozen=True)
class NexyCompileError(Exception):
    """Compilation failure for a single route file, as Raised by the compiler.

    Attributes:
        source_path: Path of the file that failed to compile.
        message: Human-readable failure reason.
        line: 1-based source line when the parser could locate it.
        column: 1-based source column when the parser could locate it.
        hint: Concrete remediation step, when the compiler knows one.
    """

    source_path: str
    message: str
    line: int | None = None
    column: int | None = None
    hint: str | None = None

    def __str__(self) -> str:
        loc = ""
        if self.line is not None:
            col = self.column if self.column is not None else 0
            loc = f":{self.line}:{col}"
        base = f"{self.source_path}{loc} - {self.message}"
        return f"{base}\n  Fix: {self.hint}" if self.hint else base


_PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{code} - {title}</title>
<style>
:root{{color-scheme:light dark;--bg:#fff;--fg:#0b1a24;--muted:#5b6b78;--line:#d3d9de}}
@media (prefers-color-scheme: dark){{:root{{\
--bg:#0b1418;--fg:#eef3f6;--muted:#8da0ac;--line:#2a373f}}}}
*{{box-sizing:border-box;margin:0}}
body{{min-height:100dvh;display:grid;place-items:center;padding:1.5rem;background:var(--bg);\
color:var(--fg);font:16px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{width:min(28rem,100%);text-align:center}}
.code{{display:inline-block;padding:.4rem .8rem;border:1px dashed var(--line);border-radius:999px;\
font:600 .75rem/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.18em;\
color:var(--muted)}}
h1{{margin:1.25rem 0 .5rem;font-size:clamp(1.75rem,5vw,2.25rem);\
letter-spacing:-.03em;line-height:1.15}}
p{{color:var(--muted)}}
.ref{{margin-top:.75rem;font:.75rem ui-monospace,monospace}}
a{{display:inline-block;margin-top:1.75rem;padding:.55rem 1.1rem;border-radius:999px;\
background:var(--fg);color:var(--bg);font-size:.9rem;font-weight:500;text-decoration:none}}
a:hover{{opacity:.85}}
</style>
</head>
<body>
<main>
<span class="code">{code}</span>
<h1>{title}</h1>
<p>{message}</p>
{reference}<a href="/">Back to home</a>
</main>
</body>
</html>
"""


def error_page(
    status_code: int, title: str, message: str, reference: str | None = None
) -> Response:
    """Build the HTML page for an error status.

    The page is self-contained (no font, script or stylesheet to fetch) because it is shown when
    the application itself may be broken, and it follows the visitor's light or dark theme.
    Everything interpolated is escaped.

    Args:
        status_code: HTTP status of the response, also shown on the page.
        title: Short headline, for example ``Page not found``.
        message: One sentence telling the visitor what to do next.
        reference: Identifier of the error, the same as in the server log.

    Returns:
        An HTML response with the given status.
    """
    ref = f'<p class="ref">Reference: {escape(reference)}</p>' if reference else ""
    body = _PAGE.format(
        code=status_code, title=escape(title), message=escape(message), reference=ref
    )
    return HTMLResponse(content=body, status_code=status_code)


def NotFound() -> Response:
    """Build the styled 404 HTML error response.

    Returns:
        A FastAPI Response with status 404 and the Nexy 404 page.
    """
    return error_page(
        404, "Page not found", "The page you are looking for does not exist or was moved."
    )


def InternalServerError(reference: str | None = None) -> Response:
    """Build the styled 500 HTML error response.

    Returns:
        A FastAPI Response with status 500 and the Nexy 500 page.
    """
    return error_page(
        500,
        "Something went wrong",
        "The server hit an unexpected problem. Try again in a moment.",
        reference,
    )
