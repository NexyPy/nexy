"""`nx skills`: add or refresh the agent files of a project."""

from pathlib import Path

import typer

from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.modules.cli.agents import detect_profile, install_agent_files
from nexy.modules.i18n import t


def _require_project(root: Path) -> None:
    if (root / "nexyconfig.py").is_file():
        return
    message = t(
        "cli.skills.not_a_project",
        "No nexyconfig.py in {path}: run this at the root of a Nexy project.",
    )
    console.print(tagged("nexy", message.format(path=root), "red"))
    raise typer.Exit(code=1)


def skills(
    path: Path = typer.Argument(
        Path("."),
        help=t("cli.skills.help_path", "Root of the project (default: the current folder)"),
    ),
) -> None:
    """Add or refresh the skills, AGENTS.md and CLAUDE.md for coding agents."""
    root = path.resolve()
    _require_project(root)
    report = install_agent_files(root, detect_profile(root))
    done = t("cli.skills.done", "{count} skills in .agents/skills and .claude/skills")
    console.print(tagged("nexy", done.format(count=len(report.skills))))
    if report.kept:
        kept = t("cli.skills.kept", "Kept your {files}.")
        console.print(tagged("nexy", kept.format(files=", ".join(report.kept))))
