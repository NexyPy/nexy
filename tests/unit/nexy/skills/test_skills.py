"""The skills follow the Agent Skills format and say only what the code does today."""

from __future__ import annotations

import ast
import importlib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
CLIENT = ROOT / "nexy" / "modules" / "frontend" / "client"
CLIENT_FILE = {
    "nexy-react": "react.ts",
    "nexy-preact": "preact.ts",
    "nexy-solid": "solid.tsx",
    "nexy-vue": "vue.ts",
    "nexy-svelte": "svelte.ts",
}
FRAMEWORK_SKILLS = [path for path in SKILLS if path.parent.name in CLIENT_FILE]
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BLOCK = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")


def _ids(path: Path) -> str:
    return path.parent.name


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    assert lines[0] == "---", "frontmatter must open on the first line"
    end = lines.index("---", 1)
    fields = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def _blocks(text: str, language: str | None = None) -> list[str]:
    return [body for lang, body in BLOCK.findall(text) if language in (None, lang)]


def _imported(module: str, names: str) -> list[tuple[str, str]]:
    cleaned = names.replace("(", "").replace(")", "")
    return [(module, part.split(" as ")[0].strip()) for part in cleaned.split(",") if part.strip()]


@pytest.mark.parametrize("skill", SKILLS, ids=_ids)
class TestFormat:
    def test_the_name_matches_the_folder_and_the_rules(self, skill):
        name = _frontmatter(skill.read_text(encoding="utf-8"))["name"]
        assert name == skill.parent.name and NAME.match(name) and len(name) <= 64

    def test_the_description_says_when_to_use_it_within_the_limit(self, skill):
        description = _frontmatter(skill.read_text(encoding="utf-8"))["description"]
        assert 40 <= len(description) <= 1024 and "Load it" in description

    def test_the_body_stays_under_five_hundred_lines(self, skill):
        assert len(skill.read_text(encoding="utf-8").splitlines()) <= 500

    def test_it_holds_no_emoji(self, skill):
        assert EMOJI.search(skill.read_text(encoding="utf-8")) is None


@pytest.mark.parametrize("skill", SKILLS, ids=_ids)
class TestTruth:
    def test_every_python_example_parses(self, skill):
        for body in _blocks(skill.read_text(encoding="utf-8"), "python"):
            ast.parse(body)

    def test_every_nexy_import_exists(self, skill):
        text = skill.read_text(encoding="utf-8")
        statements = re.findall(r"^from (nexy[\w.]*) import ([^\n]+)$", text, re.MULTILINE)
        for module, names in statements:
            for mod, name in _imported(module, names):
                assert hasattr(importlib.import_module(mod), name), f"{mod}.{name}"

    def test_every_config_field_exists(self, skill):
        from nexy.core.models import NexyConfigModel

        text = skill.read_text(encoding="utf-8")
        for field in set(re.findall(r"\b(use[A-Z]\w*)\s*=", text)):
            assert hasattr(NexyConfigModel, field), field

    def test_every_command_exists(self, skill):
        from nexy.modules.cli import CLI

        known = {c.name or c.callback.__name__ for c in CLI.registered_commands}
        text = skill.read_text(encoding="utf-8")
        invoked = re.findall(r"(?:^|`)(?:nx|nexy) ([a-z]+)\b", text, re.MULTILINE)
        for command in set(invoked):
            assert command in known, command

    def test_every_source_path_exists(self, skill):
        text = skill.read_text(encoding="utf-8")
        for path in set(re.findall(r"`(nexy/[\w/.-]+)`", text)):
            assert (ROOT / path.rstrip("/")).exists(), path


@pytest.mark.parametrize("skill", FRAMEWORK_SKILLS, ids=_ids)
def test_the_client_names_a_framework_skill_uses_exist_for_that_framework(skill):
    source = (CLIENT / CLIENT_FILE[skill.parent.name]).read_text(encoding="utf-8")
    text = skill.read_text(encoding="utf-8")
    for name in re.findall(r"`(\w+)` from `@nexy/client`", text):
        assert re.search(rf"export (?:const|function|type) {name}\b", source), name


def test_every_skill_is_listed_in_the_index():
    index = (ROOT / "skills" / "README.md").read_text(encoding="utf-8")
    assert all(f"({path.parent.name}/SKILL.md)" in index for path in SKILLS)
