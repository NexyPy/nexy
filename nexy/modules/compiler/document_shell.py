"""Fallback HTML document for views that have no ``layout.*`` ancestor.

Scaffolded projects always ship a root ``layout.nexy`` that owns the document
(``<!DOCTYPE html>``, ``<html>``, ``<head>``, ``<body>``), like Next.js' root
layout. This shell only exists for hand-written projects without one, and
mirrors that structure so the output is equally valid.
"""

from pathlib import Path

from nexy.core.config import Config

CSR_SHELL_FUNCTION = "__nexy_shell"


def is_route_file(source_path: str) -> bool:
    """True for files under the router directory; components must stay fragments."""
    routes = Path(Config.ROUTER_PATH).as_posix().strip("/")
    return f"/{routes}/" in f"/{Path(source_path).as_posix()}"


_THEME_SCRIPT = (
    "<script>document.documentElement.classList.toggle('dark',"
    "localStorage.getItem('nexy-theme')==='dark'||"
    "(!('nexy-theme' in localStorage)&&matchMedia('(prefers-color-scheme: dark)').matches))"
    "</script>"
)

CSR_SHELL_HEADER = (
    "from nexy.vite import Vite as __Vite\n"
    f"def {CSR_SHELL_FUNCTION}(children: str) -> str:\n"
    "    if children.lstrip()[:15].lower().startswith(('<!doctype', '<html')):\n"
    "        return children\n"
    "    return (\n"
    "        '<!DOCTYPE html><html lang=\"en\"><head>'\n"
    "        '<meta charset=\"utf-8\">'\n"
    '        \'<meta name="viewport" content="width=device-width, initial-scale=1">\'\n'
    f"        {_THEME_SCRIPT!r}\n"
    "        + __Vite()\n"
    "        + '</head><body>'\n"
    "        + children\n"
    "        + '</body></html>'\n"
    "    )\n"
)

CSR_SHELL_RENDER = f"{CSR_SHELL_FUNCTION}(rendered)"


LAYOUT_RENDER = "str(__Layout(children=rendered))"
_LAYOUT_IMPORT = (
    "try:\n"
    "    from {layout} import Layout as __Layout\n"
    "except ImportError:\n"
    "    def __Layout(children: str = '', **kwargs) -> str:\n"
    "        return '<div data-nexy-error=\"Layout not available\"></div>'\n"
)


def layout_parts(layout_import: str | None, *, fallback_shell: bool) -> tuple[str, str]:
    """(header, render expression) that wrap a view: its layout, else the shell, else nothing.

    A layout always wins. Without one the view gets the minimal document shell, unless it is a
    fragment (a component) that must stay one.
    """
    if layout_import:
        return _LAYOUT_IMPORT.format(layout=layout_import), LAYOUT_RENDER
    if fallback_shell:
        return CSR_SHELL_HEADER, CSR_SHELL_RENDER
    return "", "rendered"
