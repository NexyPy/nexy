"""The import alias of a new project: validated, and written everywhere the scaffold uses `@/`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nexy.modules.cli.init.alias import apply_alias, validate_alias
from nexy.modules.cli.init.template_setup import _render_local_template


@pytest.mark.parametrize("alias", ["@", "~", "#", "$", "@app", "~src", "#app-1"])
def test_a_prefix_is_accepted(alias):
    assert validate_alias(alias) is True


@pytest.mark.parametrize("alias", ["", "app", "@/", "~ x", "@@", "/"])
def test_anything_else_is_refused_with_a_message(alias):
    assert isinstance(validate_alias(alias), str)


def _project(tmp_path: Path) -> Path:
    (tmp_path / "src" / "routes").mkdir(parents=True)
    (tmp_path / "src" / "routes" / "layout.nexy").write_text(
        'from "@/components/header.nexy" import Header\nimport "@nexy/vite"\n', encoding="utf-8"
    )
    (tmp_path / "src" / "page.tsx").write_text("import A from '@/a.tsx'\n", encoding="utf-8")
    (tmp_path / "tsconfig.json").write_text('{"paths": {"@/*": ["./src/*"]}}', encoding="utf-8")
    (tmp_path / "nexyconfig.py").write_text('useAliases = {"@": "src"}\n', encoding="utf-8")
    return tmp_path


def test_the_default_alias_changes_nothing(tmp_path):
    before = (_project(tmp_path) / "tsconfig.json").read_text("utf-8")
    apply_alias(tmp_path, "@")
    assert (tmp_path / "tsconfig.json").read_text("utf-8") == before


def test_imports_use_the_new_prefix(tmp_path):
    apply_alias(_project(tmp_path), "~")
    text = (tmp_path / "src" / "routes" / "layout.nexy").read_text("utf-8")
    assert 'from "~/components/header.nexy"' in text


def test_single_quoted_imports_are_rewritten_too(tmp_path):
    apply_alias(_project(tmp_path), "~")
    assert "'~/a.tsx'" in (tmp_path / "src" / "page.tsx").read_text("utf-8")


def test_the_nexy_prefix_is_left_alone(tmp_path):
    apply_alias(_project(tmp_path), "~")
    assert '"@nexy/vite"' in (tmp_path / "src" / "routes" / "layout.nexy").read_text("utf-8")


def test_tsconfig_paths_follow(tmp_path):
    apply_alias(_project(tmp_path), "~")
    paths = json.loads((tmp_path / "tsconfig.json").read_text("utf-8"))["paths"]
    assert "~/*" in paths and "@/*" not in paths


def test_nexyconfig_aliases_follow(tmp_path):
    apply_alias(_project(tmp_path), "#app")
    assert 'useAliases = {"#app": "src"}' in (tmp_path / "nexyconfig.py").read_text("utf-8")


@pytest.mark.parametrize("framework", ["none", "react", "vue"])
def test_a_scaffolded_project_uses_the_chosen_alias_everywhere(tmp_path, framework):
    config = {
        "client_framework": framework,
        "FBRouter": True,
        "project_type": "web",
        "orm": "None",
        "useCSR": False,
        "alias": "~",
    }
    _render_local_template("web-fbr", tmp_path, config, "demo")
    sources = [p for p in (tmp_path / "src").rglob("*") if p.is_file() and p.suffix != ".pyc"]
    leftovers = [p.name for p in sources if '"@/' in p.read_text("utf-8", errors="ignore")]
    assert leftovers == []
    assert '"~": "src"' in (tmp_path / "nexyconfig.py").read_text("utf-8")
