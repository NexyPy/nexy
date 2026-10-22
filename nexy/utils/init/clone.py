import os
import shutil
import stat
import subprocess  # nosec B404
from collections.abc import Callable
from pathlib import Path
from typing import Any

from nexy.i18n import t
from nexy.utils.common.console import console


class GitClone:
    def __init__(self) -> None:
        self.repo = "https://github.com/NexyPy/nexy.git"
        self.branch = "master"
        self.dest = Path(".")

    def _is_empty_dir(self, path: Path) -> bool:
        return not any(path.iterdir())

    def clone(self, repo: str, branch: str, dest: Path, subdir: str | None = None) -> None:
        """Clones the template. If subdir is provided, extracts only that directory's contents."""
        has_user_git = self._stash_git_repo()

        try:
            is_empty = self._is_empty_dir(dest)
            has_only_venv = False
            if not is_empty:
                items = [i for i in dest.iterdir() if i.name != ".git_old"]
                if len(items) == 0:
                    is_empty = True
                elif len(items) == 1 and items[0].name == ".venv":
                    has_only_venv = True

            init_cmds = [
                ["git", "init"],
                ["git", "remote", "add", "origin", repo],
                ["git", "fetch", "--depth=1", "origin", branch],
            ]
            for cmd in init_cmds:
                try:
                    subprocess.run(
                        cmd,
                        cwd=dest.as_posix(),
                        capture_output=True,
                        text=True,
                        check=True,
                    )  # nosec B603 - fixed git argv, repo URL from user's own template choice
                except subprocess.CalledProcessError as e:
                    if "fetch" in cmd and e.returncode == 128:
                        raise Exception(
                            t(
                                "init.template_not_found",
                                "Template or branch '{branch}' not found on remote.",
                            ).format(branch=branch)
                        ) from e
                    raise e

            checkout_path = subdir if subdir else "."

            if is_empty or has_only_venv:
                checkout_cmd = ["git", "checkout", "FETCH_HEAD", "--", checkout_path]
                try:
                    subprocess.run(
                        checkout_cmd,
                        cwd=dest.as_posix(),
                        capture_output=True,
                        text=True,
                        check=True,
                    )  # nosec B603 - fixed git argv, path from the template manifest
                except subprocess.CalledProcessError as e:
                    raise Exception(
                        t(
                            "init.checkout_failed",
                            "Failed to extract files from template '{path}'.",
                        ).format(path=checkout_path)
                    ) from e

                if subdir:
                    self._move_subdir_to_root(dest, Path(subdir))
            else:
                console.print(
                    "[yellow]nexy[/yellow] » "
                    + t("init.merging", "Directory not empty, merging files...")
                )
                merge_cmds = [
                    ["git", "checkout", "FETCH_HEAD", "--", checkout_path],
                    ["git", "merge", "--ff-only", "FETCH_HEAD"],
                    ["git", "reset", "--hard"],
                ]
                for cmd in merge_cmds:
                    try:
                        subprocess.run(
                            cmd,
                            cwd=dest.as_posix(),
                            capture_output=True,
                            text=True,
                            check=True,
                        )  # nosec B603 - fixed git argv
                    except subprocess.CalledProcessError as e:
                        raise Exception(
                            t(
                                "init.checkout_failed",
                                "Failed to extract files from template '{path}'.",
                            ).format(path=checkout_path)
                        ) from e

                if subdir:
                    self._move_subdir_to_root(dest, Path(subdir))

        finally:
            self._cleanup_git(dest)

            if has_user_git:
                self._restore_git_repo()

    def _move_subdir_to_root(self, root: Path, subdir: Path) -> None:
        """Moves all contents from a subdirectory to the root and removes the subdirectory."""
        source = root / subdir
        if not source.exists():
            return

        excluded = ["build", "dist", ".venv", "node_modules", "__pycache__"]

        for item in source.iterdir():
            if item.name in excluded:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink()
                continue

            target = root / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target, ignore_errors=True)
                else:
                    target.unlink()
            shutil.move(str(item), str(root))

        current = source
        while current != root:
            parent = current.parent
            shutil.rmtree(current, ignore_errors=True)
            current = parent
            if any(current.iterdir()):
                break

    def _cleanup_git(self, dest: Path) -> None:
        """Removes the .git directory to cut any link with the remote repository."""

        def on_rm_error(
            func: Callable[[str], Any], path: str, _exc_info: tuple[object, ...]
        ) -> None:
            os.chmod(path, stat.S_IWRITE)
            func(path)

        gitdir = dest / ".git"
        if gitdir.exists():
            shutil.rmtree(gitdir, onerror=on_rm_error)

        githubdir = dest / ".github"
        if githubdir.exists():
            shutil.rmtree(githubdir, onerror=on_rm_error)

    def _stash_git_repo(self) -> bool:
        """Backs up the existing .git directory to .git_old."""
        root = Path(".")
        gitdir = root / ".git"
        backup = root / ".git_old"

        if backup.exists():

            def on_rm_error(
                func: Callable[[str], Any], path: str, _exc_info: tuple[object, ...]
            ) -> None:
                os.chmod(path, stat.S_IWRITE)
                func(path)

            shutil.rmtree(backup, onerror=on_rm_error)

        if gitdir.exists():
            try:
                gitdir.rename(backup)
                return True
            except Exception:
                try:
                    shutil.copytree(gitdir, backup, dirs_exist_ok=True)

                    def on_rm_error(
                        func: Callable[[str], Any], path: str, _exc_info: tuple[object, ...]
                    ) -> None:
                        os.chmod(path, stat.S_IWRITE)
                        func(path)

                    shutil.rmtree(gitdir, onerror=on_rm_error)
                    return True
                except Exception:
                    return False
        return False

    def _restore_git_repo(self) -> None:
        """Restores the .git directory from .git_old and deletes the backup."""
        root = Path(".")
        gitdir = root / ".git"
        backup = root / ".git_old"

        if backup.exists():
            if gitdir.exists():
                self._cleanup_git(root)

            try:
                backup.rename(gitdir)
            except Exception:

                def on_rm_error(
                    func: Callable[[str], Any], path: str, _exc_info: tuple[object, ...]
                ) -> None:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)

                try:
                    shutil.copytree(backup, gitdir, dirs_exist_ok=True)
                    shutil.rmtree(backup, onerror=on_rm_error)
                except (OSError, shutil.Error):
                    # Backup restore is best-effort: the destination .git stays
                    # untouched, so a failed restore cannot corrupt the project.
                    warn = t("init.git_restore", "could not restore previous .git")
                    console.print(f"  [yellow]\u26a0[/yellow] {warn}")
