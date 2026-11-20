"""After the files are written, nx new installs the project from its own folder."""

from __future__ import annotations

from types import SimpleNamespace

from nexy.modules.cli.init import template_setup


def test_the_pipeline_installs_the_project_in_its_folder(tmp_path, monkeypatch):
    seen = []

    def installer(directory):
        seen.append(directory)
        return SimpleNamespace(install_all=lambda: None)

    monkeypatch.setattr(template_setup, "DependencyInstaller", installer)
    monkeypatch.setattr(template_setup, "init_git", lambda _dest: None)
    monkeypatch.setattr(template_setup, "print_success_message", lambda *_a, **_k: None)
    template_setup._run_post_init_pipeline(tmp_path, {}, "shop")
    assert seen == [tmp_path]
