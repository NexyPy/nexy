"""Shared CLI guard: refuse to run a project whose configuration contradicts itself."""

import sys

from nexy.core.config import Config
from nexy.core.project_rules import project_problems
from nexy.helpers.common.console import console


def abort_on_invalid_config() -> None:
    """Print the configuration error and exit instead of starting a broken server."""
    try:
        Config().require_valid()
    except ValueError as exc:
        console.print(f"[red]nexy[/red] \u00bb {exc}")
        sys.exit(1)
    problems = project_problems()
    if problems:
        for problem in problems:
            console.print(f"[red]nexy[/red] \u00bb {problem}")
        sys.exit(1)
