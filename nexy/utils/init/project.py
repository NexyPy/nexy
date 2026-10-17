from pathlib import Path
from typing import Any

from nexy.__version__ import __version__
from nexy.i18n import t
from nexy.utils.common.console import console

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
    ) -> None:
        """Main execution flow for project initialization."""
        if project_dir:
            dest = Path(project_dir).resolve()
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest = Path(".").resolve()

        if show_title:
            title = t("init.title", "nexy {version} {command}").format(
                version=self.version, command=command
            )
            console.print(title)

        self._ensure_ready(dest, project_dir)

        if template:
            config: dict[str, Any] = {"orm": "None", "db_url": None}
            if template_source(template) == "github":
                initialize_from_template(
                    template, dest, config, use_github=True, subdir=f"templates/{template}"
                )
            else:
                initialize_from_template(template, dest, config)
            return

        config = ProjectPrompter().ask_all()
        template_name = TemplateResolver.resolve(config)
        initialize_from_template(template_name, dest, config)

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
            raise AlreadyInitializedError()
