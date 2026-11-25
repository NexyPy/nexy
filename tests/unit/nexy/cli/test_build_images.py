"""`nx build` publishes responsive images before the client bundle reads the manifest."""

from __future__ import annotations

import importlib
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from nexy.modules.images.generator import ImageBuildError
from nexy.modules.images.manifest import IMAGE_MANIFEST, IMAGE_TYPESCRIPT

build_module = importlib.import_module("nexy.modules.cli.commands.build")
PAGE = '<Image src="/logo.png" alt="Logo" />'


@pytest.fixture
def quiet_build(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    names = ("pycache", "ensure_project_packages", "abort_on_invalid_config", "_announce_start")
    for name in names:
        monkeypatch.setattr(build_module, name, lambda: None)
    monkeypatch.setattr(build_module, "_announce_end", lambda _started: None)
    monkeypatch.setattr(build_module, "_show_summary", lambda *_args: None)
    monkeypatch.setattr(build_module, "write_build_marker", lambda _version: None)
    monkeypatch.setattr(build_module.Config, "useVite", False)
    done = SimpleNamespace(success=["a"], failed=[], skipped=[])
    monkeypatch.setattr(build_module, "_compile_server_components", lambda: done)


def _sample_project(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src/index.nexy").write_text(PAGE, encoding="utf-8")
    (tmp_path / "public").mkdir()
    Image.new("RGB", (800, 400), "blue").save(tmp_path / "public/logo.png")


@pytest.mark.usefixtures("quiet_build")
def test_the_build_writes_the_image_variants(tmp_path: Path) -> None:
    _sample_project(tmp_path)

    build_module.build()

    assert len(list((tmp_path / "__nexy__/client/images").glob("*.webp"))) >= 2


@pytest.mark.usefixtures("quiet_build")
def test_the_build_writes_the_client_manifest(tmp_path: Path) -> None:
    _sample_project(tmp_path)

    build_module.build()

    assert "logo.png" in (tmp_path / IMAGE_TYPESCRIPT).read_text(encoding="utf-8")


@pytest.mark.usefixtures("quiet_build")
def test_generated_images_survive_the_client_bundle(monkeypatch, tmp_path: Path) -> None:
    _sample_project(tmp_path)

    def wipe_client() -> list:
        shutil.rmtree(tmp_path / "__nexy__/client", ignore_errors=True)
        return []

    monkeypatch.setattr(build_module, "_build_client_bundle", wipe_client)
    monkeypatch.setattr(build_module.Config, "useVite", True)

    build_module.build()

    assert len(list((tmp_path / "__nexy__/client/images").glob("*.webp"))) >= 2


@pytest.mark.usefixtures("quiet_build")
def test_an_invalid_image_fails_the_build(monkeypatch) -> None:
    def fail() -> None:
        raise ImageBuildError("logo.png: invalid width 0 (width must be positive)")

    monkeypatch.setattr(build_module, "_prepare_images", fail)

    with pytest.raises(SystemExit, match="1"):
        build_module.build()


@pytest.mark.usefixtures("quiet_build")
def test_the_build_manifest_matches_the_written_files(tmp_path: Path) -> None:
    _sample_project(tmp_path)

    build_module.build()

    manifest = json.loads((tmp_path / IMAGE_MANIFEST).read_text(encoding="utf-8"))
    assert manifest["logo.png"]["src"].startswith("/images/")
