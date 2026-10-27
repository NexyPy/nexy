"""What the agent files are tailored to: the stack of one project."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_FRAMEWORK = re.compile(r"^\s*useFF\s*=\s*(\w+)\(", re.MULTILINE)
_CLIENT_ROUTED = re.compile(r"^\s*useCSR\s*=\s*True\b", re.MULTILINE)
_MODULAR = re.compile(r"^\s*useRouter\s*=", re.MULTILINE)


@dataclass(frozen=True)
class Profile:
    """The stack of a project: its name, client framework, routing mode and style mode."""

    name: str
    framework: str
    client_routed: bool
    style: str
    kind: str = "web"
    router: str = "fbr"


def profile_from_context(context: dict[str, Any]) -> Profile:
    """The profile of a project that is being scaffolded."""
    style = context.get("style", "tailwind")
    return Profile(
        name=context.get("project_name", "app"),
        framework=context.get("client_framework", "none"),
        client_routed=bool(context.get("useCSR", False)),
        style="vanilla" if style == "other" else style,
        kind=context.get("project_type", "web"),
        router="fbr" if context.get("FBRouter", False) else "modular",
    )


def _style_of(project: Path) -> str:
    try:
        package = json.loads((project / "package.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "vanilla"
    dependencies = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    for style in ("tailwindcss", "unocss"):
        if style in dependencies:
            return "tailwind" if style == "tailwindcss" else style
    return "vanilla"


def detect_profile(project: Path) -> Profile:
    """The profile of an existing project, read from its files without running its code."""
    try:
        config = (project / "nexyconfig.py").read_text(encoding="utf-8")
    except OSError:
        config = ""
    found = _FRAMEWORK.search(config)
    return Profile(
        name=project.resolve().name,
        framework=found.group(1) if found else "none",
        client_routed=bool(_CLIENT_ROUTED.search(config)),
        style=_style_of(project),
        router="modular" if _MODULAR.search(config) else "fbr",
    )
