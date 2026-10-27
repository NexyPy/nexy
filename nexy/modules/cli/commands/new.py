import shutil
import sys
from pathlib import Path

import typer
from rich.markup import escape

from nexy.__version__ import __version__
from nexy.helpers.common import launcher
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.modules.cli.init import InitProject, TemplateNotFoundError, template_source
from nexy.modules.cli.init.prompts import ask_project_name
from nexy.modules.i18n import t


def _require_known_template(template: str) -> None:
    """Stop with code 1 when *template* is not a registered one."""
    try:
        template_source(template)
    except TemplateNotFoundError:
        message = t("cli.new.template_unknown", "Unknown template '{template}'.")
        console.print(tagged("nexy", message.format(template=template), "red"))
        raise typer.Exit(code=1) from None


def _report_failure(error: Exception, created: Path | None) -> typer.Exit:
    """Remove the half-made project, say why it failed, and give the exit to raise."""
    if created is not None and created.exists():
        shutil.rmtree(created, ignore_errors=True)
    reason = escape(str(error)) or type(error).__name__
    console.print()
    console.print(f"[red]x[/red] {t('cli.new.failed', 'Could not create the project')}")
    console.print(f"  [dim]{reason}[/dim]")
    return typer.Exit(code=1)


def _scaffold(project_name: str, template: str | None, agents: bool) -> None:
    """Create the project in its own folder, without the banner `new` already printed."""
    InitProject().run(
        template=template,
        project_dir=project_name,
        command="new",
        show_title=False,
        agents=agents,
    )


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
    agents: bool = typer.Option(
        True,
        "--agents/--no-agents",
        help=t("cli.new.help_agents", "Add AGENTS.md and the skills for coding agents."),
    ),
) -> None:
    launcher.banner("new", __version__)
    if template:
        _require_known_template(template)
    created: Path | None = None
    try:
        project_name = project_name or ask_project_name()
        if not project_name:
            return
        created = Path(project_name).resolve()
        _scaffold(project_name, template, agents)
    except KeyboardInterrupt:
        print()
        sys.exit(130)
    except typer.Exit:
        raise
    except Exception as error:
        raise _report_failure(error, created) from None
