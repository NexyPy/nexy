"""Contract of Node.js package manager detection and install argv."""

from pathlib import Path

import pytest

from nexy.helpers.common import package_manager


def _only(*installed: str):
    return lambda name: f"/bin/{name}" if name in installed else None


def test_detect_prefers_bun_over_pnpm_and_npm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(package_manager, "resolve", _only("bun", "pnpm", "npm"))

    assert package_manager.detect(tmp_path) == "bun"


def test_detect_falls_back_to_pnpm_without_bun(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(package_manager, "resolve", _only("pnpm", "npm"))

    assert package_manager.detect(tmp_path) == "pnpm"


def test_detect_falls_back_to_npm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(package_manager, "resolve", _only("npm"))

    assert package_manager.detect(tmp_path) == "npm"


def test_detect_returns_none_without_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(package_manager, "resolve", _only())

    assert package_manager.detect(tmp_path) is None


def test_detect_keeps_pnpm_lockfile_over_bun_binary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    (tmp_path / "pnpm-lock.yaml").write_text("", encoding="utf-8")
    monkeypatch.setattr(package_manager, "resolve", _only("bun", "pnpm", "npm"))

    assert package_manager.detect(tmp_path) == "pnpm"


def test_detect_reads_bun_binary_lockfile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    (tmp_path / "bun.lockb").write_text("", encoding="utf-8")
    monkeypatch.setattr(package_manager, "resolve", _only("bun", "npm"))

    assert package_manager.detect(tmp_path) == "bun"


def test_install_argv_adds_pnpm_allow_build_from_major_11(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(package_manager, "executable", lambda manager: f"/bin/{manager}")
    monkeypatch.setattr(package_manager, "version", lambda *_: (11, 0, 0))

    assert package_manager.install_argv("pnpm", ("esbuild",)) == [
        "/bin/pnpm",
        "install",
        "--allow-build=esbuild",
    ]


def test_install_argv_omits_pnpm_allow_build_before_major_11(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(package_manager, "executable", lambda manager: f"/bin/{manager}")
    monkeypatch.setattr(package_manager, "version", lambda *_: (10, 12, 0))

    assert package_manager.install_argv("pnpm", ("esbuild",)) == ["/bin/pnpm", "install"]


def test_install_argv_never_adds_allow_build_to_bun(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(package_manager, "executable", lambda manager: f"/bin/{manager}")

    assert package_manager.install_argv("bun", ("esbuild",)) == ["/bin/bun", "install"]


def test_add_argv_uses_npm_install(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(package_manager, "executable", lambda manager: f"/bin/{manager}")

    assert package_manager.add_argv("npm", ["react"]) == ["/bin/npm", "install", "react"]


def test_add_argv_uses_pnpm_add(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(package_manager, "executable", lambda manager: f"/bin/{manager}")

    assert package_manager.add_argv("pnpm", ["react"]) == ["/bin/pnpm", "add", "react"]
