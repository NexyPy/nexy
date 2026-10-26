"""The shape of a line in the dev log: ``LABEL » message``, as for ``GET »`` and ``vite »``."""

from __future__ import annotations


def tag(label: str, colour: str = "dim") -> str:
    """Rich markup for the start of a log line: the label in *colour*, then a dim ``»``."""
    return f"[{colour}]{label}[/{colour}] [dim]»[/dim]"


def tagged(label: str, message: str, colour: str = "dim") -> str:
    """Rich markup for a whole log line; *message* is used as given, escape it first."""
    return f"{tag(label, colour)} {message}"
