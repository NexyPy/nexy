"""The docs say where `nexy` may run: `uvx` only creates a project, the rest runs inside it.

`uvx nexy dev` starts Nexy in a temporary environment that holds Nexy and nothing else, so a
project that needs `sqlmodel` or any other package fails to import its own config. Documenting it
sent people into that failure.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
PAGES = {
    "README": ROOT / "README.md",
    "installation": ROOT / "docs" / "getting-started" / "installation.md",
    "quick-start": ROOT / "docs" / "getting-started" / "quick-start.md",
    "tutorial": ROOT / "docs" / "getting-started" / "tutorial.md",
    "cli": ROOT / "docs" / "reference" / "cli.md",
    "troubleshooting": ROOT / "docs" / "guides" / "troubleshooting.md",
}
GETTING_STARTED = ("README", "installation", "quick-start")


def _text(name: str) -> str:
    return PAGES[name].read_text(encoding="utf-8")


def _every_doc() -> list[Path]:
    return [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md")), ROOT / "llms.txt"]


@pytest.mark.parametrize("path", _every_doc(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_no_page_runs_a_project_command_with_uvx(path):
    commands = re.findall(
        r"uvx nexy (dev|start|build|migrate|check|format|test)\b", path.read_text(encoding="utf-8")
    )
    assert commands == []


@pytest.mark.parametrize("name", ["README", "installation", "quick-start", "cli"])
def test_the_page_says_uv_comes_with_uvx(name):
    assert re.search(r"`uvx`[^.]*(comes with|installed with|part of)\s+(\[)?uv\b", _text(name))


@pytest.mark.parametrize("name", GETTING_STARTED)
def test_the_page_tells_to_activate_the_virtual_environment(name):
    text = _text(name)
    assert r".venv\Scripts\activate" in text and "source .venv/bin/activate" in text


@pytest.mark.parametrize("name", GETTING_STARTED)
def test_the_page_says_to_stay_in_the_virtual_environment(name):
    assert "virtual environment" in _text(name)


@pytest.mark.parametrize("name", GETTING_STARTED)
def test_the_page_offers_uv_run_for_people_who_do_not_activate(name):
    assert "uv run nexy dev" in _text(name)


def test_the_tutorial_activates_the_environment_before_the_dev_server():
    text = _text("tutorial")
    assert text.index("activate") < text.index("nexy dev")


def test_troubleshooting_explains_a_module_that_cannot_be_found():
    text = _text("troubleshooting")
    assert "No module named" in text and "virtual environment" in text
