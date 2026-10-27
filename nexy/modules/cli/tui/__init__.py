"""The terminal interface of the CLI: prompts that look the same everywhere and can go back.

from nexy.modules.cli import tui

answer = tui.select("Choose a style", [tui.Option("tw", "Tailwind CSS", "utility classes")])
"""

from nexy.modules.cli.tui.prompts import BACK, confirm, select, text
from nexy.modules.cli.tui.render import Option
from nexy.modules.cli.tui.terminal import Terminal, terminal
from nexy.modules.cli.tui.transcript import transcript

__all__ = ["BACK", "Option", "Terminal", "confirm", "select", "terminal", "text", "transcript"]
