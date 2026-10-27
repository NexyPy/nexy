"""The HTML document of a client-routed route whose root ``layout.tsx`` owns ``<html>``.

The document is rendered by Node, never by Python:

* development: the running Vite dev server renders it on demand (``/__nexy__/render``);
* production: ``nx build`` pre-renders it to ``__nexy__/client/static`` (``.document.html`` for a
  static route, ``.shell.html`` - the layouts around an empty page - for a dynamic one).

Whatever the source, Nexy injects the client assets before ``</head>`` and a JSON description of the
page before ``</body>``. The browser reads it to hydrate the same React tree.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.server.proxy import vite_proxy_port
from nexy.hooks import _get_req as _get_request
from nexy.vite import Vite

_STATIC_ROOT = "__nexy__/client/static"
_RENDER_TIMEOUT = 15.0


def _json_for_script(value: Any) -> str:
    """JSON that is safe inside ``<script type="application/json">``."""
    text = json.dumps(value, default=str, separators=(",", ":"))
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def _inject(document: str, head: str, body: str) -> str:
    lowered = document.lower()
    index = lowered.rfind("</head>")
    if index != -1:
        document = document[:index] + head + document[index:]
    lowered = document.lower()
    index = lowered.rfind("</body>")
    if index != -1:
        return document[:index] + body + document[index:]
    return document + body


def _is_document(html: str) -> bool:
    return "<html" in html[:2000].lower()


def _fallback_document() -> str:
    """Empty document used when no pre-rendered HTML is available: the browser renders it all."""
    return (
        '<!DOCTYPE html><html lang="en"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        "</head><body></body></html>"
    )


def _from_production(static_stem: str, dynamic: bool) -> str | None:
    suffix = "shell" if dynamic else "document"
    path = Path(f"{_STATIC_ROOT}{static_stem}.{suffix}.html")
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _request_location() -> dict[str, str] | None:
    """The path and query of the request being answered, or None outside a request."""
    try:
        url = _get_request().url
    except RuntimeError:
        return None
    return {"pathname": url.path, "search": f"?{url.query}" if url.query else ""}


def _from_vite(page_file: str, layouts: list[str], props: dict[str, Any], port: int) -> str | None:
    # The props go in the body: they can be large, and a URL has a hard length limit.
    body: dict[str, Any] = {
        "page": page_file,
        "layouts": layouts,
        "props": json.loads(json.dumps(props, default=str)),
    }
    if location := _request_location():
        body["location"] = location
    try:
        response = httpx.post(
            f"http://127.0.0.1:{port}/__nexy__/render", json=body, timeout=_RENDER_TIMEOUT
        )
    except httpx.HTTPError as error:
        console.print(tagged("nexy", f"document render unavailable: {error}", "yellow"))
        return None
    if response.status_code != 200:
        failure = f"rendering {page_file} failed:\n{response.text[:2000]}"
        console.print(tagged("nexy", failure, "red"))
        return None
    return response.text


def render_document(
    *,
    page_file: str,
    page_key: str,
    layouts: list[str],
    layout_keys: list[str],
    props: dict[str, Any],
    static_stem: str,
    dynamic: bool,
) -> str:
    """Return the full HTML document for one client route."""
    html: str | None
    mode = "document"
    if Path("__nexy__/nexy.prod").is_file():
        html = _from_production(static_stem, dynamic)
        mode = "shell" if dynamic else "document"
    else:
        port = vite_proxy_port()
        html = _from_vite(page_file, layouts, props, port) if port else None

    if html is None or not _is_document(html):
        html, mode = _fallback_document(), "client"

    boot = {"mode": mode, "page": page_key, "layouts": layout_keys, "props": props}
    return _inject(
        html,
        head=Vite(),
        body=f'<script id="__nexy_page" type="application/json">{_json_for_script(boot)}</script>',
    )
