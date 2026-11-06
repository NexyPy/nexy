"""The CLI reads `COM/`, fails on what blocks a post, and never talks to a network."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "publish_social.py"


def _load() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("publish_social", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["publish_social"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="cli")
def cli_fixture() -> types.ModuleType:
    return _load()


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "COM"
    (root / "proof").mkdir(parents=True)
    (root / "proof" / "hmr-2026-11.md").write_text("# HMR\n")
    return root


def _post(root: Path, slug: str = "2026-11-hmr", body: str = "47 ms.") -> Path:
    directory = root / "posts" / slug
    (directory / "carousel").mkdir(parents=True, exist_ok=True)
    for index in (1, 2):
        Image.new("RGB", (1080, 1350), "white").save(directory / "carousel" / f"0{index}.png")
    (directory / "post.md").write_text(
        "+++\n"
        "date = 2026-11-06\n"
        'platforms = ["linkedin"]\n'
        'cta = "comment"\n'
        'ask = "report"\n'
        'proof = ["hmr-2026-11.md"]\n'
        'alt = ["one", "two"]\n'
        "+++\n\n"
        f"{body}\n",
        encoding="utf-8",
    )
    return directory


def test_list_names_every_item(
    cli: types.ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _post(_root(tmp_path))
    assert cli.main(["--root", str(tmp_path / "COM"), "--list"]) == 0
    assert "posts/2026-11-hmr.en" in capsys.readouterr().out


def test_list_says_so_when_there_is_nothing(cli: types.ModuleType, tmp_path: Path) -> None:
    assert cli.main(["--root", str(tmp_path / "COM"), "--list"]) == 1


def test_check_passes_on_a_clean_item(cli: types.ModuleType, tmp_path: Path) -> None:
    _post(_root(tmp_path))
    assert cli.main(["--root", str(tmp_path / "COM"), "--check"]) == 0


def test_check_fails_on_a_hashtag(cli: types.ModuleType, tmp_path: Path) -> None:
    _post(_root(tmp_path), body="47 ms.\n\n#python")
    assert cli.main(["--root", str(tmp_path / "COM"), "--check"]) == 1


def test_pack_writes_the_pdf_and_the_contact_sheet(
    cli: types.ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _post(_root(tmp_path))
    assert cli.main(["--root", str(tmp_path / "COM"), "--pack"]) == 0
    assert "2026-11-hmr-feed.png" in capsys.readouterr().out


def test_pack_without_a_carousel_says_so(cli: types.ModuleType, tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "posts" / "2026-11-text").mkdir(parents=True)
    (root / "posts" / "2026-11-text" / "post.md").write_text(
        "+++\ndate = 2026-11-06\n+++\n\nBody.\n"
    )
    assert cli.main(["--root", str(root), "--pack"]) == 1


def test_dry_run_prints_the_caption_and_a_tagged_link(
    cli: types.ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    directory = _post(_root(tmp_path))
    path = directory / "post.md"
    path.write_text(
        path.read_text().replace(
            'cta = "comment"', 'cta = "comment"\nlink = "https://example.test/x"'
        )
    )
    assert cli.main(["--root", str(tmp_path / "COM"), "--dry-run", "--platform", "linkedin"]) == 0
    printed = capsys.readouterr().out
    assert "utm_source=linkedin" in printed and "47 ms." in printed


def test_dry_run_says_so_when_the_language_is_not_there(
    cli: types.ModuleType, tmp_path: Path
) -> None:
    _post(_root(tmp_path))
    assert cli.main(["--root", str(tmp_path / "COM"), "--dry-run", "--lang", "fr"]) == 1
