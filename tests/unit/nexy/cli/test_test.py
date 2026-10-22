from pathlib import Path

from nexy.modules.cli.commands.test import _has_vitest


def test_has_vitest_detects_config_file(tmp_path: Path) -> None:
    (tmp_path / "vitest.config.ts").write_text("", encoding="utf-8")
    assert _has_vitest(tmp_path)


def test_has_vitest_detects_package_json_dep(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{"devDependencies": {"vitest": "^1.0.0"}}', encoding="utf-8"
    )
    assert _has_vitest(tmp_path)


def test_has_vitest_false_without_config(tmp_path: Path) -> None:
    assert not _has_vitest(tmp_path)


def test_has_vitest_false_on_malformed_package_json(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("not json", encoding="utf-8")
    assert not _has_vitest(tmp_path)
