"""Every web-fbr starter ships a /connection page and the server action it calls."""

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


def _scaffold(dest: Path, style: str, framework: str) -> Path:
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": "None",
        "useCSR": framework != "none",
        "style": style,
    }
    _render_local_template("web-fbr", dest, config, "demo")
    return dest


def _page(tmp_path: Path, style: str, framework: str) -> str:
    _scaffold(tmp_path, style, framework)
    return (tmp_path / "src" / "routes" / PAGES[framework]).read_text("utf-8")


@pytest.mark.parametrize(("style", "framework"), STARTERS)
class TestTheConnectionPage:
    def test_the_page_is_written(self, tmp_path, style, framework):
        assert "Ping the server" in _page(tmp_path, style, framework)

    def test_the_action_it_calls_is_written(self, tmp_path, style, framework):
        _scaffold(tmp_path, style, framework)
        assert "async def ping() -> Pong:" in (tmp_path / "src/actions/ping.py").read_text("utf-8")

    def test_the_answer_is_announced_to_a_screen_reader(self, tmp_path, style, framework):
        assert 'aria-live="polite"' in _page(tmp_path, style, framework)

    def test_no_build_time_jinja_is_left(self, tmp_path, style, framework):
        assert "{%" not in _page(tmp_path, style, framework)


@pytest.mark.parametrize("framework", [fw for fw in PAGES if fw != "none"])
def test_a_client_routed_page_calls_the_typed_action(tmp_path, framework):
    assert 'import { ping } from "@nexy/actions";' in _page(tmp_path, "vanilla", framework)


def test_a_server_page_posts_to_the_path_of_the_action(tmp_path):
    assert "data-ping=\"{{ __actions_path['ping'] }}\"" in _page(tmp_path, "vanilla", "none")
