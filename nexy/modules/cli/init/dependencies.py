import os
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

from nexy.helpers.common import package_manager
from nexy.helpers.common.console import console
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

    install_msg = (
        f"[yellow]nexy[/yellow] » {t('add.installing', 'Installing dependencies')}: "
        f"{', '.join(deps)}..."
    )
    with console.status(install_msg, spinner="dots"):
        try:
            subprocess.run(  # nosec B603 - resolved executable, fixed argv
                package_manager.add_argv(pm, deps),
                check=True,
                capture_output=True,
                cwd=dest,
            )
        except (OSError, subprocess.SubprocessError) as e:
            error_msg = (
                f"[red]{t('add.error', 'Error:')}[/red] "
                f"{t('add.install_failed', 'Failed to install dependencies')}: {e}"
            )
            console.print(error_msg)


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

    def _run(self, cmd: list[str], desc: str) -> bool:
        try:
            # Resolve the executable (npm.cmd/pnpm.cmd on Windows) instead of
            # using shell=True, which would let arguments inject commands.
            exe = shutil.which(cmd[0]) or cmd[0]
            subprocess.run(
                [exe, *cmd[1:]],
                cwd=self.directory,
                check=True,
                capture_output=True,
            )  # nosec B603
            return True
        except (OSError, subprocess.SubprocessError) as e:
            console.print(f"[red]nexy[/red] » {desc} failed")
            output = getattr(e, "stdout", None) or b""
            output += getattr(e, "stderr", None) or b""
            if output:
                console.print(output.decode("utf-8", errors="replace")[:500])
            else:
                console.print(f"[red]{e}[/red]")
            return False

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
        with console.status(
            "[yellow]nexy[/yellow] » Installing uv...",
            spinner="dots",
        ):
            self._run(
                [sys.executable, "-m", "pip", "install", "uv"],
                "uv installation",
            )

    def create_venv(self) -> None:
        if self.venv_dir.exists():
            return

        with console.status(
            "[yellow]nexy[/yellow] » Creating virtual environment...",
            spinner="dots",
        ):
            self._run(["uv", "venv", str(self.venv_dir)], "Virtual environment creation")

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

            with console.status(
                "[yellow]nexy[/yellow] » "
                + t("init.installing_node", "Installing Node.js dependencies..."),
                spinner="dots",
            ):
                ok = self._run(cmd, "Node.js dependencies installation")
                if not ok and pm == "npm":
                    console.print(
                        "[yellow]nexy[/yellow] » "
                        + t(
                            "init.node_retry",
                            "Retrying with --legacy-peer-deps...",
                        )
                    )
                    ok = self._run(
                        [*cmd, "--legacy-peer-deps"],
                        "Node.js dependencies installation (legacy-peer-deps)",
                    )
                if ok:
                    console.print(
                        "[green]nexy[/green] » "
                        + t(
                            "init.node_installed",
                            "Node.js dependencies installed with {pm}.",
                        ).format(pm=pm)
                    )

    def install_python_dependencies(self) -> None:
        pyproject = self.directory / "pyproject.toml"
        if not pyproject.exists():
            return

        with console.status(
            "[yellow]nexy[/yellow] » "
            + t("init.installing_python", "Installing Python dependencies..."),
            spinner="dots",
        ):
            self._run(["uv", "sync"], "Python dependencies installation")

    def install_orm(self) -> None:
        if not self.orm or self.orm == "None":
            return
        package = _ORM_PACKAGES.get(self.orm)
        if not package:
            return
        with console.status(
            f"[yellow]nexy[/yellow] » Installing {self.orm}...",
            spinner="dots",
        ):
            self._run(["uv", "add", package], f"{self.orm} installation")
            extras = _ORM_EXTRA_PACKAGES.get(self.orm, [])
            for extra in extras:
                self._run(["uv", "add", extra], f"{extra} installation")
            self._run(["uv", "add", "python-dotenv"], "python-dotenv installation")

    def _remove_egg_info(self) -> None:
        for item in self.directory.glob("**/*.egg-info"):
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
