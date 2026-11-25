"""An imported image renders markup with generated variants, or a plain fallback URL."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from nexy.core.config import Config
from nexy.helpers.imports.images import Image as ImportedImage


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(Config, "PROJECT_ROOT", tmp_path)
    Image.new("RGB", (400, 200), "blue").save(tmp_path / "logo.png")
    (tmp_path / "__nexy__").mkdir()
    (tmp_path / "__nexy__/image-manifest.json").write_text(
        json.dumps(
            {
                "logo.png": {
                    "src": "/images/logo-abc.webp",
                    "srcset": "/images/logo-abc.webp 400w",
                    "sizes": "100vw",
                    "width": 400,
                    "height": 200,
                }
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


@pytest.mark.usefixtures("project")
def test_an_imported_image_used_as_a_value_returns_its_variant_url() -> None:
    asset = ImportedImage.create("logo.png")

    assert asset() == "/images/logo-abc.webp"


@pytest.mark.usefixtures("project")
def test_an_imported_image_can_render_an_img_element() -> None:
    asset = ImportedImage.create("logo.png")

    assert 'srcset="/images/logo-abc.webp 400w"' in asset(alt="Logo")


def test_without_a_manifest_the_imported_image_keeps_its_data_uri(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(Config, "PROJECT_ROOT", tmp_path)
    Image.new("RGB", (10, 10), "red").save(tmp_path / "logo.png")
    asset = ImportedImage.create("logo.png")

    assert asset().startswith("data:image/png;base64,")


def test_an_absolute_import_path_keeps_its_data_uri(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Config, "PROJECT_ROOT", tmp_path / "other")
    Image.new("RGB", (10, 10), "red").save(tmp_path / "logo.png")
    asset = ImportedImage.create(str(tmp_path / "logo.png"))

    assert asset().startswith("data:image/png;base64,")


def test_a_missing_import_keeps_the_empty_fallback(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Config, "PROJECT_ROOT", tmp_path)
    asset = ImportedImage.create("missing.png")

    assert asset() == ""
