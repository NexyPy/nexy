"""The messages of a room newer than the last one the page shows: what the island asks for."""

from dataclasses import asdict

from nexy.http import JSONResponse, Request

from src.chat.store import ROOMS, message_id, messages


def GET(request: Request) -> JSONResponse:
    room = request.query_params.get("room", "")
    after = message_id(request.query_params.get("after", "0"))
    if room not in ROOMS or after is None:
        return JSONResponse([], status_code=400)
    return JSONResponse([asdict(message) for message in messages(room, after)])
