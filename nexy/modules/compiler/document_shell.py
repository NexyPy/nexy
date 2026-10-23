"""Minimal HTML document shell for client-routing projects.

With ``useCSR`` the framework owns the views, so a route may have no
``layout.*`` file. A bare component fragment is not a valid page: the browser
needs a document and the Vite tags. This shell fills that gap and is only used
when the user has not supplied a layout of their own.

The generated Python is written into compiled route modules, not imported here.
"""

CSR_SHELL_FUNCTION = "__nexy_shell"

CSR_SHELL_HEADER = (
    "from nexy.vite import Vite as __Vite\n"
    f"def {CSR_SHELL_FUNCTION}(children: str) -> str:\n"
    "    return (\n"
    "        '<!DOCTYPE html><html><head><meta charset=\"utf-8\">'\n"
    '        \'<meta name="viewport" content="width=device-width, initial-scale=1">\'\n'
    "        + __Vite()\n"
    "        + '</head><body>'\n"
    "        + children\n"
    "        + '</body></html>'\n"
    "    )\n"
)

CSR_SHELL_RENDER = f"{CSR_SHELL_FUNCTION}(rendered)"
