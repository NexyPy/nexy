"""Consistent, professional output for the Nexy command launcher.

The shape follows the launchers developers already know: one command header,
then a short list of aligned entries. Keep it free of emoji and decorative
noise; the terminal is a build log, not a marketing surface.
"""

from __future__ import annotations

from nexy.helpers.common.console import console

_BRAND = "[bold green]nexy[/bold green]"
_ARROW = "\u279c"


def banner(command: str, version: str) -> None:
    """Print the command header once."""
    console.print()
    console.print(f"{_BRAND} [dim]{version}[/dim]  [bold]{command}[/bold]")
    console.print()


def entry(label: str, value: str, style: str = "green") -> None:
    """Print one aligned launcher entry, for example ``Local  http://...``."""
    console.print(
        f"  [dim]{_ARROW}[/dim]  {label.rstrip(':') + ':':<10} [{style}]{value}[/{style}]"
    )


def step(command: str, description: str = "") -> None:
    """Print one next-step command with an optional dim description."""
    suffix = f"  [dim]{description}[/dim]" if description else ""
    console.print(f"  [dim]{_ARROW}[/dim]  [cyan]{command}[/cyan]{suffix}")


def success(message: str) -> None:
    """Print a green success line."""
    console.print(f"  [green]\u2713[/green] {message}")


def failure(message: str) -> None:
    """Print a red failure line."""
    console.print(f"  [red]\u2718[/red] {message}")
