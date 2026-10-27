from pathlib import Path
from typing import Any

from nexy.modules.cli import tui
from nexy.modules.i18n import t

from .questions import BACK, DONE, STEPS


def ask_project_name() -> str:
    """Prompt for a project name; Ctrl+C raises KeyboardInterrupt."""
    return str(tui.text(t("cli.new.prompt", "Project name:"), validate=validate_project_name))


def validate_project_name(name: str) -> bool | str:
    """Accept a valid, available project name or return the error message."""
    if not name.strip():
        return t("cli.new.error_empty", "Project name cannot be empty.")
    if not name[0].isalpha():
        return t("cli.new.error_letter", "Project name must start with a letter.")
    if not all(c.isalnum() or c in "-_" for c in name):
        return t("cli.new.error_chars", "Use only letters, numbers, hyphens, underscores.")
    if Path(name).exists():
        return t("cli.new.error_exists", "Directory '{name}' already exists.").format(name=name)
    return True


class ProjectPrompter:
    """Runs the questions of project initialization, in order.

    Each question answers done, skip (does not apply) or back. Going back returns to the last
    question that was actually asked, so skipped ones are never shown on the way.
    """

    def __init__(self) -> None:
        self.config: dict[str, Any] = {}

    def ask_all(self) -> dict[str, Any]:
        """Runs the full questionnaire and returns the configuration dictionary."""
        asked: list[int] = []
        position = 0
        while position < len(STEPS):
            outcome = STEPS[position](self.config)
            if outcome == BACK:
                position = asked.pop() if asked else position
                continue
            if outcome == DONE:
                asked.append(position)
            position += 1
        return self.config


__all__ = ["ProjectPrompter", "ask_project_name", "validate_project_name"]
