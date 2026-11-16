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


def step(command: str, description: str = "") -> None:
    """Print one next-step command with an optional dim description."""
    suffix = f"  [dim]{description}[/dim]" if description else ""
    console.print(f"  [cyan]{command}[/cyan]{suffix}")
