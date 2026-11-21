"""The chat opens on the general room."""

from nexy.http import RedirectResponse


def GET() -> RedirectResponse:
    return RedirectResponse("/rooms/general", status_code=307)
