import os
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

from nexy.helpers.common import package_manager
from nexy.helpers.common.console import console
from nexy.helpers.common.network import Connection, format_speed, probe, quality
from nexy.helpers.common.tasks import run_task
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


def install_packages(deps: list[str], dest: Path | None = None) -> None:
    """Install node *deps* into *dest* with the detected package manager."""
    if not deps:
        return

    dest = (dest or Path(".")).resolve()
    pm = node_package_manager(dest)
    if pm is None:
        warning_msg = f"[yellow]{t('add.warning', 'Warning:')}[/yellow] " + t(
            "add.no_pm", "No package manager found. Please install dependencies manually: {names}"
        )
        console.print(warning_msg.format(names=", ".join(deps)))
        return

    names = ", ".join(deps)
    result = run_task(
        t("add.installing", "Installing {names}").format(names=names),
        package_manager.add_argv(pm, deps),
        cwd=dest,
        done=t("add.installed", "Installed {names}").format(names=names),
    )
    if not result.ok:
        console.print(
            f"[red]{t('add.error', 'Error:')}[/red] "
            f"{t('add.install_failed', 'Failed to install dependencies')}"
        )


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
        self.is_windows = os.name == "nt"
        self.venv_dir = directory / ".venv"

    def _python(self) -> str:
        if self.is_windows:
            return str(self.venv_dir / "Scripts" / "python.exe")
        return str(self.venv_dir / "bin" / "python")

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
        if self.orm in _ORM_PACKAGES:
            steps += 2 + len(_ORM_EXTRA_PACKAGES.get(self.orm, []))
            steps += len(driver_packages(self.database, self.orm))
        return steps

    def install_all(self) -> None:
        if not self._network_is_usable():
            return
        self._finished, self._total = 0, self._count_steps()
        self._install_uv()
        self.create_venv()
        self.install_node_dependencies()
        self.install_python_dependencies()
        self.install_orm()
        self._remove_egg_info()

    def _network_is_usable(self) -> bool:
        """Look at the connection; say what it is, and skip the installs when there is none."""
        connection = self.probe()
        state = quality(connection)
        if state == "offline":
            console.print(
                "[yellow]![/yellow] "
                + t("init.network.offline", "No connection: packages were not installed.")
            )
            console.print(
                t(
                    "init.network.offline_hint",
                    "When you are online, run uv sync and your package manager's install "
                    "in the project folder.",
                )
            )
            return False
        console.print(self._connection_line(connection))
        if state == "slow":
            console.print(
                "[yellow]![/yellow] "
                + t("init.network.slow", "Slow connection: installing packages may take a while.")
            )
        return True

    @staticmethod
    def _connection_line(connection: Connection) -> str:
        latency = f"{connection.latency_ms:.0f}"
        if connection.speed_kbps is None:
            return t("init.network.latency", "Connection: {latency} ms").format(latency=latency)
        speed = format_speed(connection.speed_kbps)
        return t("init.network.speed", "Connection: {latency} ms, {speed}").format(
            latency=latency, speed=speed
        )

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

            label = f"{pm} install node_modules"
            ok = self._run(cmd, label, label)
            if not ok and pm == "npm":
                console.print(
                    "[yellow]![/yellow] "
                    + t("init.node_retry", "Retrying with --legacy-peer-deps...")
                )
                self._run([*cmd, "--legacy-peer-deps"], label, label)

    def install_python_dependencies(self) -> None:
        pyproject = self.directory / "pyproject.toml"
        if not pyproject.exists():
            return

        self._run(["uv", "sync"], "uv sync .venv")

    def install_orm(self) -> None:
        if not self.orm or self.orm == "None":
            return
        package = _ORM_PACKAGES.get(self.orm)
        if not package:
            return
        self._add(package)
        for extra in _ORM_EXTRA_PACKAGES.get(self.orm, []):
            self._add(extra)
        for driver in driver_packages(self.database, self.orm):
            self._add(driver)
        self._add("python-dotenv")

    def _add(self, package: str) -> bool:
        return self._run(["uv", "add", package], f"uv add .venv {package}")

    def _remove_egg_info(self) -> None:
        for item in self.directory.glob("**/*.egg-info"):
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
