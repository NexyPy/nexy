"""`nx skills` adds or refreshes the agent files of an existing project."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from nexy.modules.cli import CLI

runner = CliRunner()


def _project(root: Path) -> Path:
    (root / "nexyconfig.py").write_text(
        "class NexyConfig(NexyConfigModel):\n    useFF = vue()\n    useCSR = True\n",
        encoding="utf-8",
    )
    (root / "package.json").write_text('{"devDependencies":{"tailwindcss":"4"}}', encoding="utf-8")
    return root


def test_it_installs_the_skills_of_the_project_stack(tmp_path):
    result = runner.invoke(CLI, ["skills", str(_project(tmp_path))])
    assert result.exit_code == 0
    assert (tmp_path / ".claude/skills/nexy-vue/SKILL.md").is_file()


def test_it_writes_agents_md_for_that_stack(tmp_path):
    runner.invoke(CLI, ["skills", str(_project(tmp_path))])
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "Vue" in text and "Tailwind" in text


def test_it_says_what_it_did(tmp_path):
    result = runner.invoke(CLI, ["skills", str(_project(tmp_path))])
    assert ".agents/skills" in result.output and ".claude/skills" in result.output


def test_it_keeps_the_agents_md_you_wrote_and_says_so(tmp_path):
    _project(tmp_path)
    (tmp_path / "AGENTS.md").write_text("mine\n", encoding="utf-8")
    result = runner.invoke(CLI, ["skills", str(tmp_path)])
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "mine\n"
    assert "AGENTS.md" in result.output


def test_it_refuses_a_folder_that_is_not_a_nexy_project(tmp_path):
    result = runner.invoke(CLI, ["skills", str(tmp_path)])
    assert result.exit_code == 1 and "nexyconfig.py" in result.output
    assert not (tmp_path / ".claude").exists()


def test_it_works_from_the_current_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(_project(tmp_path))
    assert runner.invoke(CLI, ["skills"]).exit_code == 0
