"""What `nx` prints when it is run without a command: the version and the commands."""

from __future__ import annotations

from nexy.__version__ import __version__
from nexy.helpers.common.console import console
from nexy.modules.i18n import t


def _commands() -> list[tuple[str, str]]:
    """(usage, description) of each command, in the order they are shown."""
    return [
        (
            "new [dim]<project-name>[/dim]",
            t("cli.cmd.new", "Create a new project in a new directory"),
        ),
        ("init", t("cli.cmd.init", "Initialize Nexy in the current directory")),
        ("dev", t("cli.cmd.dev", "Start local development server with hot reload")),
        ("start", t("cli.cmd.start", "Start production server")),
        ("build", t("cli.cmd.build", "Compile project for production deployment")),
        ("check", t("cli.cmd.check", "Run type checking across all project files")),
        ("format", t("cli.cmd.format", "Auto-format all project files")),
        ("test", t("cli.cmd.test", "Run tests (--server / --client)")),
        ("migrate", t("cli.cmd.migrate", "Run ORM migrations (auto-detects ORM)")),
    ]


def _print_commands() -> None:
    commands = _commands()
    width = max(len(usage) for usage, _ in commands)
    for usage, description in commands:
        console.print(f"  [yellow]{usage.ljust(width)}[/yellow]  {description}")


def print_overview() -> None:
    tagline = t("cli.tagline", "The modern full-stack framework that just works")
    header = t("cli.commands_header", "Available Commands:")
    usage = t("cli.usage", "Run nx or nexy <command> --help for detailed usage")
    console.print()
    console.print(f"[bold green]nexy[/bold green] [dim]{__version__}[/dim]")
    console.print()
    console.print(f"[italic]{tagline}[/italic]")
    console.print()
    console.print(f"[bold cyan]{header}[/bold cyan]")
    _print_commands()
    console.print()
    console.print(f"[dim]{usage}[/dim]")
    console.print()
