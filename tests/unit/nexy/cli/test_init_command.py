"""`nx init` ends a failure with one uv error line, not a Python traceback."""

import importlib

from typer.testing import CliRunner

from nexy.modules.cli import CLI


def _run(tmp_path, monkeypatch, failure):
    init_module = importlib.import_module("nexy.modules.cli.commands.init")

    def failing(*_args, **_kwargs):
        raise failure

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(init_module.InitProject, "run", failing)
    return CliRunner().invoke(CLI, ["init"])


def test_a_failure_exits_with_one(tmp_path, monkeypatch):
    assert _run(tmp_path, monkeypatch, RuntimeError("no network")).exit_code == 1


def test_a_failure_is_an_error_line_with_its_cause(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, RuntimeError("no network"))
    assert "error: Could not initialize the project\n  cause: no network\n" in result.output


def test_a_failure_shows_no_traceback(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, RuntimeError("no network"))
    assert "Traceback" not in result.output
