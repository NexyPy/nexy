"""nx build writes `@nexy/actions` through the action engine before the bundle."""

from __future__ import annotations

import importlib

from nexy.modules.routers.actions import engine

# The package exports the `build` function under the module's name: import the module itself.
build = importlib.import_module("nexy.modules.cli.commands.build")


def test_the_build_refreshes_the_action_client(monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(engine.ACTION_ENGINE, "refresh_client", lambda: calls.append("refresh"))
    build._write_action_client()
    assert calls == ["refresh"]
