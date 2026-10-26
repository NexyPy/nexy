import shutil
import sys
from collections.abc import Callable
from pathlib import Path

from nexy.helpers.common import package_manager
from nexy.helpers.common.console import console
from nexy.helpers.common.network import Connection, probe
from nexy.helpers.common.tasks import run_task
from nexy.modules.cli.init.connection import is_usable
from nexy.modules.i18n import t

from .databases import driver_packages

_ORM_PACKAGES: dict[str, str] = {
    "SQLModel": "sqlmodel",
    "SQLAlchemy": "sqlalchemy",
    "Tortoise-ORM": "tortoise-orm",
}

_ORM_EXTRA_PACKAGES: dict[str, list[str]] = {
    "Tortoise-ORM": ["aerich"],
}


def node_package_manager(dest: Path = Path(".")) -> str | None:
    """Detect the package manager for *dest*.

    A lockfile wins; otherwise the priority is bun, pnpm, then npm.
    """
    return package_manager.detect(dest)


def _no_package_manager(deps: list[str]) -> None:
    warning = f"[yellow]{t('add.warning', 'Warning:')}[/yellow] "
    message = t(
        "add.no_pm", "No package manager found. Please install dependencies manually: {names}"
    )
    console.print(warning + message.format(names=", ".join(deps)))


def install_packages(deps: list[str], dest: Path | None = None) -> None:
    """Install node *deps* into *dest* with the detected package manager."""
    if not deps:
        return
    dest = (dest or Path(".")).resolve()
    manager = node_package_manager(dest)
    if manager is None:
        _no_package_manager(deps)
        return
    names = ", ".join(deps)
    result = run_task(
        t("add.installing", "Installing {names}").format(names=names),
        package_manager.add_argv(manager, deps),
        cwd=dest,
        done=t("add.installed", "Installed {names}").format(names=names),
    )
    if not result.ok:
        error, failed = (
            t("add.error", "Error:"),
            t("add.install_failed", "Failed to install dependencies"),
        )
        console.print(f"[red]{error}[/red] {failed}")


def orm_packages(orm: str | None, database: str) -> list[str]:
    """The Python packages an ORM needs: the ORM, its tools, its database driver, dotenv."""
    package = _ORM_PACKAGES.get(orm or "")
    if not package:
        return []
    return [
        package,
        *_ORM_EXTRA_PACKAGES.get(orm or "", []),
        *driver_packages(database, orm or ""),
        "python-dotenv",
    ]


def _remove_egg_info(directory: Path) -> None:
    for item in directory.glob("**/*.egg-info"):
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)


class DependencyInstaller:
    """Handles automatic installation of dependencies for different project types."""

    def __init__(
        self,
        directory: Path = Path("."),
        orm: str | None = None,
        database: str = "none",
        probe: Callable[[], Connection] = probe,
    ):
        self.directory = directory
        self.orm = orm
        self.database = database
        self.probe = probe
        self._finished = 0
        self._total = 0
        self.venv_dir = directory / ".venv"

    def _run(self, cmd: list[str], label: str, done: str | None = None) -> bool:
        place = (self._finished, self._total) if self._total > 1 else None
        self._finished += 1
        return run_task(label, cmd, cwd=self.directory, done=done, progress=place).ok

    def _count_steps(self) -> int:
        """How many tasks `install_all` is about to run, for the progress bar."""
        steps = int(shutil.which("uv") is None) + int(not self.venv_dir.exists())
        steps += int(
            (self.directory / "package.json").exists()
            and (self.directory / "vite.config.ts").exists()
        )
        steps += int((self.directory / "pyproject.toml").exists())
        return steps + len(orm_packages(self.orm, self.database))

    def install_all(self) -> None:
        if not is_usable(self.probe()):
            return
        self._finished, self._total = 0, self._count_steps()
        self._install_uv()
        self.create_venv()
        self.install_node_dependencies()
        self.install_python_dependencies()
        self.install_orm()
        _remove_egg_info(self.directory)

    def _install_uv(self) -> None:
        if shutil.which("uv") is not None:
            return
        self._run(
            [sys.executable, "-m", "pip", "install", "uv"],
            t("init.installing_uv", "Installing uv"),
            t("init.installed_uv", "Installed uv"),
        )

    def create_venv(self) -> None:
        if self.venv_dir.exists():
            return
        self._run(
            ["uv", "venv", str(self.venv_dir)],
            t("init.venv.creating", "Creating virtual environment"),
            t("init.venv.created", "Created virtual environment"),
        )

    def install_node_dependencies(self) -> None:
        if not (
            (self.directory / "package.json").exists()
            and (self.directory / "vite.config.ts").exists()
        ):
            return
        manager = node_package_manager(self.directory)
        if manager is None:
            missing = t(
                "init.node_manager_not_found",
                "No Node.js package manager found. Install bun, pnpm or npm.",
            )
            console.print(f"[yellow]nexy[/yellow] » {missing}")
            return
        command = package_manager.install_argv(manager, allow_builds=("esbuild",))
        label = f"{manager} install node_modules"
        if not self._run(command, label, label) and manager == "npm":
            retry = t("init.node_retry", "Retrying with --legacy-peer-deps...")
            console.print(f"[yellow]![/yellow] {retry}")
            self._run([*command, "--legacy-peer-deps"], label, label)

    def install_python_dependencies(self) -> None:
        if (self.directory / "pyproject.toml").exists():
            self._run(["uv", "sync"], "uv sync .venv")

    def install_orm(self) -> None:
        for package in orm_packages(self.orm, self.database):
            self._run(["uv", "add", package], f"uv add .venv {package}")
