"""How the prompts look: colours and the plain glyphs every terminal can print."""

from __future__ import annotations

from dataclasses import dataclass

from prompt_toolkit.styles import Style

ACCENT = "#00d084"

STYLE = Style.from_dict(
    {
        "gutter": "#525252",
        "question": f"bold {ACCENT}",
        "answered": "#737373",
        "label": "#a3a3a3",
        "label.selected": f"bold {ACCENT}",
        "hint": "#525252",
        "hint.selected": "#a3a3a3",
        "radio": "#525252",
        "radio.selected": ACCENT,
        "keys": "#525252",
        "error": "bold #ef4444",
        "input": "#ededed",
        "title": "bold #ededed",
        "step": "#737373",
    }
)


@dataclass(frozen=True)
class Glyphs:
    """The characters of the prompt frame: only ones a person types."""

    asking: str
    answered: str
    start: str
    end: str
    gutter: str
    selected: str
    unselected: str
    pointer: str
    separator: str


ASCII = Glyphs("*", "o", "+", "+", "|", "(x)", "( )", ">", "-")


def glyphs_for(encoding: str | None = None) -> Glyphs:
    """The plain glyphs, on every terminal, whatever its encoding."""
    del encoding
    return ASCII
