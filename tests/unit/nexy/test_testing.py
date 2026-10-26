"""`nexy.testing.render`: a .nexy component rendered in-process for a unit test."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.testing import render

HELLO = """---
name: prop[str] = "world"
shout = name.upper()
---
<h1>Hello {{ name }} {{ shout }}</h1>
"""

PAGE = """---
from "./hello.nexy" import Hello
---
<main><Hello name="Ada" /></main>
"""

CARD = """---
title: prop[str]
---
<section><h2>{{ title }}</h2>{{ Slot() | safe }}</section>
"""


@pytest.fixture
def project(tmp_path, monkeypatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    return tmp_path


def _write(project: Path, name: str, source: str) -> str:
    path = project / "src" / name
    path.write_text(source, encoding="utf-8")
    return str(path.relative_to(project))


def test_a_component_renders_with_its_default_props(project):
    assert "Hello world WORLD" in render(_write(project, "hello.nexy", HELLO))


def test_props_are_passed_as_keywords(project):
    assert "Hello Bob BOB" in render(_write(project, "hello.nexy", HELLO), name="Bob")


def test_logic_in_the_frontmatter_runs(project):
    assert "AMY" in render(_write(project, "hello.nexy", HELLO), name="Amy")


def test_children_fill_the_slot(project):
    html = render(_write(project, "card.nexy", CARD), title="T", children="<p>inside</p>")
    assert "<p>inside</p>" in html


def test_a_component_that_imports_another_renders_it(project):
    _write(project, "hello.nexy", HELLO)
    assert "Hello Ada ADA" in render(_write(project, "page.nexy", PAGE))


def test_an_edited_component_is_read_again(project):
    path = _write(project, "hello.nexy", HELLO)
    render(path)
    _write(project, "hello.nexy", HELLO.replace("Hello", "Bye"))
    assert "Bye world" in render(path)


@pytest.mark.usefixtures("project")
def test_a_missing_file_is_refused():
    with pytest.raises(FileNotFoundError):
        render("src/none.nexy")


def test_a_file_that_is_not_a_component_is_refused(project):
    (project / "notes.txt").write_text("x", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        render("notes.txt")
