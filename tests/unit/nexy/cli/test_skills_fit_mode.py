"""The agent files a project gets speak only of its own mode (#605).

A client-routed project has no `.nexy` file and an API project has no view at all: neither is
told about them. The check reads what is installed, not the sources in `skills/`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from nexy.modules.cli.agents import Profile, install_agent_files, skills_source
from nexy.modules.cli.agents.sections import MARKER, TAGS

PROFILES = {
    "server": Profile("demo", "none", False, "tailwind"),
    "server-react": Profile("demo", "react", False, "tailwind"),
    "client-react": Profile("demo", "react", True, "tailwind"),
    "api-fbr": Profile("demo", "none", False, "vanilla", kind="api"),
    "api-modular": Profile("demo", "none", False, "vanilla", kind="api", router="modular"),
}


def _installed_text(root: Path, name: str) -> str:
    install_agent_files(root, PROFILES[name])
    files = [root / "AGENTS.md", *root.glob(".agents/skills/**/*.md")]
    files += root.glob(".claude/skills/**/*.md")
    return "\n".join(path.read_text(encoding="utf-8") for path in files)


@pytest.mark.parametrize("name", ["client-react", "api-fbr", "api-modular"])
def test_a_project_without_nexy_files_is_never_told_about_them(tmp_path, name):
    assert re.findall(r"\.nexy\b", _installed_text(tmp_path, name)) == []


@pytest.mark.parametrize("name", ["api-fbr", "api-modular"])
def test_an_api_project_is_never_told_about_islands(tmp_path, name):
    assert re.findall(r"(?i)\bislands?\b", _installed_text(tmp_path, name)) == []


def test_a_server_project_still_learns_the_nexy_files(tmp_path):
    assert ".nexy" in _installed_text(tmp_path, "server")


@pytest.mark.parametrize("name", list(PROFILES))
def test_no_marker_reaches_a_project(tmp_path, name):
    assert "<!-- nexy:" not in _installed_text(tmp_path, name)


def _markers(path: Path) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [(m[1], m[2]) for m in (MARKER.match(line.strip()) for line in lines) if m]


@pytest.mark.parametrize("path", sorted(skills_source().rglob("*.md")), ids=lambda p: p.parent.name)
def test_every_marker_of_a_skill_is_known_and_closed(path):
    markers = _markers(path)
    opened = [tag for slash, tag in markers[0::2] if not slash]
    closed = [tag for slash, tag in markers[1::2] if slash]
    assert (opened == closed and set(opened) <= set(TAGS)) and len(markers) % 2 == 0
