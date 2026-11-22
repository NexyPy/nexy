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
    nexy_files: bool = True

    @property
    def writes_nexy(self) -> bool:
        """Whether the project has `.nexy` files: a server-rendered web project that keeps them."""
        return self.kind == "web" and not self.client_routed and self.nexy_files


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


def _kind_of(project: Path, config: str) -> str:
    """A project with views has a client framework or a package.json; an API project has neither."""
    has_views = _FRAMEWORK.search(config) or (project / "package.json").is_file()
    return "web" if has_views else "api"


def _has_nexy_files(project: Path) -> bool:
    """A `.nexy` file anywhere in `src/`; a project without `src/` is taken at its mode."""
    src = project / "src"
    return not src.is_dir() or next(src.rglob("*.nexy"), None) is not None


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
        kind=_kind_of(project, config),
        router="modular" if _MODULAR.search(config) else "fbr",
        nexy_files=_has_nexy_files(project),
    )
