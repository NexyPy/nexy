"""The /todos page of every web starter keeps its tasks on the Python server.

Each starter is scaffolded, built and served by `nx start`; Chromium opens /todos and uses it as a
person would: add, tick, rename, filter, delete. Every change goes through an action, and the page
shows the list the server answers with.
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
    project = tmp_path_factory.mktemp("todos") / "app"
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


def _open(page: Page, url: str) -> None:
    """Open /todos once the first answer of the server is on the page."""
    page.goto(url + "/todos")
    expect(page.get_by_text("Add a task with the field above")).to_be_visible()


def _add(page: Page, title: str) -> None:
    page.get_by_label("New task").fill(title)
    page.get_by_label("New task").press("Enter")


def _tasks(page: Page):
    return page.get_by_role("list", name="Tasks").get_by_role("listitem")


def _task(page: Page, title: str):
    """The row of one task: a click on it waits until the server has sent it."""
    return _tasks(page).filter(has_text=title)


@pytest.mark.e2e
def test_the_page_lists_the_tasks_the_server_keeps(starter, page: Page):
    _open(page, starter)
    expect(_tasks(page).filter(has_text="Tick a task to mark it done")).to_have_count(1)


@pytest.mark.e2e
def test_the_page_says_how_long_the_server_took(starter, page: Page):
    _open(page, starter)
    expect(page.get_by_text(re.compile(r"^\d+ ms$"))).to_be_visible()


@pytest.mark.e2e
def test_a_new_task_comes_back_from_the_server(starter, page: Page):
    _open(page, starter)
    _add(page, "Water the plants")
    expect(_tasks(page).last).to_contain_text("Water the plants")


@pytest.mark.e2e
def test_the_field_is_empty_once_the_task_is_added(starter, page: Page):
    _open(page, starter)
    _add(page, "Call the plumber")
    expect(page.get_by_label("New task")).to_have_value("")


@pytest.mark.e2e
def test_the_server_refuses_an_empty_task(starter, page: Page):
    _open(page, starter)
    _add(page, "   ")
    expect(page.get_by_text("Write what there is to do.")).to_be_visible()


@pytest.mark.e2e
def test_a_ticked_task_is_done(starter, page: Page):
    _open(page, starter)
    _add(page, "Feed the cat")
    page.get_by_label("Done: Feed the cat").click()
    expect(page.get_by_label("Done: Feed the cat")).to_be_checked()


@pytest.mark.e2e
def test_enter_saves_a_new_title(starter, page: Page):
    _open(page, starter)
    _add(page, "Buy bread")
    page.get_by_text("Buy bread").dblclick()
    page.get_by_label("Rename the task").fill("Buy rye bread")
    page.get_by_label("Rename the task").press("Enter")
    expect(page.get_by_text("Buy rye bread")).to_be_visible()


@pytest.mark.e2e
def test_escape_keeps_the_old_title(starter, page: Page):
    _open(page, starter)
    _add(page, "Read a book")
    _task(page, "Read a book").get_by_role("button", name="Rename").click()
    page.get_by_label("Rename the task").fill("Something else")
    page.get_by_label("Rename the task").press("Escape")
    expect(_task(page, "Read a book")).to_be_visible()


@pytest.mark.e2e
def test_the_done_filter_shows_only_done_tasks(starter, page: Page):
    _open(page, starter)
    page.get_by_role("button", name=re.compile("^Done")).click()
    expect(page.get_by_text("Add a task with the field above")).to_have_count(0)


@pytest.mark.e2e
def test_delete_removes_the_task(starter, page: Page):
    _open(page, starter)
    _add(page, "Short lived")
    _task(page, "Short lived").get_by_role("button", name="Delete").click()
    expect(page.get_by_text("Short lived")).to_have_count(0)
