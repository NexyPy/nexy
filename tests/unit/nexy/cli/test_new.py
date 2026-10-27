import importlib

from nexy.modules.cli.init import GitClone
from nexy.modules.cli.init.prompts import validate_project_name as _validate_name


def test_git_clone_targets_repository_default_branch() -> None:
    assert GitClone().branch == "main"


def test_validate_name_empty_returns_error() -> None:
    assert isinstance(_validate_name("   "), str)


def test_validate_name_must_start_with_letter() -> None:
    assert isinstance(_validate_name("3app"), str)


def test_validate_name_rejects_invalid_chars() -> None:
    assert isinstance(_validate_name("my app!"), str)


def test_validate_name_accepts_valid_name(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert _validate_name("my-app") is True


def test_validate_name_rejects_existing_dir(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "taken").mkdir()
    assert isinstance(_validate_name("taken"), str)


class TestFailure:
    """A project that cannot be created ends with one clear line, not a Python traceback."""

    def _run(self, tmp_path, monkeypatch, error):
        from typer.testing import CliRunner

        from nexy.modules.cli import CLI

        new_module = importlib.import_module("nexy.modules.cli.commands.new")

        def failing(*_args, **_kwargs):
            raise error

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(new_module.InitProject, "run", failing)
        return CliRunner().invoke(CLI, ["new", "demo", "--template", "web-fbr"])

    def test_the_exit_code_is_one(self, tmp_path, monkeypatch):
        assert self._run(tmp_path, monkeypatch, RuntimeError("no network")).exit_code == 1

    def test_the_reason_is_shown(self, tmp_path, monkeypatch):
        result = self._run(tmp_path, monkeypatch, RuntimeError("no network"))
        assert "no network" in result.output

    def test_no_traceback_is_shown(self, tmp_path, monkeypatch):
        result = self._run(tmp_path, monkeypatch, RuntimeError("no network"))
        assert "Traceback" not in result.output and "site-packages" not in result.output

    def test_the_half_created_directory_is_removed(self, tmp_path, monkeypatch):
        def create_then_fail(*_args, **_kwargs):
            (tmp_path / "demo").mkdir()
            raise RuntimeError("boom")

        from typer.testing import CliRunner

        from nexy.modules.cli import CLI

        new_module = importlib.import_module("nexy.modules.cli.commands.new")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(new_module.InitProject, "run", create_then_fail)
        CliRunner().invoke(CLI, ["new", "demo", "--template", "web-fbr"])
        assert not (tmp_path / "demo").exists()
