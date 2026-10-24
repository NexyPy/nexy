"""`nexy dev` must fail fast when node_modules is absent, never install it."""

import importlib
from pathlib import Path

import pytest

dev_module = importlib.import_module("nexy.modules.cli.commands.dev")


def _write_vite(root: Path) -> None:
    vite = root / "node_modules" / "vite" / "bin" / "vite.js"
    vite.parent.mkdir(parents=True)
    vite.write_text("", encoding="utf-8")


def test_require_vite_install_returns_when_local_vite_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_vite(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert dev_module._require_vite_install() is None


def test_require_vite_install_exits_when_local_vite_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(dev_module.package_manager, "detect", lambda: "bun")

    with pytest.raises(SystemExit) as error:
        dev_module._require_vite_install()

    assert error.value.code == 1


def test_require_vite_install_names_the_detected_manager(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(dev_module.package_manager, "detect", lambda: "pnpm")

    with pytest.raises(SystemExit):
        dev_module._require_vite_install()

    assert "pnpm install" in capsys.readouterr().out
