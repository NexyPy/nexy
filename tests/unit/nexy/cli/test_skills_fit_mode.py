"""The agent files a project gets speak only of its own mode (#605, #607).

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
    "server-md": Profile("demo", "none", False, "tailwind", nexy_files=False),
    "server-react-tsx": Profile("demo", "react", False, "tailwind", nexy_files=False),
    "api-fbr": Profile("demo", "none", False, "vanilla", kind="api"),
    "api-modular": Profile("demo", "none", False, "vanilla", kind="api", router="modular"),
}
FRAMEWORKS = ("react", "vue", "svelte", "solid", "preact")
STYLES = ("tailwind", "unocss", "vanilla")


def _installed_text(root: Path, name: str | Profile) -> str:
    install_agent_files(root, PROFILES[name] if isinstance(name, str) else name)
    files = [root / "AGENTS.md", *root.glob(".agents/skills/**/*.md")]
    files += root.glob(".claude/skills/**/*.md")
    return "\n".join(path.read_text(encoding="utf-8") for path in files)


@pytest.mark.parametrize(
    "name", ["client-react", "api-fbr", "api-modular", "server-md", "server-react-tsx"]
)
def test_a_project_without_nexy_files_is_never_told_about_them(tmp_path, name):
    assert re.findall(r"\.nexy\b", _installed_text(tmp_path, name)) == []


@pytest.mark.parametrize("name", ["api-fbr", "api-modular"])
def test_an_api_project_is_never_told_about_islands(tmp_path, name):
    assert re.findall(r"(?i)\bislands?\b", _installed_text(tmp_path, name)) == []


@pytest.mark.parametrize("style", STYLES)
@pytest.mark.parametrize("framework", FRAMEWORKS)
def test_a_client_routed_project_of_any_stack_is_never_told_about_nexy_files(
    tmp_path, framework, style
):
    profile = Profile("demo", framework, True, style)
    assert re.findall(r"\.nexy\b", _installed_text(tmp_path, profile)) == []


@pytest.mark.parametrize("name", ["server", "server-react"])
def test_a_server_project_is_never_told_to_route_in_the_browser(tmp_path, name):
    assert "useCSR = True" not in _installed_text(tmp_path, name)


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
    pairs = list(zip(markers[0::2], markers[1::2], strict=False))
    assert len(markers) % 2 == 0 and all(
        not opening[0] and closing == ("/", opening[1]) and opening[1] in TAGS
        for opening, closing in pairs
    )


def test_a_project_without_nexy_files_gets_no_nexy_file_skill(tmp_path):
    _installed_text(tmp_path, "server-react-tsx")
    assert not (tmp_path / ".agents/skills/nexy-file").exists()


def test_a_server_project_without_nexy_files_still_learns_its_error_pages(tmp_path):
    assert "notfound.tsx" in _installed_text(tmp_path, "server-react-tsx")
