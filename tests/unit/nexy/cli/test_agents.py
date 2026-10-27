"""A new project ships the rules for coding agents for its stack and never overwrites files."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from nexy.modules.cli.agents import (
    Profile,
    detect_profile,
    install_agent_files,
    select_skills,
    skills_source,
)
from nexy.modules.cli.init.template_setup import _render_local_template

EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")
ALWAYS = {
    "nexy-principles",
    "nexy-project",
    "nexy-backend",
    "nexy-testing",
    "nexy-security",
}


def _profile(
    framework: str = "react", client_routed: bool = True, style: str = "unocss", kind: str = "web"
) -> Profile:
    return Profile("demo", framework, client_routed, style, kind)


def _installed(root: Path, where: str) -> set[str]:
    return {path.parent.name for path in (root / where).glob("*/SKILL.md")}


class TestSelection:
    def test_every_project_gets_the_rules_that_always_apply(self):
        assert set(select_skills(_profile())) >= ALWAYS

    def test_the_skill_for_work_on_nexy_itself_is_never_shipped(self):
        assert "nexy-framework-dev" not in select_skills(_profile())

    def test_a_client_routed_project_gets_its_framework_skill_only(self):
        chosen = set(select_skills(_profile("vue")))
        assert "nexy-vue" in chosen and "nexy-react" not in chosen

    def test_a_client_routed_project_has_no_nexy_pages(self):
        chosen = set(select_skills(_profile("react")))
        assert "nexy-file" not in chosen and "nexy-markdown" not in chosen

    def test_a_server_project_gets_the_page_skills(self):
        chosen = set(select_skills(_profile("none", client_routed=False)))
        assert {"nexy-file", "nexy-markdown"} <= chosen

    def test_a_server_project_with_islands_gets_the_framework_skill_too(self):
        chosen = set(select_skills(_profile("react", client_routed=False)))
        assert {"nexy-file", "nexy-react"} <= chosen

    def test_an_api_project_has_no_view_skills(self):
        chosen = set(select_skills(_profile("none", client_routed=False, kind="api")))
        assert chosen == ALWAYS

    def test_a_project_with_views_gets_the_experience_audit_and_styling(self):
        assert {"nexy-ux-audit", "nexy-styling"} <= set(select_skills(_profile()))


class TestInstall:
    def test_the_skills_land_where_each_tool_looks(self, tmp_path):
        install_agent_files(tmp_path, _profile())
        assert _installed(tmp_path, ".agents/skills") == _installed(tmp_path, ".claude/skills")
        assert "nexy-react" in _installed(tmp_path, ".agents/skills")

    def test_both_copies_are_identical(self, tmp_path):
        install_agent_files(tmp_path, _profile())
        one = (tmp_path / ".agents/skills/nexy-principles/SKILL.md").read_bytes()
        two = (tmp_path / ".claude/skills/nexy-principles/SKILL.md").read_bytes()
        assert one == two

    def test_agents_md_names_the_stack(self, tmp_path):
        install_agent_files(tmp_path, _profile("react", True, "tailwind"))
        text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "React" in text and "Tailwind" in text and "client-routed" in text

    def test_agents_md_lists_every_installed_skill(self, tmp_path):
        install_agent_files(tmp_path, _profile())
        text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert all(f"`{name}`" in text for name in _installed(tmp_path, ".agents/skills"))

    def test_agents_md_starts_with_the_order_of_work(self, tmp_path):
        install_agent_files(tmp_path, _profile())
        text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert text.index("audit") < text.index("failing test")

    def test_agents_md_stays_short_and_plain(self, tmp_path):
        install_agent_files(tmp_path, _profile())
        text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert len(text.splitlines()) <= 80 and EMOJI.search(text) is None

    def test_claude_code_reads_it_through_an_import(self, tmp_path):
        install_agent_files(tmp_path, _profile())
        assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8").startswith("@AGENTS.md")

    def test_an_api_project_is_not_told_to_audit_views(self, tmp_path):
        install_agent_files(tmp_path, _profile("none", False, "tailwind", "api"))
        text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "nexy-ux-audit" not in text


class TestNeverClobber:
    def test_an_existing_agents_md_is_kept(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("mine\n", encoding="utf-8")
        install_agent_files(tmp_path, _profile())
        assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "mine\n"

    def test_an_existing_claude_md_is_kept(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("mine\n", encoding="utf-8")
        install_agent_files(tmp_path, _profile())
        assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == "mine\n"

    def test_a_skill_of_the_project_is_left_alone(self, tmp_path):
        own = tmp_path / ".claude/skills/billing"
        own.mkdir(parents=True)
        (own / "SKILL.md").write_text("mine\n", encoding="utf-8")
        install_agent_files(tmp_path, _profile())
        assert (own / "SKILL.md").read_text(encoding="utf-8") == "mine\n"

    def test_a_second_run_refreshes_the_nexy_skills(self, tmp_path):
        install_agent_files(tmp_path, _profile())
        target = tmp_path / ".agents/skills/nexy-principles/SKILL.md"
        target.write_text("stale\n", encoding="utf-8")
        install_agent_files(tmp_path, _profile())
        assert target.read_text(encoding="utf-8") != "stale\n"

    def test_a_skill_that_no_longer_applies_is_removed(self, tmp_path):
        install_agent_files(tmp_path, _profile("react"))
        install_agent_files(tmp_path, _profile("vue"))
        assert "nexy-react" not in _installed(tmp_path, ".agents/skills")

    def test_it_reports_what_it_kept(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("mine\n", encoding="utf-8")
        report = install_agent_files(tmp_path, _profile())
        assert report.kept == ["AGENTS.md"]


class TestSource:
    def test_the_skills_are_found_in_a_source_checkout_and_in_a_wheel(self):
        assert (skills_source() / "nexy-principles" / "SKILL.md").is_file()


@pytest.mark.parametrize(("framework", "csr"), [("react", True), ("none", False), ("vue", True)])
class TestScaffold:
    def _config(self, framework: str, csr: bool, **extra) -> dict:
        return {
            "client_framework": framework,
            "FBRouter": True,
            "project_type": "web",
            "orm": "None",
            "useCSR": csr,
            "style": "tailwind",
            **extra,
        }

    def test_a_new_project_ships_agents_md_and_the_skills(self, tmp_path, framework, csr):
        _render_local_template("web-fbr", tmp_path, self._config(framework, csr), "demo")
        assert (tmp_path / "AGENTS.md").is_file()
        assert "nexy-principles" in _installed(tmp_path, ".agents/skills")

    def test_a_project_can_opt_out(self, tmp_path, framework, csr):
        config = self._config(framework, csr, agents=False)
        _render_local_template("web-fbr", tmp_path, config, "demo")
        assert not (tmp_path / "AGENTS.md").exists()
        assert not (tmp_path / ".agents").exists()


class TestDetect:
    def _project(self, root: Path, config: str, package: str = "{}") -> Path:
        (root / "nexyconfig.py").write_text(config, encoding="utf-8")
        (root / "package.json").write_text(package, encoding="utf-8")
        return root

    def test_a_client_routed_react_project(self, tmp_path):
        config = "class NexyConfig(NexyConfigModel):\n    useFF = react()\n    useCSR = True\n"
        profile = detect_profile(
            self._project(tmp_path, config, '{"devDependencies":{"unocss":"1"}}')
        )
        assert (profile.framework, profile.client_routed, profile.style) == (
            "react",
            True,
            "unocss",
        )

    def test_a_server_project_without_a_framework(self, tmp_path):
        profile = detect_profile(
            self._project(tmp_path, "class NexyConfig(NexyConfigModel):\n    pass\n")
        )
        assert (profile.framework, profile.client_routed, profile.style) == (
            "none",
            False,
            "vanilla",
        )

    def test_tailwind_is_read_from_the_dependencies(self, tmp_path):
        config = "class NexyConfig(NexyConfigModel):\n    useFF = svelte()\n"
        package = '{"devDependencies":{"tailwindcss":"4"}}'
        assert detect_profile(self._project(tmp_path, config, package)).style == "tailwind"
