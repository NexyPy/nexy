"""Formatting of the two halves of a .nexy file: Python logic with ruff, the template with prettier.

Both tools reject what is specific to .nexy (imports of files, Jinja tags), so those parts are
swapped for something they accept before formatting and put back after.
"""

from __future__ import annotations

import re
import subprocess  # nosec B404

_NEXY_IMPORT = re.compile(r"^([ \t]*)((?:from|import)[ \t]+[\"'].*)$", re.MULTILINE)
_MARKED_IMPORT = re.compile(r"^([ \t]*)# nexy-import: (.*)$", re.MULTILINE)
_JINJA = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}", re.DOTALL)
_TOKEN = "NXFMT{index}Z"  # nosec B105 - placeholder pattern of the formatter, not a credential
_BLANK_RUNS = re.compile(r"\n{3,}")


class FormatError(Exception):
    """A half of a file could not be formatted; the message says why."""


def protect_imports(logic: str) -> str:
    """Turn `from "./x.nexy" import X` lines into comments, which ruff leaves alone."""
    return _NEXY_IMPORT.sub(r"\1# nexy-import: \2", logic)


def restore_imports(logic: str) -> str:
    return _MARKED_IMPORT.sub(r"\1\2", logic)


def protect_jinja(template: str) -> tuple[str, list[str]]:
    """Replace each Jinja tag with a word prettier treats as text; returns the tags in order."""
    tags: list[str] = []

    def swap(match: re.Match[str]) -> str:
        tags.append(match.group(0))
        return _TOKEN.format(index=len(tags) - 1)

    return _JINJA.sub(swap, template), tags


def restore_jinja(template: str, tags: list[str]) -> str:
    """Put the tags back; a tag that prettier lost means the result cannot be trusted."""
    for index, tag in enumerate(tags):
        token = _TOKEN.format(index=index)
        if token not in template:
            raise FormatError("a template tag was lost while formatting")
        template = template.replace(token, tag)
    return template


def normalize(template: str) -> str:
    """What is safe without prettier: no trailing spaces, no run of blank lines."""
    lines = [line.rstrip() for line in template.splitlines()]
    return _BLANK_RUNS.sub("\n\n", "\n".join(lines)).strip()


def _run(args: list[str], source: str) -> str:
    result = subprocess.run(args, input=source, capture_output=True, text=True)  # nosec B603
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        raise FormatError(detail[-1] if detail else f"exit {result.returncode}")
    return result.stdout


def format_logic(logic: str, ruff_exe: str | None) -> str:
    """The Python half, formatted by ruff (unchanged when ruff is missing)."""
    if not logic or not ruff_exe:
        return logic
    protected = protect_imports(logic)
    formatted = _run([ruff_exe, "format", "--stdin-filename", "block.py"], protected)
    return restore_imports(formatted)


def format_template(template: str, prettier_exe: str | None, name: str) -> str:
    """The template half, formatted by prettier, or just normalized when prettier is missing."""
    if not template:
        return template
    if not prettier_exe:
        return normalize(template)
    protected, tags = protect_jinja(template)
    formatted = _run([prettier_exe, "--parser", "html", "--stdin-filepath", name], protected)
    return normalize(restore_jinja(formatted, tags))
