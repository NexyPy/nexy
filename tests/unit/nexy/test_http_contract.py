"""`nexy.http` is the HTTP vocabulary of a handler; application code should not import FastAPI."""

import importlib

import pytest

import nexy.http as http

CONTRACT = {
    "BackgroundTasks",
    "Body",
    "Cookie",
    "Depends",
    "FileResponse",
    "HTMLResponse",
    "Header",
    "HTTPException",
    "JSONResponse",
    "Path",
    "PlainTextResponse",
    "Query",
    "RedirectResponse",
    "Request",
    "Response",
    "StreamingResponse",
    "status",
}


def test_the_public_surface_is_exactly_the_contract():
    assert set(http.__all__) == CONTRACT


@pytest.mark.parametrize("name", sorted(CONTRACT))
def test_every_name_resolves(name):
    assert getattr(http, name) is not None


def test_exception_is_the_one_the_error_handlers_catch():
    from starlette.exceptions import HTTPException as Starlette

    assert issubclass(http.HTTPException, Starlette)


def test_a_handler_written_with_the_contract_runs():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()

    @app.get("/who")
    async def who(request: http.Request, user: str = http.Header(default="anon")):
        if user == "banned":
            raise http.HTTPException(status_code=403, detail="no")
        return http.JSONResponse({"user": user, "path": request.url.path})

    client = TestClient(app)
    assert client.get("/who", headers={"user": "ada"}).json() == {"user": "ada", "path": "/who"}
    assert client.get("/who", headers={"user": "banned"}).status_code == 403


def test_importing_it_does_not_import_the_application():
    assert importlib.import_module("nexy.http").__name__ == "nexy.http"
