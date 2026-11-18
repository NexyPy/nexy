"""A new web project never asks for a dependency below the release that fixed a known advisory."""

from __future__ import annotations

import json
from pathlib import Path

import jinja2
import pytest

import nexy

TEMPLATE = Path(nexy.__file__).parent / "modules/cli/templates/_shared/web/package.json.jinja2"
FRAMEWORKS = ["none", "react", "vue", "svelte", "solid", "preact"]

# The first release of each package that fixed an advisory its earlier ones carry.
FLOORS = {
    "glob": ((14, 0, 2), "GHSA-3g3m-2fjr-6pw4, and minimatch GHSA-g3hv-75wg-m249 through it"),
}


def _dependencies(framework: str) -> dict[str, str]:
    source = jinja2.Template(TEMPLATE.read_text(encoding="utf-8"))
    package = json.loads(source.render(client_framework=framework, style="tailwind"))
    return {**package["dependencies"], **package["devDependencies"]}


def _lowest(spec: str) -> tuple[int, ...]:
    """The lowest version a caret or tilde range accepts: `^13.0.6` accepts 13.0.6 first."""
    return tuple(int(part) for part in spec.lstrip("^~>=").split("."))


@pytest.mark.parametrize("framework", FRAMEWORKS)
@pytest.mark.parametrize("name", sorted(FLOORS))
def test_a_starter_asks_for_a_fixed_release(name, framework):
    floor, advisory = FLOORS[name]
    assert _lowest(_dependencies(framework)[name]) >= floor, advisory
