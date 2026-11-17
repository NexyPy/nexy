"""`useMaxBodySize` is read from nexyconfig.py and mounted on the real application."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _post(nexy_project, attrs: str, size: int) -> int:
    from nexy.modules.routers.app import AppServer

    nexy_project(attrs)
    client = TestClient(AppServer().run(), raise_server_exceptions=False)
    return client.post("/nowhere", content=b"a" * size).status_code


def test_app_body_limit_a_body_over_the_default_is_a_413(nexy_project):
    assert _post(nexy_project, "", 1024 * 1024 + 1) == 413


def test_app_body_limit_the_project_sets_the_limit(nexy_project):
    assert _post(nexy_project, "useMaxBodySize = 10", 11) == 413


def test_app_body_limit_zero_turns_it_off(nexy_project):
    assert _post(nexy_project, "useMaxBodySize = 0", 1024 * 1024 + 1) != 413
