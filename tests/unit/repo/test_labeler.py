"""A pull request labels itself with the areas of the files it changes (#298)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]


def _globs() -> dict[str, list[str]]:
    config = yaml.safe_load((ROOT / ".github" / "labeler.yml").read_text("utf-8"))
    return {
        label: [glob for rule in rules for glob in rule["changed-files"][0]["any-glob-to-any-file"]]
        for label, rules in config.items()
    }


def _matches(glob: str, path: str) -> bool:
    """The minimatch subset the file uses: `**` crosses folders, `*` stays in one."""
    parts = re.split(r"(\*\*|\*)", glob)
    regex = "".join({"**": ".*", "*": "[^/]*"}.get(part, re.escape(part)) for part in parts)
    return re.fullmatch(regex, path) is not None


def _labels(path: str) -> set[str]:
    return {label for label, globs in _globs().items() if any(_matches(g, path) for g in globs)}


@pytest.mark.parametrize(
    ("path", "label"),
    [
        ("nexy/modules/routers/app.py", "area:router"),
        ("nexy/modules/modular/metadata.py", "area:router"),
        ("nexy/modules/compiler/parser/scanner.py", "area:compiler"),
        ("nexy/modules/frontend/client/router.ts", "area:frontend"),
        ("nexy/modules/cli/commands/dev.py", "area:cli"),
        ("docs/guides/sitemap.md", "area:docs"),
        (".github/workflows/ci.yml", "area:ci"),
        ("extensions/vscode/src/extension.ts", "area:vscode"),
    ],
)
def test_labeler_gives_a_file_its_area(path, label):
    assert _labels(path) == {label}


def test_labeler_gives_every_label_the_area_prefix():
    assert all(label.startswith("area:") for label in _globs())


def test_labeler_leaves_a_file_of_no_area_unlabelled():
    assert _labels("pyproject.toml") == set()
