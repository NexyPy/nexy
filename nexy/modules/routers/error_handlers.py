from http import HTTPStatus

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException

from nexy.errors import InternalServerError, NotFound, error_page
from nexy.modules.routers.crash import wants_json


def _phrase(code: int) -> str:
    try:
        return HTTPStatus(code).phrase
    except ValueError:
        return "Error"


def _redirect_of(exc: HTTPException) -> Response | None:
    """A real redirect for a 3xx exception that names a `Location`; None for anything else."""
    if not 300 <= exc.status_code < 400:
        return None
    named = {key.lower(): value for key, value in (getattr(exc, "headers", None) or {}).items()}
    if "location" not in named:
        return None
    return RedirectResponse(named["location"], status_code=exc.status_code)


def handle_http_exception(request: Request, exc: HTTPException) -> Response:
    """Map HTTP exceptions to redirects, JSON for API clients, else to Nexy error pages."""
    redirect = _redirect_of(exc)
    if redirect is not None:
        return redirect
    headers = getattr(exc, "headers", None)
    if wants_json(request):
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
            if wants_json(request):
                return JSONResponse({"detail": "Not Found"}, status_code=status.HTTP_404_NOT_FOUND)
            return NotFound()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": jsonable_encoder(errors)},
        )
