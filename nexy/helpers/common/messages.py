"""Messages of the command line, in the shape uv gives them: ``error: ...``, ``warning: ...``.

The keyword stays English and bold, as in uv, cargo and rustc, so a log reads the same in every
language and a search finds it; the message after it is the translated text.
"""

from __future__ import annotations

from rich.console import Console

from nexy.helpers.common.console import console as _console
from nexy.modules.i18n import t


def _say(keyword: str, colour: str, message: str, console: Console | None) -> None:
    (console or _console).print(f"[bold {colour}]{keyword}[/bold {colour}][bold]:[/bold] {message}")


def error(message: str, cause: str | None = None, console: Console | None = None) -> None:
    """``error: message``, then ``  cause: ...`` when the failure has one."""
    _say("error", "red", message, console)
    if cause:
        (console or _console).print(f"  [bold red]cause[/bold red][bold]:[/bold] {cause}")


def warning(message: str, console: Console | None = None) -> None:
    """``warning: message``: the command goes on, but something needs a look."""
    _say("warning", "yellow", message, console)


def hint(message: str, console: Console | None = None) -> None:
    """``hint: message``: what to do next."""
    _say("hint", "cyan", message, console)


def took(message: str, duration: str) -> str:
    """Markup for a finished step: ``Installed zod in 1.2s``, the duration dim."""
    return f"{message} [dim]{t('cli.took', 'in {duration}').format(duration=duration)}[/dim]"
