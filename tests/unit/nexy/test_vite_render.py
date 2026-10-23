import json
from pathlib import Path

import pytest

from nexy.vite import Vite


@pytest.fixture
def vite_project(nexy_project, tmp_path: Path) -> Path:
    nexy_project("useVite = True")
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    return tmp_path


def _write_manifest(project: Path, payload: dict) -> None:
    manifest = project / "__nexy__" / "client" / ".vite" / "manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload), encoding="utf-8")


def test_returns_empty_without_vite_config(nexy_project) -> None:
    nexy_project("useVite = True")
    assert Vite() == ""


def test_returns_empty_when_vite_disabled(nexy_project, tmp_path: Path) -> None:
    nexy_project("useVite = False")
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    assert Vite() == ""


@pytest.mark.usefixtures("vite_project")
def test_dev_mode_serves_hmr_script() -> None:
    assert "/@vite/client" in Vite()


def test_prod_mode_requires_manifest(vite_project: Path) -> None:
    (vite_project / "__nexy__" / "nexy.prod").parent.mkdir()
    (vite_project / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
    assert Vite() == ""


def test_prod_mode_without_entry_returns_empty(vite_project: Path) -> None:
    (vite_project / "__nexy__" / "nexy.prod").parent.mkdir()
    (vite_project / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
    _write_manifest(vite_project, {"other": {"file": "x.js"}})
    assert Vite() == ""


def test_prod_mode_links_built_client(vite_project: Path) -> None:
    client = vite_project / "__nexy__" / "client"
    (client / "assets").mkdir(parents=True)
    (client / "assets" / "main.js").write_text("", encoding="utf-8")
    (client / "assets" / "main.css").write_text("", encoding="utf-8")
    (vite_project / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
    _write_manifest(
        vite_project,
        {"__nexy__/main.ts": {"file": "assets/main.js", "css": ["assets/main.css"]}},
    )
    markup = Vite()
    assert 'src="/assets/main.js"' in markup
    assert 'href="/assets/main.css"' in markup


def test_prod_mode_inlines_built_client(
    vite_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = vite_project / "__nexy__" / "client"
    (client / "assets").mkdir(parents=True)
    (client / "assets" / "main.js").write_text("console.log(1)", encoding="utf-8")
    (client / "assets" / "main.css").write_text("body{}", encoding="utf-8")
    (vite_project / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
    monkeypatch.setenv("NEXY_INLINE_CLIENT", "1")
    _write_manifest(
        vite_project,
        {"__nexy__/main.ts": {"file": "assets/main.js", "css": ["assets/main.css"]}},
    )
    markup = Vite()
    assert "<style>body{}</style>" in markup
    assert "console.log(1)" in markup


def test_prod_mode_malformed_manifest_returns_empty(vite_project: Path) -> None:
    client = vite_project / "__nexy__" / "client"
    (client / ".vite").mkdir(parents=True)
    (client / ".vite" / "manifest.json").write_text("{not json", encoding="utf-8")
    (vite_project / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
    assert Vite() == ""
