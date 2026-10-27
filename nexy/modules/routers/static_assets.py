import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"'
    ' stroke-width="1.5" stroke="currentColor">'
    '<path stroke-linecap="round" stroke-linejoin="round"'
    ' d="M7.864 4.243A7.5 7.5 0 0 1 19.5 10.5c0 2.92-.556 5.709-1.568 8.268'
    "M5.742 6.364A7.465 7.465 0 0 0 4.5 10.5a7.464 7.464 0 0 1-1.15 3.993"
    "m1.989 3.559A11.209 11.209 0 0 0 8.25 10.5a3.75 3.75 0 1 1 7.5 0c0 .527-.021 1.049-.064 1.565"
    'M12 10.5a14.94 14.94 0 0 1-3.6 9.75m6.633-4.596a18.666 18.666 0 0 1-2.485 5.33"'
    " /></svg>"
)


class PublicFilesMiddleware:
    """Serve `public/<file>` at `/<file>`, the way Vite and Next.js do.

    Vite serves `public/` at the root in development; this brings production to the same URLs, so
    a page that writes `/logo.svg` works in both. Only GET and HEAD requests whose last segment has
    an extension are looked up, so pages and API routes pay nothing. Dot files are never served.
    """

    def __init__(self, app: Any, directory: str | Path = "public") -> None:
        self.app = app
        self.root = Path(directory).resolve()

    def _file_for(self, path: str) -> Path | None:
        relative = path.lstrip("/")
        parts = relative.split("/")
        if "." not in parts[-1] or any(part.startswith(".") for part in parts):
            return None
        candidate = (self.root / relative).resolve()
        if candidate.is_file() and candidate.is_relative_to(self.root):
            return candidate
        return None

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] == "http" and scope["method"] in ("GET", "HEAD"):
            file = self._file_for(scope["path"])
            if file is not None:
                await FileResponse(file)(scope, receive, send)
                return
        await self.app(scope, receive, send)


def setup_static_files(server: FastAPI) -> None:
    """Mounts directories if they exist."""
    mounts = {"/public": "public", "/assets": "__nexy__/client/assets"}
    for path, directory in mounts.items():
        if os.path.isdir(directory):
            server.mount(path, StaticFiles(directory=directory), name=directory)
    if os.path.isdir("public"):
        server.add_middleware(PublicFilesMiddleware, directory="public")


def setup_favicon(server: FastAPI, router_path: str) -> None:
    """Serve /favicon.ico from the router folder, public/ or the built-in SVG.

    The handler is synchronous on purpose: FastAPI runs it in a worker thread, so reading the file
    never blocks the event loop.
    """
    candidates = (Path(router_path) / "favicon.ico", Path("public") / "favicon.ico")

    @server.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        for candidate in candidates:
            try:
                return Response(content=candidate.read_bytes(), media_type="image/x-icon")
            except OSError:
                continue
        return Response(content=FAVICON_SVG.encode("utf-8"), media_type="image/svg+xml")
