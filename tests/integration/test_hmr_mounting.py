"""The hot-reload socket exists in development only."""

from __future__ import annotations

from nexy.helpers.server.proxy import DEV_ENV_VAR
from nexy.modules.routers.app import AppServer

HMR_PATH = "/_nexy/hmr"


def _paths() -> set[str]:
    return {getattr(route, "path", "") for route in AppServer().run().routes}


def test_production_does_not_mount_the_hmr_socket(nexy_project, monkeypatch):
    monkeypatch.delenv(DEV_ENV_VAR, raising=False)
    nexy_project("")
    assert HMR_PATH not in _paths()


def test_development_mounts_the_hmr_socket(nexy_project, monkeypatch):
    monkeypatch.setenv(DEV_ENV_VAR, "1")
    nexy_project("")
    assert HMR_PATH in _paths()
