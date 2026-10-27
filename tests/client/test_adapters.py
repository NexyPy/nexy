"""Link, Image and the hooks behave the same in React, Preact, Solid, Vue and Svelte.

Each framework renders a page on the server at ``/about?tab=a``, hydrates it in jsdom with the real
router running, then hovers, clicks and pushes. The five reports have the same shape.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")

FRAMEWORKS = ("react", "preact", "solid", "vue", "svelte")


def _node(*args: str, browser: bool = True) -> subprocess.CompletedProcess[str]:
    flags = ["--conditions=browser"] if browser else []
    return subprocess.run(
        [NODE, *flags, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
        cwd=HERE,
    )


def _run(framework: str) -> dict:
    if framework == "solid":
        served = _node("adapter_solid.mjs", "server", browser=False)
        assert served.returncode == 0, served.stderr[-1500:]
        done = _node("adapter_solid.mjs", "client")
    elif framework in ("react", "preact"):
        done = _node("adapter_jsx.mjs", framework)
    else:
        done = _node(f"adapter_{framework}.mjs")
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


@pytest.fixture(scope="module", params=FRAMEWORKS)
def story(request: pytest.FixtureRequest) -> dict:
    return _run(request.param)


def _classes(link: dict) -> list[str]:
    return (link["class"] or "").split()


class TestServerRender:
    def test_the_link_to_the_current_page_is_marked_current_and_active(self, story):
        about = story["initial"]["links"]["about"]
        assert about["current"] == "page" and _classes(about) == ["nav", "on"]

    def test_the_other_links_are_neither(self, story):
        home = story["initial"]["links"]["home"]
        assert home["current"] is None and _classes(home) == ["nav"]

    def test_every_link_carries_the_router_marker(self, story):
        assert all(link["marker"] == "true" for link in story["initial"]["links"].values() if link)

    def test_the_hooks_see_the_request_url_during_the_first_render(self, story):
        initial = story["initial"]
        assert (initial["path"], initial["params"], initial["tab"]) == ("/about", "{}", "a")

    def test_hydration_finds_no_mismatch(self, story):
        assert story["errors"] == []


class TestImage:
    def test_it_is_lazy_and_keeps_its_aspect_ratio(self, story):
        image = story["initial"]["image"]
        assert (image["loading"], image["decoding"]) == ("lazy", "async")
        assert (image["width"], image["height"]) == ("800", "600")
        assert image["style"].rstrip(";") == "height:auto;max-width:100%"
        assert image["alt"] == "A"


class TestNavigation:
    def test_hovering_a_link_warms_its_page(self, story):
        assert story["afterHover"] == ["/src/routes/users/[id].tsx"]

    def test_clicking_a_link_renders_the_page_without_a_reload(self, story):
        click = story["afterClick"]
        assert click["rendered"] == ["/src/routes/index.tsx"] and click["url"] == "/"

    def test_the_links_follow_the_new_page(self, story):
        links = story["afterClick"]["links"]
        assert links["home"]["current"] == "page" and _classes(links["home"]) == ["nav", "on"]
        assert links["about"]["current"] is None and _classes(links["about"]) == ["nav"]

    def test_the_hooks_follow_the_new_page(self, story):
        click = story["afterClick"]
        assert (click["path"], click["params"], click["tab"]) == ("/", "{}", "")


class TestRouterObject:
    def test_push_updates_the_url_params_and_query(self, story):
        push = story["afterPush"]
        assert push["url"] == "/users/7?tab=x"
        assert (push["path"], push["params"], push["tab"]) == ("/users/7", '{"id":"7"}', "x")

    def test_the_link_to_the_pushed_page_becomes_current(self, story):
        assert story["afterPush"]["links"]["user"]["current"] == "page"
