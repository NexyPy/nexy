"""The /connection page of every web starter lists a team the Python server keeps, and joins it.

Each starter is scaffolded, built and served by `nx start`; Chromium opens /connection, waits for
the team, then sends the form: the team actions of web-fbr, the team controller of web-modular.
"""

from __future__ import annotations

import re
import subprocess  # nosec B404
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from nexy.modules.cli.init.template_setup import _render_local_template
from tests.e2e.conftest import _free_port, _install_node_modules, _run, _wait_for_port

NX = "import sys; from nexy.modules.cli import CLI; sys.argv[0] = 'nx'; CLI()"
STATUS = "[role='status']"

# (template, style, client framework, client-side routing)
STARTERS = [
    ("web-fbr", style, framework, framework != "none")
    for style in ("tailwind", "vanilla")
    for framework in ("none", "react", "preact", "solid", "vue", "svelte")
] + [("web-modular", style, "none", False) for style in ("tailwind", "vanilla")]


def _scaffold(project: Path, template: str, style: str, framework: str, csr: bool) -> None:
    config = {
        "client_framework": framework,
        "FBRouter": template == "web-fbr",
        "project_type": "web",
        "orm": "None",
        "useCSR": csr,
        "style": style,
    }
    _render_local_template(template, project, config, "demo")


@pytest.fixture(scope="module", params=STARTERS, ids=lambda s: "-".join(map(str, s)))
def starter(request: pytest.FixtureRequest, tmp_path_factory) -> Iterator[str]:
    """One starter, built and served by `nx start`; yields its base URL."""
    project = tmp_path_factory.mktemp("connection") / "app"
    _scaffold(project, *request.param)
    _install_node_modules(project)
    _run(project, sys.executable, "-c", NX, "build")
    port = _free_port()
    server = subprocess.Popen(  # nosec B603 - sys.executable with a fixed launcher
        [sys.executable, "-c", NX, "start", "--port", str(port)],
        cwd=project,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert _wait_for_port(port), "nx start did not listen"
        yield f"http://127.0.0.1:{port}"
    finally:
        server.terminate()
        server.wait(timeout=10)


def _join(page: Page, url: str, name: str, email: str) -> None:
    page.goto(url + "/connection")
    expect(page.locator(STATUS)).to_contain_text("Loaded from Python")
    page.get_by_label("Name").fill(name)
    page.get_by_label("Email").fill(email)
    page.get_by_role("button", name="Add to the team").click()


@pytest.mark.e2e
def test_the_page_lists_the_team_the_server_keeps(starter, page: Page):
    page.goto(starter + "/connection")
    expect(page.get_by_role("list", name="Team")).to_contain_text("Ada Lovelace")


@pytest.mark.e2e
def test_the_page_says_how_long_the_list_took(starter, page: Page):
    page.goto(starter + "/connection")
    expect(page.locator(STATUS)).to_have_text(re.compile(r"^Loaded from Python in \d+ ms\.$"))


@pytest.mark.e2e
def test_a_new_member_comes_back_from_the_server(starter, page: Page):
    _join(page, starter, "Katherine Johnson", "katherine@example.com")
    expect(page.get_by_role("list", name="Team")).to_contain_text("Katherine Johnson")


@pytest.mark.e2e
def test_the_server_refuses_a_member_already_on_the_team(starter, page: Page):
    _join(page, starter, "Ada", "ada@example.com")
    expect(page.locator(STATUS)).to_have_text("ada@example.com is already on the team.")
