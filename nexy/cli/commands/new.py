import sys
from pathlib import Path

import questionary
import typer

from nexy.__version__ import __Version__
from nexy.i18n import t
from nexy.utils.common.console import console
from nexy.utils.init import InitProject


def new(
    project_name: str | None = typer.Argument(
        None, help=t("cli.new.help_arg", "Name of the project to create (creates a new directory)")
    ),
    template: str | None = typer.Option(
        None,
        "--template",
        "-t",
        help=t("cli.new.help_template", "Initialize from a registered template (silent clone)."),
    ),
) -> None:
    title = t("init.title", "nexy {version} {command}").format(
        version=__Version__().get(), command="new"
    )
    console.print(title)

    try:
        if not project_name:
            project_name = _ask_project_name()
            if not project_name:
                return
        InitProject().run(
            template=template, project_dir=project_name, command="new", show_title=False
        )
    except KeyboardInterrupt:
        print()
        sys.exit(130)


def _ask_project_name() -> str | None:
    name = questionary.text(
        t("cli.new.prompt", "Project name:"),
        qmark="»",
        validate=lambda val: _validate_name(val),
    ).ask()
    if name is None:
        return None
    return name or _ask_project_name()


def _validate_name(name: str) -> bool | str:
    if not name.strip():
        return t("cli.new.error_empty", "Project name cannot be empty.")
    if not name[0].isalpha():
        return t("cli.new.error_letter", "Project name must start with a letter.")
    if not all(c.isalnum() or c in "-_" for c in name):
        return t("cli.new.error_chars", "Use only letters, numbers, hyphens, underscores.")
    if Path(name).exists():
        return t("cli.new.error_exists", "Directory '{name}' already exists.").format(name=name)
    return True
