"""The SSG scripts are copied into the project; a failure is reported, not swallowed."""

from __future__ import annotations

import shutil
from pathlib import Path

from nexy.modules.frontend.assets import copy_ssg_scripts


def test_the_scripts_are_copied_with_the_excludes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    copy_ssg_scripts(["dist"])
    assert "dist/**" in (tmp_path / "__nexy__" / "scripts" / "excludes.ts").read_text("utf-8")


def test_a_copy_failure_is_reported_on_the_console(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    def refuse(*_args: object, **_kwargs: object) -> Path:
        raise PermissionError("denied")

    monkeypatch.setattr(shutil, "copytree", refuse)
    copy_ssg_scripts([])
    assert "could not copy the SSG scripts" in capsys.readouterr().out
