"""A page declares `revalidate` and `metadata` in its frontmatter; the router reads the module.

The frontmatter runs inside the component function, so a plain `revalidate = 60` there was a local
variable that no router could see: the documented ISR cache never switched on for a `.nexy` page.
Literal values of these names are therefore written at module level.
"""

from __future__ import annotations

from types import ModuleType

import pytest

from nexy.core.config import Config
from nexy.core.models import ParserModel
from nexy.modules.compiler.generator import logic as logic_module
from nexy.modules.compiler.generator.logic import render_module
from nexy.modules.routers.fbrouter.layout import RouteLayout


@pytest.fixture
def module_of(monkeypatch):
    monkeypatch.setattr(RouteLayout, "get_closest_import", staticmethod(lambda *_a, **_k: None))
    monkeypatch.setattr(Config, "useRouter", None)

    def build(frontmatter: str) -> ModuleType:
        source = ParserModel(frontmatter=frontmatter, template="<p></p>", props=[])
        module = ModuleType("page")
        exec(render_module("__nexy__/page.nexy", source), module.__dict__)  # noqa: S102
        return module

    return build


def test_a_literal_revalidate_is_a_module_attribute(module_of):
    assert module_of("revalidate = 60\n").revalidate == 60


def test_a_literal_metadata_is_a_module_attribute(module_of):
    module = module_of('metadata = {"title": "Blog", "description": "Posts"}\n')
    assert module.metadata == {"title": "Blog", "description": "Posts"}


def test_a_value_that_is_computed_stays_in_the_component(module_of):
    module = module_of("import os\nrevalidate = int(os.environ.get('N', '5'))\n")
    assert not hasattr(module, "revalidate")


def test_a_name_assigned_in_a_function_is_not_an_export(module_of):
    module = module_of("def helper():\n    revalidate = 5\n    return revalidate\n")
    assert not hasattr(module, "revalidate")


def test_other_names_stay_in_the_component(module_of):
    assert not hasattr(module_of("title = 'x'\n"), "title")


class TestSplit:
    def test_exports_leave_the_body(self):
        exports, body = logic_module.split_route_exports("revalidate = 60\nx = 1\n")
        assert (exports, body) == ("revalidate = 60", "x = 1")

    def test_a_frontmatter_without_exports_is_left_alone(self):
        assert logic_module.split_route_exports("x = 1\n") == ("", "x = 1\n")

    def test_a_frontmatter_that_does_not_parse_is_left_alone(self):
        assert logic_module.split_route_exports("def (:") == ("", "def (:")

    def test_imports_and_exports_both_go_to_module_level(self):
        top, body = logic_module.split_frontmatter("import os\nrevalidate = 5\nx = os.sep\n")
        assert (top, body) == ("import os\nrevalidate = 5", "x = os.sep")


class TestStaticMetadata:
    def test_a_page_with_metadata_applies_it_when_it_runs(self):
        top, body = logic_module.split_frontmatter('metadata = {"title": "Blog"}\nx = 1\n')
        assert body.startswith("__apply_metadata(metadata)")
        assert "apply_static_metadata as __apply_metadata" in top

    def test_a_page_without_metadata_gets_no_extra_code(self):
        top, body = logic_module.split_frontmatter("revalidate = 5\nx = 1\n")
        assert (top, body) == ("revalidate = 5", "x = 1")

    def test_a_page_whose_only_content_is_metadata_still_applies_it(self):
        _, body = logic_module.split_frontmatter('metadata = {"title": "Blog"}\n')
        assert body.strip() == "__apply_metadata(metadata)"
