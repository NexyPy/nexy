"""`nx build` lists the literal props of each island before the client build reads them (#554)."""

from __future__ import annotations

import importlib
import json
from types import SimpleNamespace

from nexy.modules.builder.island_props import MANIFEST

build_module = importlib.import_module("nexy.modules.cli.commands.build")


def test_the_build_writes_the_island_props_for_the_client_build(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for name in (
        "pycache",
        "ensure_project_packages",
        "abort_on_invalid_config",
        "_announce_start",
    ):
        monkeypatch.setattr(build_module, name, lambda: None)
    monkeypatch.setattr(build_module, "_announce_end", lambda _started: None)
    monkeypatch.setattr(build_module, "_show_summary", lambda *_args: None)
    monkeypatch.setattr(build_module, "write_build_marker", lambda _version: None)
    monkeypatch.setattr(build_module.Config, "useVite", False)
    done = SimpleNamespace(success=["a"], failed=[], skipped=[])
    monkeypatch.setattr(build_module, "_compile_server_components", lambda: done)
    (tmp_path / "src" / "routes").mkdir(parents=True)
    (tmp_path / "src" / "routes" / "index.nexy").write_text(
        '---\nfrom "../components/spike.vue" import Spike\n---\n<Spike label="clicks" />'
    )
    build_module.build()
    assert "src/components/spike.vue" in json.loads(MANIFEST.read_text(encoding="utf-8"))
