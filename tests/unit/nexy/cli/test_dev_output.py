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


def test_dev_a_server_that_crashes_is_a_uv_error(monkeypatch, capsys):
    def crash(*_args):
        raise RuntimeError("socket closed")

    monkeypatch.setattr(dev, "_watch", crash)
    monkeypatch.setattr(dev, "_release", lambda *_args: None)
    dev._serve(SimpleNamespace(), None, dev._Session(), 0.0, dev.OccupiedPort(3000, 3000))
    assert capsys.readouterr().out == "error: socket closed\n"


class _FreedPort:
    asked = 3000

    def free(self):
        return 4242


class _KeptPort:
    asked = 3000

    def free(self):
        return None


def test_dev_reports_the_port_it_freed_on_stop(monkeypatch, capsys):
    monkeypatch.setattr(dev, "stop_observer", lambda _observer: None)
    monkeypatch.setattr(dev.Server, "stop_process", lambda _process: None)
    dev._release(None, dev._Session(), _FreedPort())
    assert "Freed port 3000: stopped process 4242." in capsys.readouterr().out


def test_dev_says_nothing_when_no_port_was_freed(monkeypatch, capsys):
    monkeypatch.setattr(dev, "stop_observer", lambda _observer: None)
    monkeypatch.setattr(dev.Server, "stop_process", lambda _process: None)
    dev._release(None, dev._Session(), _KeptPort())
    assert "Freed port" not in capsys.readouterr().out
