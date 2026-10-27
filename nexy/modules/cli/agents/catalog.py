"""Which skills a project needs, from its stack."""

from __future__ import annotations

from nexy.modules.cli.agents.profile import Profile

FRAMEWORK_SKILLS = {
    "react": "nexy-react",
    "preact": "nexy-preact",
    "solid": "nexy-solid",
    "vue": "nexy-vue",
    "svelte": "nexy-svelte",
}
API_SKILLS = ("nexy-principles", "nexy-project", "nexy-backend", "nexy-security", "nexy-testing")
# Work on the framework itself is not work in a project built with it.
NEVER_SHIPPED = ("nexy-framework-dev",)
_ORDER = (
    "nexy-principles",
    "nexy-ux-audit",
    "nexy-project",
    "nexy-file",
    "nexy-markdown",
    *FRAMEWORK_SKILLS.values(),
    "nexy-styling",
    "nexy-backend",
    "nexy-security",
    "nexy-testing",
)


def _wanted(profile: Profile) -> set[str]:
    if profile.kind == "api":
        return set(API_SKILLS)
    wanted = set(API_SKILLS) | {"nexy-ux-audit", "nexy-styling"}
    if not profile.client_routed:
        wanted |= {"nexy-file", "nexy-markdown"}
    framework = FRAMEWORK_SKILLS.get(profile.framework)
    return wanted | {framework} if framework else wanted


def select_skills(profile: Profile) -> list[str]:
    """The skills to install for *profile*, in the order they are listed."""
    wanted = _wanted(profile)
    return [name for name in _ORDER if name in wanted]
