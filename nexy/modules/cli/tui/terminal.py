"""The terminal the prompts talk to: the real one, or a scripted one in tests."""

from __future__ import annotations

from dataclasses import dataclass

from prompt_toolkit.input import Input
from prompt_toolkit.output import Output


@dataclass
class Terminal:
    """Where keys come from and where the prompts draw; None means the process's own terminal."""

    input: Input | None = None
    output: Output | None = None


terminal = Terminal()
