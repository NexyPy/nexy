"""A skill reaches a project with only the parts that fit its mode."""

from __future__ import annotations

from pathlib import Path

from nexy.modules.cli.agents import Profile
from nexy.modules.cli.agents.sections import fit, fit_tree, modes_of

SKILL = """# Title

Shared line.

<!-- nexy:server -->
Server line.
<!-- /nexy:server -->

<!-- nexy:client -->
Client line.
<!-- /nexy:client -->

<!-- nexy:web -->
Web line.
<!-- /nexy:web -->

Last line.
"""
SERVER = {"web", "server"}
CLIENT = {"web", "client"}


def test_untagged_text_reaches_every_project():
    assert "Shared line." in fit(SKILL, set())


def test_a_section_of_another_mode_is_dropped():
    assert "Client line." not in fit(SKILL, SERVER)


def test_a_section_of_the_mode_is_kept():
    assert "Server line." in fit(SKILL, SERVER)


def test_the_markers_never_reach_the_project():
    assert "nexy:" not in fit(SKILL, CLIENT)


def test_an_api_project_keeps_only_untagged_text():
    assert fit(SKILL, set()) == "# Title\n\nShared line.\n\nLast line.\n"


def test_a_web_section_reaches_a_client_routed_project():
    assert "Web line." in fit(SKILL, CLIENT)


def test_a_server_project_has_the_server_and_web_modes():
    assert modes_of(Profile("demo", "none", False, "tailwind")) == SERVER


def test_a_client_routed_project_has_the_client_and_web_modes():
    assert modes_of(Profile("demo", "react", True, "tailwind")) == CLIENT


def test_an_api_project_has_no_mode():
    assert modes_of(Profile("demo", "none", False, "vanilla", kind="api")) == set()


def test_every_markdown_file_of_a_skill_is_fitted(tmp_path: Path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "guide.md").write_text(SKILL, encoding="utf-8")
    fit_tree(tmp_path, CLIENT)
    assert "Server line." not in (tmp_path / "nested" / "guide.md").read_text(encoding="utf-8")
