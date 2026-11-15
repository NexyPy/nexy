"""`nx build` leaves the marker `nx start` asks for, and only when the build succeeds."""

from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

build_module = importlib.import_module("nexy.modules.cli.commands.build")


@pytest.fixture
def quiet_build(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for name in ("pycache", "ensure_project_packages", "abort_on_invalid_config"):
        monkeypatch.setattr(build_module, name, lambda: None)
    monkeypatch.setattr(build_module, "_announce_start", lambda: None)
    monkeypatch.setattr(build_module, "_announce_end", lambda _started: None)
    monkeypatch.setattr(build_module, "_show_summary", lambda *_args: None)
    monkeypatch.setattr(build_module.Config, "useVite", False)
    return tmp_path


def _compiled(failed: list[str]):
    return lambda: SimpleNamespace(success=["a"], failed=failed, skipped=[])


def test_a_successful_build_leaves_the_marker(monkeypatch, quiet_build):
    monkeypatch.setattr(build_module, "_compile_server_components", _compiled([]))
    build_module.build()
    assert (quiet_build / "__nexy__" / "build.json").is_file()


def test_a_failed_build_leaves_no_marker(monkeypatch, quiet_build):
    monkeypatch.setattr(build_module, "_compile_server_components", _compiled(["x.nexy"]))
    with pytest.raises(SystemExit):
        build_module.build()
    assert not (quiet_build / "__nexy__" / "build.json").exists()
