"""The /connection page of every web starter reaches the Python server through a server action.

Each starter is scaffolded, built and served by `nx start`; Chromium opens /connection, presses the
button and waits for the answer of `src/actions/ping.py`.
"""

from __future__ import annotations

import platform
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

# (style, client framework, client-side routing)
STARTERS = [
    (style, framework, framework != "none")
    for style in ("tailwind", "vanilla")
    for framework in ("none", "react", "preact", "solid", "vue", "svelte")
]


def _scaffold(project: Path, style: str, framework: str, csr: bool) -> None:
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": "None",
        "useCSR": csr,
        "style": style,
    }
    _render_local_template("web-fbr", project, config, "demo")


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


def _ping(page: Page, url: str) -> None:
    page.goto(url + "/connection")
    page.get_by_role("button", name="Ping the server").click()


@pytest.mark.e2e
def test_the_page_says_nothing_was_checked_yet(starter, page: Page):
    page.goto(starter + "/connection")
    expect(page.locator(STATUS)).to_have_text("Not checked yet.")


@pytest.mark.e2e
def test_the_button_reaches_the_python_server(starter, page: Page):
    _ping(page, starter)
    expect(page.locator(STATUS)).to_contain_text(f"Python {platform.python_version()} answered")


@pytest.mark.e2e
def test_the_page_says_how_long_the_round_trip_took(starter, page: Page):
    _ping(page, starter)
    expect(page.locator(STATUS)).to_have_text(re.compile(r"^Connected in \d+ ms\."))
