"""`nx format` on .nexy files: imports and Jinja tags survive, the result is stable."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.helpers.common.executables import find_tool
from nexy.helpers.fs import nexy_format
from nexy.helpers.fs.nexy_format import FormatError
from nexy.modules.cli.commands.format import formatted_source

RUFF = find_tool("ruff")

SOURCE = """---
from "./button.nexy" import Button
import "./data.json" as data
title   =   'Hello'
items=[1,2,3]
---
<main>


  <h1>{{ title }}</h1>
  {% for item in items %}<Button label="{{ item }}" />{% endfor %}
</main>
"""


def _format(source: str = SOURCE) -> str:
    return formatted_source(Path("page.nexy"), source, RUFF, None)


class TestImports:
    def test_protected_imports_are_comments(self):
        protected = nexy_format.protect_imports('from "./a.nexy" import A\nx = 1')
        assert protected.startswith("# nexy-import: from")

    def test_restoring_gives_the_import_back(self):
        source = 'from "./a.nexy" import A\nimport "./d.json" as d\n'
        protected = nexy_format.protect_imports(source)
        assert nexy_format.restore_imports(protected) == source

    def test_python_imports_are_not_touched(self):
        assert (
            nexy_format.protect_imports("import os\nfrom a import b")
            == "import os\nfrom a import b"
        )

    def test_indentation_is_kept(self):
        source = '    from "./a.nexy" import A'
        assert nexy_format.restore_imports(nexy_format.protect_imports(source)) == source


class TestJinja:
    def test_tags_round_trip(self):
        source = "<p>{{ a }}</p>{% if b %}x{% endif %}{# note #}"
        protected, tags = nexy_format.protect_jinja(source)
        assert nexy_format.restore_jinja(protected, tags) == source

    def test_protected_text_has_no_braces(self):
        protected, _ = nexy_format.protect_jinja("<p>{{ a }}</p>")
        assert "{" not in protected

    def test_a_lost_tag_is_an_error(self):
        _, tags = nexy_format.protect_jinja("{{ a }}")
        with pytest.raises(FormatError):
            nexy_format.restore_jinja("<p></p>", tags)


class TestNormalize:
    def test_trailing_spaces_go(self):
        assert nexy_format.normalize("<p>a</p>   ") == "<p>a</p>"

    def test_blank_runs_collapse_to_one_blank_line(self):
        assert nexy_format.normalize("a\n\n\n\nb") == "a\n\nb"


class TestFormattedSource:
    def test_python_logic_is_formatted(self):
        assert "title = 'Hello'" in _format() or 'title = "Hello"' in _format()

    def test_nexy_imports_are_kept(self):
        assert 'from "./button.nexy" import Button' in _format()

    def test_data_imports_are_kept(self):
        assert 'import "./data.json" as data' in _format()

    def test_jinja_tags_are_kept(self):
        assert "{{ title }}" in _format()

    def test_the_template_is_normalized_without_prettier(self):
        assert "\n\n\n" not in _format() and "   \n" not in _format()

    def test_formatting_twice_changes_nothing(self):
        once = _format()
        assert _format(once) == once

    def test_the_file_ends_with_one_newline(self):
        result = _format()
        assert result.endswith("</main>\n") and not result.endswith("\n\n")

    def test_a_file_without_logic_is_just_a_template(self):
        assert _format("<p>{{ a }}</p>   \n\n\n") == "<p>{{ a }}</p>\n"
