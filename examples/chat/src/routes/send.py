"""Where the message form posts. Without JavaScript the browser comes back to the room; the island
asks for JSON instead, with the messages it has not shown yet."""

from dataclasses import asdict
from urllib.parse import parse_qs, quote

from nexy.http import JSONResponse, RedirectResponse, Request, Response

from src.chat.store import NOTES, ROOMS, message_id, messages, send

LONGEST_BODY = 4096  # a room, a name, a message and the id of the last one, with room to spare
NAME_COOKIE = "chat_name"
A_YEAR = 365 * 24 * 3600


async def read_form(request: Request) -> dict[str, str]:
    """The fields of an urlencoded body, first value of each; a longer body is cut."""
    body = b""
    async for chunk in request.stream():
        body += chunk
        if len(body) > LONGEST_BODY:
            break
    fields = parse_qs(body[:LONGEST_BODY].decode("utf-8", "replace"))
    return {key: values[0] for key, values in fields.items()}


def _answer(request: Request, room: str, note: str, after: str) -> Response:
    if "application/json" in request.headers.get("accept", ""):
        last = message_id(after)
        newer = messages(room, last) if room in ROOMS and last is not None else []
        return JSONResponse({"note": NOTES.get(note, ""), "messages": [asdict(m) for m in newer]})
    room = room if room in ROOMS else "general"
    query = f"?note={quote(note)}" if note else ""
    return RedirectResponse(f"/rooms/{room}{query}#send", status_code=303)


async def POST(request: Request) -> Response:
    form = await read_form(request)
    room, name = form.get("room", ""), form.get("name", "")
    note = send(room, name, form.get("text", ""))
    answer = _answer(request, room, note, form.get("after", ""))
    if not note:  # the name is remembered once it has been used
        answer.set_cookie(NAME_COOKIE, name.strip(), max_age=A_YEAR, httponly=True, samesite="lax")
    return answer
