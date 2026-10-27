"""The lines of a prompt as styled fragments: pure functions, tested without a terminal."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from nexy.modules.cli.tui.theme import Glyphs
from nexy.modules.i18n import t

Fragments = list[tuple[str, str]]


@dataclass(frozen=True)
class Option:
    """One choice: the value it answers with, its label and a short description."""

    value: Any
    label: str
    hint: str = ""


def question(message: str, glyphs: Glyphs, *, answered: bool = False) -> Fragments:
    """The line that asks, or that remembers having asked."""
    mark, style = (
        (glyphs.answered, "class:answered") if answered else (glyphs.asking, "class:question")
    )
    return [(style, f"{mark}  {message}\n")]


def options(choices: Sequence[Option], index: int, glyphs: Glyphs) -> Fragments:
    """One line per option: a radio mark, the label (coloured when current) and its description."""
    width = max((len(option.label) for option in choices), default=0)
    lines: Fragments = []
    for position, option in enumerate(choices):
        current = position == index
        suffix = ".selected" if current else ""
        radio = glyphs.selected if current else glyphs.unselected
        lines.append(("class:gutter", f"{glyphs.gutter}  "))
        lines.append((f"class:radio{suffix}", f"{radio} "))
        lines.append((f"class:label{suffix}", option.label.ljust(width)))
        if option.hint:
            lines.append((f"class:hint{suffix}", f"  {option.hint}"))
        lines.append(("", "\n"))
    return lines


def footer(glyphs: Glyphs, *, back: bool, move: bool = True) -> Fragments:
    """The keys that work, dimmed under the options."""
    keys = []
    if move:
        keys.append(f"↑↓ {t('tui.keys.move', 'move')}")
    keys.append(f"enter {t('tui.keys.choose', 'choose')}")
    if back:
        keys.append(f"← {t('tui.keys.back', 'back')}")
    keys.append(f"ctrl+c {t('tui.keys.quit', 'quit')}")
    separator = f" {glyphs.separator} "
    return [("class:gutter", f"{glyphs.gutter}  "), ("class:keys", separator.join(keys) + "\n")]


def answered(message: str, answer: str, glyphs: Glyphs) -> Fragments:
    """What stays on screen once a question is answered."""
    return [
        *question(message, glyphs, answered=True),
        ("class:gutter", f"{glyphs.gutter}  "),
        ("class:label.selected", f"{answer}\n"),
        ("class:gutter", f"{glyphs.gutter}\n"),
    ]


def gutter(glyphs: Glyphs) -> Fragments:
    return [("class:gutter", f"{glyphs.gutter}\n")]
