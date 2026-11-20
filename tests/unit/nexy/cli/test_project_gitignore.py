"""The .gitignore of a new project keeps out what Nexy writes, so a commit holds sources only."""

from __future__ import annotations

import pytest

from nexy.modules.cli.init import template_setup


@pytest.fixture(autouse=True)
def no_git(monkeypatch: pytest.MonkeyPatch) -> None:
    """The file is the subject here, not the repository `git init` makes."""
    monkeypatch.setattr(template_setup.shutil, "which", lambda _name: None)


def test_the_compiled_pages_are_ignored(tmp_path):
    template_setup.init_git(tmp_path)
    assert "__nexy__/" in (tmp_path / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_a_gitignore_the_project_has_is_kept(tmp_path):
    (tmp_path / ".gitignore").write_text("mine/\n", encoding="utf-8")
    template_setup.init_git(tmp_path)
    assert (tmp_path / ".gitignore").read_text(encoding="utf-8") == "mine/\n"
