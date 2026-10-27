from nexy.http import RedirectResponse


async def GET() -> RedirectResponse:
    return RedirectResponse("/docs")
