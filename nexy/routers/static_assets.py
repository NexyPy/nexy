import os

from fastapi import FastAPI, Response
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


def setup_static_files(server: FastAPI) -> None:
    """Mounts directories if they exist."""
    mounts = {"/public": "public", "/assets": "__nexy__/client/assets"}
    for path, directory in mounts.items():
        if os.path.isdir(directory):
            server.mount(path, StaticFiles(directory=directory), name=directory)


def setup_favicon(server: FastAPI, router_path: str) -> None:
    """Serve /favicon.ico from the router folder, public/ or the built-in SVG."""
    favicon_path = f"{router_path}/favicon.ico"

    @server.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> Response:
        try:
            favicon_data = FAVICON_SVG.encode("utf-8")
            if os.path.isfile(favicon_path):
                with open(favicon_path, "rb") as f:
                    favicon_data = f.read()
            else:
                with open("public/favicon.ico", "rb") as f:
                    favicon_data = f.read()
            return Response(content=favicon_data, media_type="image/x-icon")
        except FileNotFoundError:
            return Response(content=FAVICON_SVG.encode("utf-8"), media_type="image/x-icon")
