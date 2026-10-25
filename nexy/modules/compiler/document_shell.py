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
    "from nexy.modules.i18n.core import current_locale as __current_locale\n"
    f"def {CSR_SHELL_FUNCTION}(children: str) -> str:\n"
    "    if children.lstrip()[:15].lower().startswith(('<!doctype', '<html')):\n"
    "        return children\n"
    "    __locale = __current_locale.get()\n"
    "    return (\n"
    "        '<!DOCTYPE html><html lang=\"' + str(__locale) + '\"><head>'\n"
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
