from starlette.requests import Request

from nexy.http import RedirectResponse
from src.content import home_link, preferred_language


async def GET(request: Request) -> RedirectResponse:
    """The root opens the docs in the first language the browser asks for that the site speaks."""
    lang = preferred_language(request.headers.get("accept-language", ""))
    return RedirectResponse(home_link(lang))
