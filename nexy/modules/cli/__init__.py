from collections.abc import Callable
from typing import Any

import typer

from nexy.__version__ import __version__
from nexy.helpers.common.console import console
from nexy.modules.cli.commands import build, check, dev, format_, init, start, test
from nexy.modules.cli.commands.migrate import migrate
from nexy.modules.cli.commands.new import new
from nexy.modules.cli.commands.skills import skills
from nexy.modules.cli.overview import print_overview
from nexy.modules.cli.terminal import keep_unicode_boxes, use_utf8_streams
from nexy.modules.i18n import t

use_utf8_streams()
keep_unicode_boxes()

VERSION = __version__

CLI = typer.Typer(
    help=t("cli.help", "Nexy CLI"),
    context_settings={"help_option_names": ["-h", "--help"]},
)


@CLI.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help=t("cli.help_version", "Show version")
    ),
) -> None:
    """Main entry point executed when no command is provided."""
    if version:
        console.print(f"[green]nexy[/green] {VERSION}")
        raise typer.Exit
    if ctx.invoked_subcommand is None:
        print_overview()


# (command, name when it is not the function's own, one-letter alias or None)
_COMMANDS: list[tuple[Callable[..., Any], str | None, str | None]] = [
    (dev, None, "d"),
    (start, None, "s"),
    (build, None, "b"),
    (check, None, "c"),
    (format_, "format", "f"),
    (test, None, None),
    (init, None, "i"),
    (new, None, "n"),
    (migrate, None, "m"),
    (skills, None, None),
]


def _register(app: typer.Typer) -> None:
    for command, name, alias in _COMMANDS:
        app.command(name=name)(command)
        if alias:
            app.command(name=alias, hidden=True)(command)


_register(CLI)

__all__ = ["CLI"]
