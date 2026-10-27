"""A request that raises is reported once and answered safely."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from nexy.helpers.server.proxy import DEV_ENV_VAR
from nexy.modules.routers.crash import handle_crash, inspect_crash

SECRET = "database password is hunter2"


def _app() -> TestClient:
    app = FastAPI()
    app.add_exception_handler(Exception, handle_crash)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError(SECRET)

    @app.get("/markup")
    def markup() -> None:
        raise ValueError("<script>alert(1)</script>")

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def prod(monkeypatch):
    monkeypatch.delenv(DEV_ENV_VAR, raising=False)


@pytest.fixture
def dev(monkeypatch):
    monkeypatch.setenv(DEV_ENV_VAR, "1")


@pytest.mark.usefixtures("prod")
class TestProduction:
    def test_a_page_asks_for_a_retry_and_shows_a_reference(self):
        page = _app().get("/boom", headers={"accept": "text/html"})
        assert page.status_code == 500 and "Reference:" in page.text

    def test_the_page_does_not_leak_the_error(self):
        page = _app().get("/boom", headers={"accept": "text/html"})
        assert SECRET not in page.text and "RuntimeError" not in page.text

    def test_an_api_client_gets_json_with_the_reference(self):
        body = _app().get("/boom", headers={"accept": "application/json"}).json()
        assert body["detail"] == "Internal Server Error" and len(body["reference"]) == 8

    def test_the_json_does_not_leak_the_error(self):
        answer = _app().get("/boom", headers={"accept": "application/json"})
        assert SECRET not in answer.text

    def test_the_answer_carries_the_security_headers(self):
        answer = _app().get("/boom", headers={"accept": "application/json"})
        assert answer.headers["x-content-type-options"] == "nosniff"

    def test_the_log_carries_the_same_reference(self, capsys):
        body = _app().get("/boom", headers={"accept": "application/json"}).json()
        assert body["reference"] in capsys.readouterr().out

    def test_the_log_has_the_whole_traceback(self, capsys):
        _app().get("/boom", headers={"accept": "application/json"})
        out = capsys.readouterr().out
        assert "RuntimeError" in out and "Traceback" in out


@pytest.mark.usefixtures("dev")
class TestDevelopment:
    def test_the_page_names_the_error_and_the_code(self):
        page = _app().get("/boom", headers={"accept": "text/html"})
        assert "RuntimeError" in page.text and "raise RuntimeError" in page.text

    def test_the_page_escapes_the_message(self):
        page = _app().get("/markup", headers={"accept": "text/html"})
        assert "<script>alert(1)</script>" not in page.text

    def test_json_names_the_error_too(self):
        body = _app().get("/boom", headers={"accept": "application/json"}).json()
        assert body["error"] == f"RuntimeError: {SECRET}"

    def test_the_log_points_at_the_line(self, capsys):
        _app().get("/boom", headers={"accept": "application/json"})
        out = capsys.readouterr().out
        assert "RuntimeError" in out and "test_crash.py" in out


def test_inspect_crash_finds_the_project_frame_that_raised():
    try:
        raise KeyError("src")
    except KeyError as error:
        crash = inspect_crash(error)
    assert crash.origin is not None and crash.origin.function == (
        "test_inspect_crash_finds_the_project_frame_that_raised"
    )


def test_inspect_crash_gives_each_crash_its_own_reference():
    first = inspect_crash(ValueError("a"))
    second = inspect_crash(ValueError("a"))
    assert first.reference != second.reference


def test_a_crash_on_the_last_line_of_a_file_still_has_its_code(tmp_path):
    source = tmp_path / "last.py"
    source.write_text("def f():" + chr(10) + "    raise ValueError('x')", encoding="utf-8")
    namespace: dict = {}
    exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), namespace)
    try:
        namespace["f"]()
    except ValueError as error:
        crash = inspect_crash(error, tmp_path)
    assert crash.origin is not None and crash.origin.code[-1] == (2, "    raise ValueError('x')")


@pytest.mark.usefixtures("prod")
def test_a_handler_that_fails_still_answers(monkeypatch):
    def broken(*_args, **_kwargs):
        raise OSError("disk")

    monkeypatch.setattr("nexy.modules.routers.crash.inspect_crash", broken)
    assert _app().get("/boom", headers={"accept": "text/html"}).status_code == 500
