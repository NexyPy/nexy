import shutil
import sys
from pathlib import Path

import typer

from nexy.__version__ import __version__
from nexy.helpers.common.console import console
from nexy.modules.cli.init import InitProject, TemplateNotFoundError, template_source
from nexy.modules.cli.init.prompts import ask_project_name
from nexy.modules.i18n import t


def new(
    project_name: str | None = typer.Argument(
        None, help=t("cli.new.help_arg", "Name of the project to create (creates a new directory)")
    ),
    template: str | None = typer.Option(
        None,
        "--template",
        "-t",
        help=t(
            "cli.new.help_template",
            "Initialize from a registered template (e.g. web-fbr-react).",
        ),
    ),
) -> None:
    title = t("init.title", "nexy {version} {command}").format(version=__version__, command="new")
    console.print(title)

    if template:
        try:
            template_source(template)
        except TemplateNotFoundError:
            console.print(
                "[red]nexy[/red] » "
                + t("cli.new.template_unknown", "Unknown template '{template}'.").format(
                    template=template
                )
            )
            raise typer.Exit(code=1) from None

    created_dir: Path | None = None
    try:
        if not project_name:
            project_name = ask_project_name()
            if not project_name:
                return
        created_dir = Path(project_name).resolve()
        InitProject().run(
            template=template, project_dir=project_name, command="new", show_title=False
        )
    except KeyboardInterrupt:
        print()
        sys.exit(130)
    except Exception:
        if created_dir is not None and created_dir.exists():
            shutil.rmtree(created_dir, ignore_errors=True)
        raise
