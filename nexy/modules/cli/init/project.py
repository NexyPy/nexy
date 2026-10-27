from pathlib import Path
from typing import Any

from nexy.__version__ import __version__
from nexy.helpers.common import launcher
from nexy.helpers.common.console import console
from nexy.modules.cli import tui
from nexy.modules.i18n import t

from .prompts import ProjectPrompter
from .registry import template_source
from .resolver import TemplateResolver
from .template_setup import initialize_from_template


class AlreadyInitializedError(Exception):
    """Raised when the target directory already contains a Nexy project."""


class InitProject:
    """Orchestrates the project initialization process."""

    def __init__(self) -> None:
        self.version = __version__

    def run(
        self,
        template: str | None = None,
        project_dir: str | None = None,
        command: str = "init",
        show_title: bool = True,
        agents: bool = True,
    ) -> None:
        """Main execution flow for project initialization."""
        dest = self._destination(project_dir)
        if show_title:
            launcher.banner(command, self.version)
        self._ensure_ready(dest, project_dir)
        if template:
            self._from_template(template, dest, agents)
            return
        config = ProjectPrompter().ask_all()
        config["agents"] = agents
        tui.transcript.erase_all()
        initialize_from_template(TemplateResolver.resolve(config), dest, config)

    @staticmethod
    def _destination(project_dir: str | None) -> Path:
        dest = Path(project_dir or ".").resolve()
        if project_dir:
            dest.mkdir(parents=True, exist_ok=True)
        return dest

    @staticmethod
    def _from_template(template: str, dest: Path, agents: bool = True) -> None:
        config: dict[str, Any] = TemplateResolver.config_for(template)
        config["agents"] = agents
        if template_source(template) == "github":
            initialize_from_template(
                template, dest, config, use_github=True, subdir=f"templates/{template}"
            )
        else:
            initialize_from_template(template, dest, config)

    def _ensure_ready(self, dest: Path, project_dir: str | None) -> None:
        """Guard against initializing inside an existing Nexy project.

        Skipped when a fresh project directory was created (`new` command).
        """
        if project_dir:
            return

        already = (
            (dest / "__nexy__").exists()
            or (dest / "nexyconfig.py").exists()
            or (dest / "vite.config.ts").exists()
        )
        if already:
            console.print(
                "[red]nexy[/red] » " + t("init.already", "Project already initialized here")
            )
            raise AlreadyInitializedError
