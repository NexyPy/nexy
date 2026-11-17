"""`useDocs` decides where the API reference and /openapi.json answer on the real application."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nexy.helpers.server.dev_mode import DEV_ENV_VAR


def _status(nexy_project, attrs: str, path: str) -> int:
    from nexy.modules.routers.app import AppServer

    nexy_project(attrs)
    client = TestClient(AppServer().run(), raise_server_exceptions=False)
    return client.get(path).status_code


@pytest.fixture
def production(monkeypatch):
    monkeypatch.delenv(DEV_ENV_VAR, raising=False)


@pytest.fixture
def dev(monkeypatch):
    monkeypatch.setenv(DEV_ENV_VAR, "1")


@pytest.mark.usefixtures("production")
@pytest.mark.parametrize("path", ["/docs", "/openapi.json"])
def test_app_docs_production_hides_them_by_default(nexy_project, path):
    assert _status(nexy_project, "", path) == 404


@pytest.mark.usefixtures("dev")
@pytest.mark.parametrize("path", ["/docs", "/openapi.json"])
def test_app_docs_the_dev_server_serves_them_by_default(nexy_project, path):
    assert _status(nexy_project, "", path) == 200


@pytest.mark.usefixtures("production")
@pytest.mark.parametrize("path", ["/docs", "/openapi.json"])
def test_app_docs_true_serves_them_in_production(nexy_project, path):
    assert _status(nexy_project, "useDocs = True", path) == 200


@pytest.mark.usefixtures("dev")
@pytest.mark.parametrize("path", ["/docs", "/openapi.json"])
def test_app_docs_false_hides_them_on_the_dev_server(nexy_project, path):
    assert _status(nexy_project, "useDocs = False", path) == 404
