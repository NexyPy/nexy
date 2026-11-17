"""`nx dev` says a failure the way uv does: an error, its cause, and a hint when one helps."""

from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

# The package re-exports the function under the module's name: import the module by path.
dev = importlib.import_module("nexy.modules.cli.commands.dev")


@pytest.fixture(autouse=True)
def english(monkeypatch):
    monkeypatch.setenv("NEXY_LANG", "en")


def test_dev_missing_node_modules_is_a_uv_error_with_hints(monkeypatch, capsys):
    monkeypatch.setattr(dev, "vite_installed", lambda: False)
    monkeypatch.setattr(dev.package_manager, "detect", lambda: "pnpm")
    with pytest.raises(SystemExit):
        dev._require_vite_install()
    assert capsys.readouterr().out.startswith(
        "error: Node.js dependencies are missing.\nhint: Run: pnpm install\n"
    )


def test_dev_a_route_that_fails_to_compile_is_a_uv_error(capsys):
    dev._report_failures(SimpleNamespace(failed=["src/routes/a.nexy"], errors={}))
    assert capsys.readouterr().out == "error: src/routes/a.nexy\n"


def test_dev_client_routes_that_cannot_update_are_a_uv_warning(monkeypatch, capsys):
    def broken() -> None:
        raise RuntimeError("disk full")

    monkeypatch.setattr(dev, "FrontendGenerator", lambda: SimpleNamespace(generate=broken))
    dev._regenerate_client_files()
    expected = "warning: Could not update the client routes: disk full\n"
    assert capsys.readouterr().out == expected


def test_dev_a_server_that_stopped_is_a_uv_error(capsys):
    dev._Reloader._failed("exit code 3")
    expected = "error: The server stopped (exit code 3): waiting for a fix.\n"
    assert capsys.readouterr().out == expected


def test_dev_a_failed_start_is_a_uv_error_with_its_cause(monkeypatch, capsys):
    # _initialise switches the VFS to dev mode: keep the other tests in their own mode.
    monkeypatch.setattr(dev.VFS, "_dev_mode", dev.VFS.is_dev_mode())

    def broken(*_args):
        raise RuntimeError("port taken")

    monkeypatch.setattr(dev, "_generate_and_compile", broken)
    with pytest.raises(SystemExit):
        dev._initialise(SimpleNamespace(useVite=False), 5173, False)
    assert capsys.readouterr().out == "error: Could not start the dev server\n  cause: port taken\n"


def test_dev_prints_no_cross_mark(monkeypatch, capsys):
    monkeypatch.setattr(dev, "vite_installed", lambda: False)
    with pytest.raises(SystemExit):
        dev._require_vite_install()
    assert not set(capsys.readouterr().out) & set("✘✗")
