"""The answers left on screen, so that going back can take the last one away."""

from __future__ import annotations

from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.output import Output, create_output
from prompt_toolkit.shortcuts import print_formatted_text

from nexy.modules.cli.tui.render import Fragments
from nexy.modules.cli.tui.terminal import terminal
from nexy.modules.cli.tui.theme import STYLE


def _output() -> Output:
    return terminal.output or create_output()


class Transcript:
    """The height, in lines, of each block printed since the flow began."""

    def __init__(self) -> None:
        self._heights: list[int] = []

    def show(self, fragments: Fragments) -> None:
        """Print a block that stays on screen."""
        text = "".join(piece for _style, piece in fragments)
        print_formatted_text(FormattedText(fragments), style=STYLE, output=_output(), end="")
        self._heights.append(text.count("\n"))

    def erase_last(self) -> None:
        """Wipe the last block from the screen; nothing happens when there is none."""
        if not self._heights:
            return
        output = _output()
        output.cursor_up(self._heights.pop())
        output.erase_down()
        output.flush()

    def clear(self) -> None:
        self._heights.clear()


transcript = Transcript()
