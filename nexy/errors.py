from __future__ import annotations

from dataclasses import dataclass

from fastapi import Response


@dataclass(frozen=True)
class NexyCompileError(Exception):
    """Compilation failure for a single route file, as Raised by the compiler.

    Attributes:
        source_path: Path of the file that failed to compile.
        message: Human-readable failure reason.
        line: 1-based source line when the parser could locate it.
        column: 1-based source column when the parser could locate it.
    """

    source_path: str
    message: str
    line: int | None = None
    column: int | None = None

    def __str__(self) -> str:
        loc = ""
        if self.line is not None:
            col = self.column if self.column is not None else 0
            loc = f":{self.line}:{col}"
        return f"{self.source_path}{loc} - {self.message}"


_STYLES = """\
<style>
*{padding:0;margin:0;box-sizing:border-box}
body{height:100vh;display:flex;justify-content:center;align-items:center;font-family:sans-serif;overflow:hidden}
.code{font-size:6rem;font-weight:bold;border-right:1px solid;padding-right:10px;margin-left:4rem}
.info{padding:1rem}
.info h2{margin:0}
.info p{width:14rem;margin-top:.5rem}
</style>"""


def _page_404() -> str:
    return f"""\
{_STYLES}<body style="background-color:yellow">
<h2 class="code" style="color:red;border-color:red">404</h2>
<div class="info">
<h2 style="color:red">Not Found</h2>
<p>Nexy did not find the requested resource.</p>
</div>
</body>"""


def _page_500() -> str:
    return f"""\
{_STYLES}<body style="background-color:red;gap:1rem;text-align:center;color:white">
<h2 class="code" style="color:red;border-color:red;font-size:3rem;margin:0">500</h2>
Internal Server Error
</body>"""


def NotFound() -> Response:
    """Build the styled 404 HTML error response.

    Returns:
        A FastAPI Response with status 404 and the Nexy 404 page.
    """
    return Response(content=_page_404(), status_code=404)


def InternalServerError() -> Response:
    """Build the styled 500 HTML error response.

    Returns:
        A FastAPI Response with status 500 and the Nexy 500 page.
    """
    return Response(content=_page_500(), status_code=500)
