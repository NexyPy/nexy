"""Every web-fbr starter ships a /connection page and the two server actions it calls."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template

PAGES = {
    "none": "connection.nexy",
    "react": "connection.tsx",
    "preact": "connection.tsx",
    "solid": "connection.tsx",
    "vue": "connection.vue",
    "svelte": "connection.svelte",
}
STARTERS = [(style, fw) for style in ("tailwind", "vanilla") for fw in PAGES]


def _scaffold(dest: Path, style: str, framework: str, orm: str = "None") -> Path:
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": orm,
        "useCSR": framework != "none",
        "style": style,
    }
    _render_local_template("web-fbr", dest, config, "demo")
    return dest


def _page(tmp_path: Path, style: str, framework: str) -> str:
    _scaffold(tmp_path, style, framework)
    return (tmp_path / "src" / "routes" / PAGES[framework]).read_text("utf-8")


def _actions(tmp_path: Path, orm: str = "None") -> str:
    _scaffold(tmp_path, "vanilla", "react", orm)
    return (tmp_path / "src/actions/team.py").read_text("utf-8")


@pytest.mark.parametrize(("style", "framework"), STARTERS)
class TestTheConnectionPage:
    def test_the_page_has_a_form_to_join_the_team(self, tmp_path, style, framework):
        assert "Add to the team" in _page(tmp_path, style, framework)

    def test_the_answer_is_announced_to_a_screen_reader(self, tmp_path, style, framework):
        assert 'aria-live="polite"' in _page(tmp_path, style, framework)

    def test_no_build_time_jinja_is_left(self, tmp_path, style, framework):
        assert "{%" not in _page(tmp_path, style, framework)


@pytest.mark.parametrize("framework", [fw for fw in PAGES if fw != "none"])
def test_a_client_routed_page_calls_the_typed_actions(tmp_path, framework):
    assert 'import { join_team, team } from "@nexy/actions";' in _page(
        tmp_path, "vanilla", framework
    )


def test_a_server_page_lists_the_team_through_its_action(tmp_path):
    assert "data-list=\"{{ __actions_path['team'] }}\"" in _page(tmp_path, "vanilla", "none")


def test_a_server_page_joins_the_team_through_its_action(tmp_path):
    assert "data-join=\"{{ __actions_path['join_team'] }}\"" in _page(tmp_path, "vanilla", "none")


def test_without_a_database_the_team_is_a_list_of_dictionaries(tmp_path):
    assert "TEAM: list[dict[str, str]] = [" in _actions(tmp_path)


@pytest.mark.parametrize("orm", ["SQLModel", "SQLAlchemy"])
def test_with_a_database_the_team_is_the_users_table(tmp_path, orm):
    assert "UserService.create(name, email)" in _actions(tmp_path, orm)


def test_with_tortoise_the_actions_wait_on_its_own_loop(tmp_path):
    assert "await arun(UserService.create(name, email))" in _actions(tmp_path, "Tortoise-ORM")


@pytest.mark.parametrize("orm", ["None", "SQLModel", "SQLAlchemy", "Tortoise-ORM"])
def test_the_actions_are_valid_python(tmp_path, orm):
    compile(_actions(tmp_path, orm), "team.py", "exec")
