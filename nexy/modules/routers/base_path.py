"""Serve the whole application under the public prefix declared by `useBasePath` (#468)."""

from starlette.types import ASGIApp, Receive, Scope, Send

from nexy.core.config import Config


def normalize_base_path(value: str | None) -> str:
    """Return a prefix like ``/app``, or ``''`` when the application lives at the root."""
    parts = [part for part in (value or "").split("/") if part]
    return "/" + "/".join(parts) if parts else ""


def public_url(path: str) -> str:
    """Prefix a root-relative URL that the browser will request."""
    base = normalize_base_path(Config().useBasePath)
    return base + path if path.startswith("/") else path


class BasePathMiddleware:
    """Strip the public prefix at the ASGI edge, so internal paths stay root-relative.

    Only ``scope["path"]`` changes: leaving ``root_path`` empty keeps the fast path,
    Starlette mounts and slash redirects working. Requests outside the prefix never
    reach the application.
    """

    def __init__(self, app: ASGIApp, base_path: str) -> None:
        self.app = app
        self.base = base_path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        base = self.base
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return
        path = scope["path"]
        if path == base:
            path = "/"
        elif not path.startswith(base + "/"):
            await _reject(scope, send)
            return
        else:
            path = path[len(base) :]
        inner = dict(scope, path=path)
        if "raw_path" in inner:
            inner["raw_path"] = inner["raw_path"][len(base.encode()) :] or b"/"
        await self.app(inner, receive, send)


async def _reject(scope: Scope, send: Send) -> None:
    """Answer a request or a socket that lives outside the prefix."""
    if scope["type"] == "websocket":
        await send({"type": "websocket.close", "code": 1008})
        return
    await send(
        {
            "type": "http.response.start",
            "status": 404,
            "headers": [(b"content-type", b"text/plain; charset=utf-8")],
        }
    )
    await send({"type": "http.response.body", "body": b"Not Found"})
