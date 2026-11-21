"""The same form without JavaScript: the browser posts it here, and goes back to the form."""

from urllib.parse import parse_qs

from nexy.http import RedirectResponse, Request

from src.services.waitlist import join

LONGEST_BODY = 2048  # an email and its field name, with room to spare


async def read_form(request: Request) -> dict[str, list[str]]:
    """The fields of an urlencoded body; a body longer than the form can send is cut."""
    body = b""
    async for chunk in request.stream():
        body += chunk
        if len(body) > LONGEST_BODY:
            break
    return parse_qs(body[:LONGEST_BODY].decode("utf-8", "replace"))


async def POST(request: Request) -> RedirectResponse:
    email = (await read_form(request)).get("email", [""])[0]
    return RedirectResponse(f"/?waitlist={join(email)}#join", status_code=303)
