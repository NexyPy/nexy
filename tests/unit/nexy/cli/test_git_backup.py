"""Putting the project's `.git` back after a template was fetched."""

import shutil
from pathlib import Path

from nexy.modules.cli.init.git_backup import GitBackup


def _refuse(*_args, **_kwargs):
    raise OSError("locked")


def test_a_history_that_cannot_be_put_back_is_a_warning(tmp_path: Path, monkeypatch, capsys):
    (tmp_path / ".git_old").mkdir()
    monkeypatch.setattr(Path, "rename", _refuse)
    monkeypatch.setattr(shutil, "copytree", _refuse)
    GitBackup(tmp_path).restore()
    assert capsys.readouterr().out == "warning: could not restore previous .git\n"
