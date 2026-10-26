"""The Python module generated for a .nexy component, checked against recorded outputs.

`golden/logic_generator.json` holds what the generator produced before it was split into small
functions; the refactor must not change a byte of it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from nexy.core.config import Config
from nexy.core.models import NexyProp, ParserModel
from nexy.modules.compiler.generator import logic as logic_module
from nexy.modules.compiler.generator.logic import LogicGenerator
from nexy.modules.routers.fbrouter.layout import RouteLayout

GOLDEN = Path(__file__).parent / "golden" / "logic_generator.json"

IMPORTS_AND_LOGIC = (
    "import os\nfrom pathlib import Path as P, *\nx = 1\ndef helper():\n    return x\n"
)

SCENARIOS: dict[str, dict[str, Any]] = {
    "plain": {"frontmatter": "x = 1\n", "props": [], "layout": None},
    "imports_and_defs": {"frontmatter": IMPORTS_AND_LOGIC, "props": [], "layout": None},
    "only_imports": {"frontmatter": "import os\nimport json as j\n", "props": [], "layout": None},
    "props": {
        "frontmatter": "title = name.upper()\n",
        "props": [("name", "str", "'a'"), ("count", "int", "0")],
        "layout": None,
    },
    "caller_and_children_props": {
        "frontmatter": "",
        "props": [("caller", "Any", "None"), ("children", "str", "''")],
        "layout": None,
    },
    "layout": {"frontmatter": "x = 1\n", "props": [], "layout": "src.routes.layout"},
    "layout_file": {
        "frontmatter": "x = 1\n",
        "props": [],
        "layout": None,
        "path": "src/routes/layout.nexy",
    },
    "syntax_error": {"frontmatter": "def broken(:\n", "props": [], "layout": None},
    "modular_router": {"frontmatter": "x = 1\n", "props": [], "layout": None, "router": True},
    "route_without_layout": {
        "frontmatter": "x = 1\n",
        "props": [],
        "layout": None,
        "path": "src/routes/index.nexy",
    },
    "underscore_and_class": {
        "frontmatter": "_hidden = 1\nclass Box:\n    pass\nasync def go():\n    pass\n",
        "props": [],
        "layout": None,
    },
}


def _generate(name: str, case: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setattr(
        RouteLayout, "get_closest_import", staticmethod(lambda *_a, **_k: case["layout"])
    )
    monkeypatch.setattr(Config, "useRouter", object() if case.get("router") else None)
    props = [NexyProp(*prop) for prop in case["props"]]
    source = ParserModel(frontmatter=case["frontmatter"], template="<p></p>", props=props)
    generator = LogicGenerator()
    generator.vfs = _MemoryVfs()
    generator.generate(f"__nexy__/{name}.nexy", source, case.get("path"))
    return generator.FRONTMATTER


class _MemoryVfs:
    def write(self, path: str, content: str) -> None:
        self.last = (path, content)


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_the_generated_module_is_what_it_was(name, monkeypatch):
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert _generate(name, SCENARIOS[name], monkeypatch) == golden[name]


def test_a_generator_without_a_source_says_so():
    with pytest.raises(RuntimeError):
        LogicGenerator()._component_model()


def test_the_module_is_importable_python():
    assert hasattr(logic_module, "LogicGenerator")


class TestPieces:
    def test_imports_are_split_from_the_logic(self):
        imports, body = logic_module.split_imports("import os\nx = 1\n")
        assert (imports, body) == ("import os", "x = 1")

    def test_a_frontmatter_without_imports_is_left_alone(self):
        assert logic_module.split_imports("x = 1\n") == ("", "x = 1\n")

    def test_a_frontmatter_that_does_not_parse_is_left_alone(self):
        assert logic_module.split_imports("def (:") == ("", "def (:")

    def test_the_template_sees_names_in_the_order_they_were_defined(self):
        props = [NexyProp("count", "int", "0")]
        names = logic_module.template_names("import os\nx = 1\ndef f(): pass\n", props)
        assert names == ["os", "x", "f", "count"]

    def test_private_names_and_star_imports_stay_out(self):
        names = logic_module.template_names("from a import *\n_x = 1\n", [])
        assert names == []

    def test_a_prop_that_is_also_defined_is_listed_once(self):
        names = logic_module.template_names("name = 1\n", [NexyProp("name", "str", "''")])
        assert names == ["name"]

    def test_the_slot_always_ends_the_context(self):
        assert logic_module.context_literal([]) == "'Slot': Slot"
        assert logic_module.context_literal(["a"]) == "\"a\": a, 'Slot': Slot"

    def test_caller_and_children_are_added_unless_declared(self):
        assert logic_module.props_signature([]) == "caller: Any = None, children: str = ''"
        declared = [NexyProp("children", "str", "''")]
        assert logic_module.props_signature(declared) == ("children: str = '', caller: Any = None")

    def test_a_component_name_is_a_valid_identifier(self):
        assert logic_module.function_name("src/routes/my-page.nexy").isidentifier()

    def test_the_modular_router_has_no_layout(self, monkeypatch):
        monkeypatch.setattr(Config, "useRouter", object())
        assert logic_module.layout_shell("src/routes/index.nexy") == logic_module.Shell()
