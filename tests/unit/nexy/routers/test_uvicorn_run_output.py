"""A server that cannot start says so the way uv says a failure."""

from __future__ import annotations

import pytest

from nexy.helpers.server import uvicorn_run


@pytest.fixture(autouse=True)
def english(monkeypatch, tmp_path):
    monkeypatch.setenv("NEXY_LANG", "en")
    monkeypatch.chdir(tmp_path)


def _refuse(*_args, **_kwargs):
    raise OSError("address already in use")


def test_a_server_that_cannot_start_is_a_uv_error_with_its_cause(monkeypatch, capsys):
    monkeypatch.setattr(uvicorn_run.uvicorn, "run", _refuse)
    uvicorn_run.run_uvicorn(port=3999)
    expected = "error: Could not start the server\n  cause: address already in use\n"
    assert capsys.readouterr().out.endswith(expected)


def test_a_server_that_cannot_start_returns_none(monkeypatch):
    monkeypatch.setattr(uvicorn_run.uvicorn, "run", _refuse)
    assert uvicorn_run.run_uvicorn(port=3999) is None
