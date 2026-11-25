"""Local images become hashed WebP variants with a manifest at build time (#658)."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from PIL import Image

from nexy.modules.images.generator import (
    DEFAULT_WIDTHS,
    ImageBuild,
    ImageBuildError,
    prepare_images,
    write_image_files,
)
from nexy.modules.images.manifest import (
    IMAGE_MANIFEST,
    IMAGE_TYPESCRIPT,
    write_image_typescript,
    write_manifest,
)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "src" / "routes").mkdir(parents=True)
    (tmp_path / "src" / "routes" / "index.nexy").write_text(
        '<Image src="/logo.png" alt="Logo" />', encoding="utf-8"
    )
    source = tmp_path / "public" / "logo.png"
    source.parent.mkdir(parents=True)
    Image.new("RGB", (1200, 600), "blue").save(source)
    return tmp_path


def test_prepare_images_generates_two_widths_in_webp(project: Path) -> None:
    build = prepare_images(project, widths=[320, 640])

    assert sorted(path.rsplit("-", 2)[1] for path in build.files) == ["320", "640"]


def test_every_generated_file_is_a_webp_image(project: Path) -> None:
    build = prepare_images(project, widths=[320, 640])

    assert all(name.endswith(".webp") and data[:4] == b"RIFF" for name, data in build.files.items())


def test_the_manifest_carries_a_srcset_and_sizes(project: Path) -> None:
    build = prepare_images(project, widths=[320, 640])

    assert build.manifest["logo.png"]["srcset"].count("w,") == 1


def test_the_manifest_accepts_a_leading_slash_key(project: Path) -> None:
    build = prepare_images(project, widths=[320, 640])

    assert build.manifest["/logo.png"] == build.manifest["logo.png"]


def test_the_manifest_carries_the_natural_dimensions(project: Path) -> None:
    build = prepare_images(project, widths=[320, 640])

    record = build.manifest["logo.png"]
    assert (record["width"], record["height"]) == (1200, 600)


def test_widths_larger_than_the_source_are_not_generated(project: Path) -> None:
    build = prepare_images(project, widths=[640, 2048])

    assert all("-640-" in path for path in build.files)


def test_a_narrow_source_still_gets_one_variant(project: Path) -> None:
    Image.new("RGB", (100, 50), "red").save(project / "public" / "logo.png")
    build = prepare_images(project, widths=[320, 640])

    assert len(build.files) == 1


def test_an_invalid_width_names_the_file_and_the_reason(project: Path) -> None:
    with pytest.raises(ImageBuildError, match="logo.png: invalid width 0"):
        prepare_images(project, widths=[0])


def test_a_missing_source_names_the_file_and_the_reason(tmp_path: Path) -> None:
    (tmp_path / "src" / "routes").mkdir(parents=True)
    (tmp_path / "src" / "routes" / "index.tsx").write_text(
        "import logo from '../assets/logo.png'", encoding="utf-8"
    )

    with pytest.raises(ImageBuildError, match="assets/logo.png: image file not found"):
        prepare_images(tmp_path, widths=DEFAULT_WIDTHS)


def test_without_pillow_the_plain_url_fallback_is_kept(project: Path, monkeypatch) -> None:
    monkeypatch.setattr("nexy.modules.images.generator._pillow", lambda: None)

    build = prepare_images(project, widths=[320, 640])

    assert build.manifest == {}


def test_writing_a_build_publishes_the_files_and_manifest(project: Path) -> None:
    build = prepare_images(project, widths=[320, 640])
    write_image_files(build, project)
    write_manifest(build.manifest, project)

    assert len(list((project / "__nexy__/client/images").glob("*.webp"))) == 2
    assert json.loads((project / IMAGE_MANIFEST).read_text(encoding="utf-8")) == build.manifest


def test_an_imported_image_can_be_found_by_its_vite_url(project: Path) -> None:
    vite = project / "__nexy__/client/.vite"
    vite.mkdir(parents=True)
    (vite / "manifest.json").write_text(
        json.dumps({"public/logo.png": {"file": "assets/logo-abc123.png"}}), encoding="utf-8"
    )
    build = prepare_images(project, widths=[320, 640])

    assert build.manifest["/assets/logo-abc123.png"] == build.manifest["logo.png"]


def test_a_broken_image_names_the_file_and_the_reason(project: Path) -> None:
    (project / "public" / "logo.png").write_bytes(b"not an image")
    with pytest.raises(ImageBuildError, match="logo.png: cannot read image"):
        prepare_images(project, widths=[320, 640])


def test_an_image_with_alpha_keeps_its_transparency(project: Path) -> None:
    Image.new("RGBA", (400, 200), (0, 0, 0, 0)).save(project / "public" / "logo.png")
    build = prepare_images(project, widths=[320])

    assert Image.open(io.BytesIO(next(iter(build.files.values())))).mode == "RGBA"


def test_a_project_without_images_has_an_empty_manifest(tmp_path: Path) -> None:
    assert prepare_images(tmp_path, widths=[320]) == ImageBuild({}, {})


def test_the_typescript_module_publishes_the_same_manifest(project: Path) -> None:
    build = prepare_images(project, widths=[320, 640])
    write_image_typescript(build.manifest, project)

    assert '"logo.png"' in (project / IMAGE_TYPESCRIPT).read_text(encoding="utf-8")


def test_the_default_widths_are_a_small_set() -> None:
    assert DEFAULT_WIDTHS == (320, 640, 960, 1280)
