"""A stand-in for a command-line tool that runs on Windows as well as on Linux and macOS."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def fake_tool(folder: Path, name: str, output: str, code: int) -> str:
    """The path of a tool *name* that prints *output* and exits with *code*.

    A script with a shebang runs on Linux and macOS only: Windows answers WinError 193. There the
    tool is a `.cmd` file that hands the same script to this Python.
    """
    script = folder / f"{name}.py"
    script.write_text(f"import sys\nprint({output!r})\nsys.exit({code})\n", encoding="utf-8")
    if os.name == "nt":
        launcher = folder / f"{name}.cmd"
        launcher.write_text(f'@"{sys.executable}" "{script}" %*\r\n', encoding="utf-8")
        return str(launcher)
    tool = folder / name
    tool.write_text(f"#!{sys.executable}\n{script.read_text(encoding='utf-8')}", encoding="utf-8")
    tool.chmod(0o755)
    return str(tool)
