"""A generated project tells whoever opens it to work inside its virtual environment.

The README is the first file read, and AGENTS.md is what a coding agent follows: both must say that
`nexy` commands run inside `.venv`, or the first `nexy dev` fails on a package the project needs.
"""

from __future__ import annotations

import pytest

from nexy.modules.cli.agents import Profile
from nexy.modules.cli.agents.document import render_agents_md
from nexy.modules.cli.init.template_setup import _render_local_template

ACTIVATE = r".venv\Scripts\activate"


@pytest.fixture(params=["web-fbr", "web-modular", "api-fbr", "api-modular"])
def readme(request, tmp_path):
    template = request.param
    config = {
        "client_framework": "none",
        "FBRouter": template.endswith("fbr"),
        "project_type": template.split("-")[0],
        "orm": "None",
        "useCSR": False,
    }
    _render_local_template(template, tmp_path, config, "demo")
    return (tmp_path / "README.md").read_text(encoding="utf-8")


def test_the_readme_activates_the_virtual_environment(readme):
    assert ACTIVATE in readme and "source .venv/bin/activate" in readme


def test_the_readme_activates_it_before_starting_the_server(readme):
    assert readme.index("activate") < readme.index("nexy dev")


def test_the_readme_offers_uv_run(readme):
    assert "uv run nexy dev" in readme


def test_agents_md_says_commands_run_inside_the_virtual_environment(tmp_path):
    (tmp_path / "nexy-principles").mkdir()
    (tmp_path / "nexy-principles" / "SKILL.md").write_text(
        "---\nname: nexy-principles\ndescription: x. Load it first.\n---\n", encoding="utf-8"
    )
    profile = Profile("demo", "none", False, "tailwind", "web", "fbr")
    text = render_agents_md(profile, tmp_path, ["nexy-principles"])
    assert "virtual environment" in text and "uv run" in text
