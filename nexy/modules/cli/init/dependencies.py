import os
import shutil
import sys
from pathlib import Path

from nexy.helpers.common import package_manager
from nexy.helpers.common.console import console
from nexy.helpers.common.tasks import run_task
from nexy.modules.i18n import t

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


def install_packages(deps: list[str], dest: Path | None = None) -> None:
    """Install node *deps* into *dest* with the detected package manager."""
    if not deps:
        return

    dest = (dest or Path(".")).resolve()
    pm = node_package_manager(dest)
    if pm is None:
        warning_msg = f"[yellow]{t('add.warning', 'Warning:')}[/yellow] " + t(
            "add.no_pm", "No package manager found. Please install dependencies manually:"
        )
        console.print(warning_msg + ", ".join(deps))
        return

    names = ", ".join(deps)
    result = run_task(
        f"{t('add.installing', 'Installing')} {names}",
        package_manager.add_argv(pm, deps),
        cwd=dest,
        done=f"{t('add.installed', 'Installed')} {names}",
    )
    if not result.ok:
        console.print(
            f"[red]{t('add.error', 'Error:')}[/red] "
            f"{t('add.install_failed', 'Failed to install dependencies')}"
        )


class DependencyInstaller:
    """Handles automatic installation of dependencies for different project types."""

    def __init__(self, directory: Path = Path("."), orm: str | None = None):
        self.directory = directory
        self.orm = orm
        self.is_windows = os.name == "nt"
        self.venv_dir = directory / ".venv"

    def _python(self) -> str:
        if self.is_windows:
            return str(self.venv_dir / "Scripts" / "python.exe")
        return str(self.venv_dir / "bin" / "python")

    def _run(self, cmd: list[str], label: str, done: str | None = None) -> bool:
        return run_task(label, cmd, cwd=self.directory, done=done).ok

    def install_all(self) -> None:
        self._install_uv()
        self.create_venv()
        self.install_node_dependencies()
        self.install_python_dependencies()
        self.install_orm()
        self._remove_egg_info()

    def _install_uv(self) -> None:
        if shutil.which("uv") is not None:
            return
        self._run([sys.executable, "-m", "pip", "install", "uv"], "Installing uv", "Installed uv")

    def create_venv(self) -> None:
        if self.venv_dir.exists():
            return

        self._run(
            ["uv", "venv", str(self.venv_dir)],
            "Creating virtual environment",
            "Created virtual environment",
        )

    def install_node_dependencies(self) -> None:
        package_json = self.directory / "package.json"
        vite_config = self.directory / "vite.config.ts"

        if package_json.exists() and vite_config.exists():
            pm = node_package_manager(self.directory)
            if pm is None:
                console.print(
                    "[yellow]nexy[/yellow] » "
                    + t(
                        "init.node_manager_not_found",
                        "No Node.js package manager found. Install bun, pnpm or npm.",
                    )
                )
                return
            cmd = package_manager.install_argv(pm, allow_builds=("esbuild",))

            label = t("init.installing_node", "Installing Node.js dependencies")
            done = t("init.node_installed", "Installed Node.js dependencies with {pm}").format(
                pm=pm
            )
            ok = self._run(cmd, label, done)
            if not ok and pm == "npm":
                console.print(
                    "[yellow]![/yellow] "
                    + t("init.node_retry", "Retrying with --legacy-peer-deps...")
                )
                self._run([*cmd, "--legacy-peer-deps"], label, done)

    def install_python_dependencies(self) -> None:
        pyproject = self.directory / "pyproject.toml"
        if not pyproject.exists():
            return

        self._run(
            ["uv", "sync"],
            t("init.installing_python", "Installing Python dependencies"),
            t("init.python_installed", "Installed Python dependencies"),
        )

    def install_orm(self) -> None:
        if not self.orm or self.orm == "None":
            return
        package = _ORM_PACKAGES.get(self.orm)
        if not package:
            return
        self._run(["uv", "add", package], f"Installing {self.orm}", f"Installed {self.orm}")
        for extra in _ORM_EXTRA_PACKAGES.get(self.orm, []):
            self._run(["uv", "add", extra], f"Installing {extra}", f"Installed {extra}")
        self._run(
            ["uv", "add", "python-dotenv"], "Installing python-dotenv", "Installed python-dotenv"
        )

    def _remove_egg_info(self) -> None:
        for item in self.directory.glob("**/*.egg-info"):
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
