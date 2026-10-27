"""Writes the skills and the agent files into a project, and never overwrites the project's own."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from nexy.modules.cli.agents.catalog import NEVER_SHIPPED, select_skills
from nexy.modules.cli.agents.document import CLAUDE_MD, render_agents_md
from nexy.modules.cli.agents.profile import Profile
from nexy.modules.cli.agents.source import skills_source

# Claude Code reads .claude/skills; Codex reads .agents/skills; OpenCode reads both.
TARGETS = (".agents/skills", ".claude/skills")


@dataclass
class Report:
    """What an installation did."""

    skills: list[str] = field(default_factory=list)
    written: list[str] = field(default_factory=list)
    kept: list[str] = field(default_factory=list)


def _shipped(source: Path) -> set[str]:
    return {path.parent.name for path in source.glob("*/SKILL.md")} - set(NEVER_SHIPPED)


def _install_into(folder: Path, source: Path, chosen: list[str]) -> None:
    """Refresh the Nexy skills of *folder*; a skill of the project itself is left alone."""
    folder.mkdir(parents=True, exist_ok=True)
    for name in _shipped(source) - set(chosen):
        shutil.rmtree(folder / name, ignore_errors=True)
    for name in chosen:
        shutil.rmtree(folder / name, ignore_errors=True)
        shutil.copytree(source / name, folder / name)


def _write_once(path: Path, text: str, report: Report) -> None:
    if path.exists():
        report.kept.append(path.name)
        return
    path.write_text(text, encoding="utf-8", newline="\n")
    report.written.append(path.name)


def install_agent_files(dest: Path, profile: Profile) -> Report:
    """Install the skills that fit *profile*, then AGENTS.md and CLAUDE.md when they are absent."""
    source = skills_source()
    chosen = select_skills(profile)
    for target in TARGETS:
        _install_into(dest / target, source, chosen)
    report = Report(skills=chosen)
    _write_once(dest / "AGENTS.md", render_agents_md(profile, source, chosen), report)
    _write_once(dest / "CLAUDE.md", CLAUDE_MD, report)
    return report
