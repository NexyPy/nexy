"""Fetching a template from a Git repository into a project folder."""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
from pathlib import Path

from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.fs.tree import remove_path, remove_tree
from nexy.modules.cli.init.git_backup import GitBackup
from nexy.modules.i18n import t

_NOT_TEMPLATE_CONTENT = {"build", "dist", ".venv", "node_modules", "__pycache__"}
_REPOSITORY_FILES = (".git", ".github")
_GIT_FETCH_NOT_FOUND = 128


class TemplateError(Exception):
    """The template could not be fetched or extracted; the message says what to do."""


def _git(dest: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=dest.as_posix(),
        capture_output=True,
        text=True,
        check=True,
    )  # nosec B603 B607 - fixed git argv; the repository and path come from the user's own choice


def _is_fresh(dest: Path) -> bool:
    """True when nothing but the backup of the history, or a virtual environment, is there."""
    names = [entry.name for entry in dest.iterdir() if entry.name != ".git_old"]
    return not names or names == [".venv"]


def _fetch(dest: Path, repo: str, branch: str) -> None:
    _git(dest, "init")
    _git(dest, "remote", "add", "origin", repo)
    try:
        _git(dest, "fetch", "--depth=1", "origin", branch)
    except subprocess.CalledProcessError as error:
        if error.returncode != _GIT_FETCH_NOT_FOUND:
            raise
        message = t("init.template_not_found", "Template or branch '{branch}' not found on remote.")
        raise TemplateError(message.format(branch=branch)) from error


def _extract(dest: Path, path: str, fresh: bool) -> None:
    """Check *path* of the fetched template out; into a folder with files, merge instead."""
    steps = [["checkout", "FETCH_HEAD", "--", path]]
    if not fresh:
        console.print(
            tagged("nexy", t("init.merging", "Directory not empty, merging files..."), "yellow")
        )
        steps += [["merge", "--ff-only", "FETCH_HEAD"], ["reset", "--hard"]]
    try:
        for step in steps:
            _git(dest, *step)
    except subprocess.CalledProcessError as error:
        message = t("init.checkout_failed", "Failed to extract files from template '{path}'.")
        raise TemplateError(message.format(path=path)) from error


def _relocate(item: Path, root: Path) -> None:
    """Move *item* up to *root*, replacing what is there; dependency folders are dropped."""
    if item.name in _NOT_TEMPLATE_CONTENT:
        remove_path(item)
        return
    target = root / item.name
    if target.exists():
        remove_path(target)
    shutil.move(str(item), str(root))


def _prune_empty_parents(start: Path, root: Path) -> None:
    """Delete *start* and the folders above it that the move left empty, up to *root*."""
    current = start
    while current != root:
        parent = current.parent
        shutil.rmtree(current, ignore_errors=True)
        current = parent
        if any(current.iterdir()):
            break


def _move_subdir_to_root(root: Path, subdir: Path) -> None:
    """Move the contents of *subdir* to *root*, then remove the folders that held them."""
    source = root / subdir
    if not source.exists():
        return
    for item in source.iterdir():
        _relocate(item, root)
    _prune_empty_parents(source, root)


def _remove_repository_files(dest: Path) -> None:
    """Cut every link with the remote: the template's `.git`, and its CI configuration."""
    for name in _REPOSITORY_FILES:
        if (dest / name).exists():
            remove_tree(dest / name)


class GitClone:
    def __init__(self) -> None:
        self.repo = "https://github.com/NexyPy/nexy.git"
        # GitHub retired `master`: `nexy new -t <github-template>` must fetch
        # the repository's actual default branch or every lookup fails.
        self.branch = "main"
        self.dest = Path(".")

    def clone(self, repo: str, branch: str, dest: Path, subdir: str | None = None) -> None:
        """Clone the template. With *subdir*, only that directory's contents end up in *dest*."""
        backup = GitBackup(Path("."))
        had_history = backup.stash()
        try:
            fresh = _is_fresh(dest)
            _fetch(dest, repo, branch)
            _extract(dest, subdir or ".", fresh)
            if subdir:
                _move_subdir_to_root(dest, Path(subdir))
        finally:
            _remove_repository_files(dest)
            if had_history:
                backup.restore()
