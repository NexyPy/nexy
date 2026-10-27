from http import HTTPStatus

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from nexy.errors import InternalServerError, NotFound, error_page


def _phrase(code: int) -> str:
    try:
        return HTTPStatus(code).phrase
    except ValueError:
        return "Error"


def _wants_json(request: Request) -> bool:
    """True for clients that ask for JSON and not for a page (API clients, fetch with headers)."""
    accept = request.headers.get("accept", "").lower()
    return "application/json" in accept and "text/html" not in accept


def handle_http_exception(request: Request, exc: HTTPException) -> Response:
    """Map HTTP exceptions to JSON for API clients, else to Nexy error pages."""
    headers = getattr(exc, "headers", None)
    if _wants_json(request):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=headers)
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return NotFound()
    if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        return InternalServerError()
    # The detail may carry user input, e.g. HTTPException(detail=f"No user {name}"): it is escaped.
    page = error_page(exc.status_code, _phrase(exc.status_code), str(exc.detail))
    page.headers.update(headers or {})
    return page


def register_validation_error_handler(server: FastAPI) -> None:
    """Convert path-param validation failures into 404s.

    A dynamic route like /{id} captures any unknown path; when the segment
    fails type validation (int("nonexistent")) FastAPI returns 422. From
    the caller's perspective the URL simply does not exist, so we surface
    it as 404 instead.
    """

    @server.exception_handler(RequestValidationError)
    async def _handle_validation(request: Request, exc: RequestValidationError) -> Response:
        errors = exc.errors()
        if errors and all(e.get("loc") and e["loc"][0] == "path" for e in errors):
            if _wants_json(request):
                return JSONResponse({"detail": "Not Found"}, status_code=status.HTTP_404_NOT_FOUND)
            return NotFound()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": jsonable_encoder(errors)},
        )
