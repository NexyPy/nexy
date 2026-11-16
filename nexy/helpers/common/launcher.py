"""Consistent, professional output for the Nexy command launcher.

The shape follows uv: one command header, then short aligned lines of plain text. No arrow, no
check mark and no emoji; the terminal is a build log, not a marketing surface.
"""

from __future__ import annotations

from nexy.helpers.common.console import console

_BRAND = "[bold green]nexy[/bold green]"


def banner(command: str, version: str) -> None:
    """Print the command header once."""
    console.print()
    console.print(f"{_BRAND} [dim]{version}[/dim]  [bold]{command}[/bold]")
    console.print()


def entry(label: str, value: str, style: str = "green") -> None:
    """Print one aligned launcher entry, for example ``Local:     http://...``."""
    console.print(f"  {label.rstrip(':') + ':':<10} [{style}]{value}[/{style}]")


def step(command: str, description: str = "", width: int = 0) -> None:
    """Print one next-step command with an optional dim description.

    *width* pads the command, so the descriptions of a list line up as uv's help does.
    """
    if not description:
        console.print(f"  [cyan]{command}[/cyan]")
        return
    console.print(f"  [cyan]{command:<{width}}[/cyan]  [dim]{description}[/dim]")
