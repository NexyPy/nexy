"""Rules for coding agents, installed into a project: skills, AGENTS.md and CLAUDE.md."""

from nexy.modules.cli.agents.catalog import select_skills
from nexy.modules.cli.agents.installer import Report, install_agent_files
from nexy.modules.cli.agents.profile import Profile, detect_profile, profile_from_context
from nexy.modules.cli.agents.source import skills_source

__all__ = [
    "Profile",
    "Report",
    "detect_profile",
    "install_agent_files",
    "profile_from_context",
    "select_skills",
    "skills_source",
]
