"""Putting the project's own `.git` aside while a template is fetched, and putting it back."""

from __future__ import annotations

import shutil
from pathlib import Path

from nexy.helpers.common.console import console
from nexy.helpers.fs.tree import remove_tree
from nexy.modules.i18n import t


class GitBackup:
    """Moves `.git` to `.git_old` of *root* and back."""

    def __init__(self, root: Path = Path(".")) -> None:
        self._git = root / ".git"
        self._backup = root / ".git_old"

    def stash(self) -> bool:
        """Set the history aside; True when there was one and it is now in the backup."""
        if self._backup.exists():
            remove_tree(self._backup)
        if not self._git.exists():
            return False
        try:
            self._git.rename(self._backup)
        except OSError:
            return self._copy_then_remove()
        return True

    def _copy_then_remove(self) -> bool:
        """The fallback when a rename is refused (a locked folder): copy, then delete."""
        try:
            shutil.copytree(self._git, self._backup, dirs_exist_ok=True)
            remove_tree(self._git)
        except (OSError, shutil.Error):
            return False
        return True

    def restore(self) -> None:
        """Bring the history back; the template's own `.git` is discarded."""
        if not self._backup.exists():
            return
        if self._git.exists():
            remove_tree(self._git)
        try:
            self._backup.rename(self._git)
        except OSError:
            self._copy_back()

    def _copy_back(self) -> None:
        try:
            shutil.copytree(self._backup, self._git, dirs_exist_ok=True)
            remove_tree(self._backup)
        except (OSError, shutil.Error):
            # Best effort: the destination .git stays untouched, so a failed restore cannot
            # corrupt the project.
            warning = t("init.git_restore", "could not restore previous .git")
            console.print(f"  [yellow]⚠[/yellow] {warning}")
