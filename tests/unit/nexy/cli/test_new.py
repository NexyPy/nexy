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
