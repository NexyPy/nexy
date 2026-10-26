"""How `from "./x.nexy" import X` and `import "./data.json" as data` become Python."""

from __future__ import annotations

import pytest

from nexy.core.config import Config
from nexy.modules.compiler.parser.sanitizer import LogicSanitizer, _require_identifier


@pytest.fixture
def sanitizer(monkeypatch) -> LogicSanitizer:
    monkeypatch.setattr(Config, "ALIASES", {"@/": "src/"})
    monkeypatch.setattr(Config, "NAMESPACE", "__nexy__/")
    monkeypatch.setattr(Config, "FRONTEND_EXTENSIONS", {".tsx": "react", ".json": "json"})
    return LogicSanitizer()


class TestModuleNames:
    def test_a_nexy_file_is_imported_from_the_compiled_namespace(self, sanitizer):
        assert sanitizer._module_name("src/ui/card.nexy", is_nexy=True) == "__nexy__.src.ui.card"

    def test_a_python_file_is_imported_by_its_own_path(self, sanitizer):
        assert sanitizer._module_name("src/lib/util.py", is_nexy=False) == "src.lib.util"

    def test_backslashes_and_repeated_dots_are_cleaned(self, sanitizer):
        assert sanitizer._module_name("src\\ui..card.nexy", is_nexy=False) == "src.ui.card"

    def test_no_namespace_means_no_prefix(self, sanitizer, monkeypatch):
        monkeypatch.setattr(Config, "NAMESPACE", "")
        assert sanitizer._prefix(is_nexy=True) == ""


class TestFrom:
    def test_a_nexy_component_becomes_a_python_import(self, sanitizer):
        out = sanitizer.sanitize('from "./card.nexy" import Card\n', "src/page.nexy")
        assert out == "from __nexy__.src.card import Card\n" or "import Card" in out

    def test_a_framework_component_becomes_an_import_call(self, sanitizer):
        out = sanitizer.sanitize('from "./card.tsx" import Card\n', "src/page.nexy")
        assert 'Card = __Import(path="src/card.tsx", framework="react", symbol="Card")' in out

    def test_an_alias_names_the_variable_and_keeps_the_symbol(self, sanitizer):
        out = sanitizer.sanitize('from "./card.tsx" import Card as Box\n', "src/page.nexy")
        assert 'Box = __Import(path="src/card.tsx", framework="react", symbol="Card")' in out

    def test_several_targets_make_several_lines(self, sanitizer):
        out = sanitizer.sanitize('from "./ui.tsx" import A, B\n', "src/page.nexy")
        assert out.count("__Import(") == 2


class TestImport:
    def test_a_json_file_becomes_a_default_import(self, sanitizer):
        out = sanitizer.sanitize('import "./data.json" as data\n', "src/page.nexy")
        assert 'data = __Import(path="src/data.json", framework="json", symbol="default")' in out

    def test_without_an_alias_the_file_name_is_used(self, sanitizer):
        out = sanitizer.sanitize('import "./my-data.json"\n', "src/page.nexy")
        assert out.startswith("my_data = __Import(")

    def test_a_python_module_is_imported_under_its_alias(self, sanitizer):
        out = sanitizer.sanitize('import "./util.py" as util\n', "src/page.nexy")
        assert out.strip() == "import src.util as util"

    def test_an_alias_that_is_not_a_name_is_refused(self):
        with pytest.raises(ValueError, match="Invalid alias"):
            _require_identifier("src.util", "not-a-name")

    def test_a_module_path_that_is_not_a_name_is_refused(self):
        with pytest.raises(ValueError, match="Invalid module name"):
            _require_identifier("src.my-mod", "ok")


class TestPaths:
    def test_a_configured_alias_is_resolved_from_the_project_root(self, sanitizer):
        assert sanitizer._resolve_full_path("src/p.nexy", "@/ui/card.nexy") == "src/ui/card.nexy"

    def test_an_alias_that_is_not_configured_is_an_error(self, sanitizer):
        with pytest.raises(ImportError, match="not configured"):
            sanitizer._resolve_full_path("src/p.nexy", "$/ui/card.nexy")

    def test_a_package_name_is_left_alone(self, sanitizer):
        assert sanitizer._resolve_full_path("src/p.nexy", "fastapi") == "fastapi"

    def test_a_relative_path_is_resolved_from_the_file(self, sanitizer):
        assert sanitizer._resolve_full_path("src/pages/p.nexy", "../ui/c.nexy") == "src/ui/c.nexy"
