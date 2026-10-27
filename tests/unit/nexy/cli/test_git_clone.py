"""`nx new -t <template>` fetches a template from a Git repository into a folder."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from nexy.modules.cli.init.clone import GitClone

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def remote(tmp_path: Path) -> Path:
    """A repository with a template at its root and another in `templates/web`."""
    repo = tmp_path / "remote"
    (repo / "templates" / "web" / "src").mkdir(parents=True)
    (repo / "templates" / "web" / "node_modules").mkdir()
    (repo / "README.md").write_text("root", encoding="utf-8")
    (repo / "templates" / "web" / "package.json").write_text("{}", encoding="utf-8")
    (repo / "templates" / "web" / "src" / "app.py").write_text("x = 1", encoding="utf-8")
    (repo / "templates" / "web" / "node_modules" / "junk.js").write_text("", encoding="utf-8")
    (repo / ".github").mkdir()
    (repo / ".github" / "ci.yml").write_text("on: push", encoding="utf-8")
    _git(repo, "init", "-b", "main")
    _git(repo, "add", "-f", ".")
    _git(repo, "commit", "-m", "template")
    return repo


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    folder = tmp_path / "project"
    folder.mkdir()
    monkeypatch.chdir(folder)
    return folder


def _clone(remote: Path, dest: Path, subdir: str | None = None, branch: str = "main") -> None:
    GitClone().clone(str(remote), branch, dest, subdir)


class TestIntoAnEmptyFolder:
    def test_the_files_of_the_repository_arrive(self, remote, project):
        _clone(remote, project)
        assert (project / "README.md").read_text(encoding="utf-8") == "root"

    def test_no_git_folder_is_left_behind(self, remote, project):
        _clone(remote, project)
        assert not (project / ".git").exists()

    def test_the_ci_folder_of_the_template_is_not_kept(self, remote, project):
        _clone(remote, project)
        assert not (project / ".github").exists()

    def test_a_subdirectory_becomes_the_project_root(self, remote, project):
        _clone(remote, project, subdir="templates/web")
        assert (project / "package.json").is_file() and (project / "src" / "app.py").is_file()

    def test_the_subdirectory_folder_itself_is_removed(self, remote, project):
        _clone(remote, project, subdir="templates/web")
        assert not (project / "templates").exists()

    def test_dependency_folders_of_the_template_are_dropped(self, remote, project):
        _clone(remote, project, subdir="templates/web")
        assert not (project / "node_modules").exists()


class TestIntoAFolderWithOnlyAVenv:
    def test_the_template_is_extracted_beside_the_venv(self, remote, project):
        (project / ".venv").mkdir()
        _clone(remote, project)
        assert (project / "README.md").is_file() and (project / ".venv").is_dir()


class TestFailures:
    def test_an_unknown_branch_says_so(self, remote, project):
        with pytest.raises(Exception, match="not found on remote"):
            _clone(remote, project, branch="nope")

    def test_an_unknown_subdirectory_says_so(self, remote, project):
        with pytest.raises(Exception, match="Failed to extract"):
            _clone(remote, project, subdir="templates/missing")

    def test_a_failure_still_removes_the_git_folder(self, remote, project):
        with pytest.raises(Exception, match="not found"):
            _clone(remote, project, branch="nope")
        assert not (project / ".git").exists()


class TestExistingGitHistory:
    def test_the_history_of_the_project_survives(self, remote, project):
        _git(project, "init", "-b", "main")
        (project / "keep.txt").write_text("mine", encoding="utf-8")
        _git(project, "add", ".")
        _git(project, "commit", "-m", "mine")
        _clone(remote, project, subdir="templates/web")
        log = subprocess.run(
            ["git", "log", "--oneline"], cwd=project, capture_output=True, text=True, check=True
        )
        assert "mine" in log.stdout

    def test_no_backup_folder_is_left_behind(self, remote, project):
        _git(project, "init", "-b", "main")
        _clone(remote, project)
        assert not (project / ".git_old").exists()
