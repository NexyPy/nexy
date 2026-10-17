from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from nexy.errors import InternalServerError, NotFound


def handle_http_exception(_request: Request, exc: HTTPException) -> Response:
    """Map HTTP exceptions to Nexy error pages (404, 500 and a plain fallback)."""
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return NotFound()
    if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        return InternalServerError()
    return Response(
        content=f"<h1>{exc.status_code} - {exc.detail}</h1>", status_code=exc.status_code
    )


def register_validation_error_handler(server: FastAPI) -> None:
    """Convert path-param validation failures into 404s.

    A dynamic route like /{id} captures any unknown path; when the segment
    fails type validation (int("nonexistent")) FastAPI returns 422. From
    the caller's perspective the URL simply does not exist, so we surface
    it as 404 instead.
    """

    @server.exception_handler(RequestValidationError)
    async def _handle_validation(_request: Request, exc: RequestValidationError) -> Response:
        errors = exc.errors()
        if errors and all(e.get("loc") and e["loc"][0] == "path" for e in errors):
            return NotFound()
        return Response(content=exc.json(), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
