"""Copies a template directory into a project, rendering its .jinja2 files with its context."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from nexy.modules.cli.constants import TEMPLATES_DIR

# Markup shared by every framework (header, footer, the starter pages): templates `include` it.
PARTIALS_DIR = TEMPLATES_DIR / "_partials"

# A suffix before `.jinja2` keeps a file for one framework only (``card.tsx.react.jinja2``).
FRAMEWORK_SUFFIXES = {
    ".react": "react",
    ".vue": "vue",
    ".svelte": "svelte",
    ".solid": "solid",
    ".preact": "preact",
    ".none": "none",
}
# A bare `.jinja2` file gets the extension of the framework: one file, many outputs.
FRAMEWORK_EXTENSIONS = {
    "none": ".nexy",
    "vue": ".vue",
    "svelte": ".svelte",
    "react": ".tsx",
    "preact": ".tsx",
    "solid": ".tsx",
}


def _split_framework_suffixes(parts: list[str], framework: str) -> tuple[list[str], bool, bool]:
    """(name parts without framework suffixes, one suffix is this framework's, one is not)."""
    matched = skipped = False
    while len(parts) > 1 and f".{parts[-1]}" in FRAMEWORK_SUFFIXES:
        if FRAMEWORK_SUFFIXES[f".{parts.pop()}"] == framework:
            matched = True
        else:
            skipped = True
    return parts, matched, skipped


def resolve_target(rel: Path, framework: str) -> Path | None:
    """Where the template file *rel* goes for *framework*; None when it is for another one."""
    framework = framework.lower()
    parts = rel.name.split(".")
    is_template = parts[-1] == "jinja2"
    if is_template:
        parts.pop()
    stripped = ".".join(parts)
    parts, matched, skipped = _split_framework_suffixes(parts, framework)
    belongs_to_another = not matched and stripped.endswith(tuple(FRAMEWORK_SUFFIXES))
    if skipped or belongs_to_another:
        return None
    target = ".".join(parts)
    if is_template:
        needs_extension = matched or "." not in target
        target += (FRAMEWORK_EXTENSIONS.get(framework, "") if needs_extension else "") + ".jinja2"
    return rel.parent / target


class TemplateRenderer:
    """Copies a local template directory and renders .jinja2 files with context.

    Supports suffix-based filtering: files ending with .react, .vue, .svelte, .solid, .preact
    are only included when client_framework matches. The suffix is stripped from the destination
    filename, and a bare .jinja2 file gets the framework's extension (see `resolve_target`).

    *exclude_suffixes* drops whole file kinds from the scaffold (e.g. ``.nexy`` when
    client-side routing owns the views).
    """

    def __init__(
        self,
        src: Path,
        dest: Path,
        context: dict[str, Any] | None = None,
        exclude_suffixes: set[str] | None = None,
    ):
        self.src = src
        self.dest = dest
        self.context = context or {}
        self.exclude_suffixes = exclude_suffixes or set()

    def render(self) -> None:
        if not self.src.is_dir():
            raise FileNotFoundError(f"Template directory not found: {self.src}")
        # Scaffolding templates emit Python/TS/HTML source files; autoescape would corrupt the
        # generated source code. See SECURITY.md.
        environment = Environment(loader=FileSystemLoader([str(self.src), str(PARTIALS_DIR)]))  # nosec B701
        self.dest.mkdir(parents=True, exist_ok=True)
        for source in self.src.rglob("*"):
            if source.is_file():
                self._write(source, environment)
        self._remove_empty_directories()

    def _write(self, source: Path, environment: Environment) -> None:
        rel = source.relative_to(self.src)
        target = resolve_target(rel, self.context.get("client_framework", ""))
        if target is None:
            return
        destination = self.dest / target
        final = destination.with_suffix("") if target.suffix == ".jinja2" else destination
        if source.suffix in self.exclude_suffixes or final.suffix in self.exclude_suffixes:
            return
        if target.suffix == ".jinja2":
            self._render_file(environment, rel, final)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    def _render_file(self, environment: Environment, rel: Path, final: Path) -> None:
        """Render a template; one that renders to nothing writes nothing."""
        output = environment.get_template(rel.as_posix()).render(**self.context)
        if output.strip():
            final.parent.mkdir(parents=True, exist_ok=True)
            final.write_text(output, encoding="utf-8")

    def _remove_empty_directories(self) -> None:
        """Deepest first, so a folder that only held empty folders goes too."""
        for path in sorted(self.dest.rglob("*"), key=lambda p: len(str(p)), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()
