"""The text of AGENTS.md and CLAUDE.md for one project."""

from __future__ import annotations

from pathlib import Path

from nexy.modules.cli.agents.profile import Profile

_FRAMEWORKS = {
    "none": "no client framework (HTML in `.nexy` pages)",
    "react": "React",
    "preact": "Preact",
    "solid": "Solid",
    "vue": "Vue",
    "svelte": "Svelte",
}
_STYLES = {"tailwind": "Tailwind", "unocss": "UnoCSS", "vanilla": "plain CSS"}
CLAUDE_MD = "@AGENTS.md\n"


def describe_skill(source: Path, name: str) -> str:
    """The first sentence of a skill's description: what it covers."""
    for line in (source / name / "SKILL.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("description:"):
            return line.partition(":")[2].strip().split(". ")[0].rstrip(".") + "."
    return ""


def _stack(profile: Profile) -> str:
    if profile.kind == "api":
        return "A Nexy API project: Python handlers, no views."
    mode = "client-routed (`useCSR = True`)" if profile.client_routed else "server-rendered"
    framework = _FRAMEWORKS.get(profile.framework, profile.framework)
    style = _STYLES.get(profile.style, profile.style)
    return f"A Nexy project: {mode}, {framework}, styled with {style}."


def _work_order(profile: Profile) -> list[str]:
    steps = ["Write the failing test, then the least code that passes."]
    if profile.kind != "api":
        steps.insert(
            0, "If the change has a view, audit the experience first: load `nexy-ux-audit`."
        )
    steps.append("Run `nx check`, `nx test` and `nx build`, and report what they print.")
    return [f"{number}. {step}" for number, step in enumerate(steps, 1)]


def _rules(profile: Profile) -> list[str]:
    rules = [
        "One function does one treatment, one class carries one intention, one folder holds one "
        "set of related intentions. Keep it simple.",
        "No emoji anywhere. Icons are real SVG. Text is plain and written for people.",
        "`__nexy__/` is generated: never edit it, never commit it.",
    ]
    if profile.kind != "api" and profile.framework != "none":
        rules.insert(2, "Write idiomatic code for the framework: no hand-written DOM scripts.")
    return [f"- {rule}" for rule in rules]


def render_agents_md(profile: Profile, source: Path, skills: list[str]) -> str:
    """AGENTS.md: the stack, the order of work, the rules, and the skills to load by topic."""
    listing = [f"- `{name}`: {describe_skill(source, name)}" for name in skills]
    sections = [
        f"# {profile.name}",
        _stack(profile),
        "## Order of work",
        "\n".join(_work_order(profile)),
        "## Rules",
        "\n".join(_rules(profile)),
        "## Commands",
        "`nx dev`, `nx build`, `nx start`, `nx test`, `nx check`.",
        "## Skills",
        "Installed in `.agents/skills/` and `.claude/skills/`. Load the one that matches the task:",
        "\n".join(listing),
        "Run `nx skills` to refresh them after upgrading Nexy.",
    ]
    return "\n\n".join(sections) + "\n"
