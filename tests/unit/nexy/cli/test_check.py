from pathlib import Path

from nexy.utils.fs.scan import has_files as _has_files


def test_has_files_detects_matching_extension(tmp_path: Path) -> None:
    (tmp_path / "index.py").write_text("", encoding="utf-8")
    assert _has_files(tmp_path, (".py",))


def test_has_files_returns_false_when_absent(tmp_path: Path) -> None:
    (tmp_path / "index.txt").write_text("", encoding="utf-8")
    assert not _has_files(tmp_path, (".py",))


def test_has_files_recurses_subdirectories(tmp_path: Path) -> None:
    (tmp_path / "routes").mkdir()
    (tmp_path / "routes" / "page.tsx").write_text("", encoding="utf-8")
    assert _has_files(tmp_path, (".tsx",))


def test_has_files_skips_excluded_dirs(tmp_path: Path) -> None:
    (tmp_path / "__nexy__").mkdir()
    (tmp_path / "__nexy__" / "gen.py").write_text("", encoding="utf-8")
    assert not _has_files(tmp_path, (".py",))
