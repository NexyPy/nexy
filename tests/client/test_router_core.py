"""The framework-neutral client router: navigation, history, scroll, clicks and prefetch.

The scenarios run in `router_scenarios.mjs` (jsdom); each test reads one observation.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")


@pytest.fixture(scope="module")
def seen() -> dict:
    done = subprocess.run(
        [NODE, str(HERE / "router_scenarios.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


class TestViewTransition:
    def test_the_page_change_runs_inside_a_view_transition(self, seen):
        assert seen["viewTransition"]["calls"] == ["start", "done"]
        assert seen["viewTransition"]["rendered"] == ["/src/routes/about.tsx"]

    def test_a_visitor_who_prefers_calm_gets_the_plain_change(self, seen):
        assert seen["viewTransition"]["calmCalls"] == []
        assert seen["viewTransition"]["calmRendered"] == ["/src/routes/about.tsx"]


class TestNavigation:
    def test_it_renders_then_moves_the_url_and_announces_itself(self, seen):
        nav = seen["navigate"]
        assert nav["ok"] and nav["path"] == "/about" and nav["location"] == "/about"
        assert nav["rendered"] == ["/src/routes/about.tsx"] and nav["events"] == ["/about"]

    def test_the_history_entry_is_marked_as_a_client_one(self, seen):
        assert seen["navigate"]["state"] is True

    def test_a_page_that_fails_to_render_leaves_the_url_alone(self, seen):
        failure = seen["renderFailure"]
        assert failure["ok"] is False and failure["path"] == "/"

    def test_a_failed_page_is_requested_from_the_server_instead(self, seen):
        assert seen["renderFailure"]["assigned"] == ["http://localhost/broken"]

    def test_a_path_without_a_route_goes_to_the_server(self, seen):
        assert seen["serverOwned"]["a"] is False
        assert "http://localhost/nowhere" in seen["serverOwned"]["assigned"]

    def test_another_origin_goes_to_the_server(self, seen):
        assert "https://example.com/about" in seen["serverOwned"]["assigned"]
        assert seen["serverOwned"]["rendered"] == []

    def test_a_newer_navigation_wins_over_one_still_rendering(self, seen):
        assert seen["concurrent"] == {"first": False, "path": "/about", "length": 2}

    def test_going_to_the_page_already_shown_does_nothing(self, seen):
        assert seen["samePage"] == {"ok": True, "rendered": [], "length": 1}


class TestHistory:
    def test_a_fragment_change_renders_nothing_and_scrolls_to_the_target(self, seen):
        hash_ = seen["hash"]
        assert hash_["rendered"] == [] and hash_["hash"] == "#section"
        assert hash_["scrolls"] == [["into", "section"]]

    def test_replace_does_not_add_an_entry(self, seen):
        assert seen["replace"] == {"grew": 0, "path": "/about"}

    def test_back_renders_the_previous_page_and_restores_its_scroll(self, seen):
        back = seen["back"]
        assert back["path"] == "/" and back["rendered"] == ["/src/routes/index.tsx"]
        assert back["scrolled"] == [0, 420]


class TestStore:
    def test_subscribers_hear_each_change_once(self, seen):
        assert seen["subscribe"] == {"calls": 1, "changed": True, "stable": True}

    def test_the_location_carries_params_and_the_query(self, seen):
        assert seen["params"] == {
            "params": {"id": "42"},
            "search": "?tab=posts",
            "query": {"tab": "posts"},
        }


class TestClicks:
    @pytest.mark.parametrize("kind", ["plain", "withLinkAttr"])
    def test_a_link_to_a_known_route_is_a_client_navigation(self, seen, kind):
        assert seen["clicks"][kind] is True

    @pytest.mark.parametrize(
        "kind",
        [
            "ctrl",
            "middle",
            "blank",
            "download",
            "reload",
            "external",
            "rel",
            "unknown",
            "hashOnly",
            "mailto",
        ],
    )
    def test_everything_else_is_left_to_the_browser(self, seen, kind):
        assert seen["clicks"][kind] is False


class TestPrefetch:
    def test_each_route_is_warmed_once_and_only_when_it_can_be_served(self, seen):
        assert seen["prefetch"] == ["/src/routes/about.tsx"]
