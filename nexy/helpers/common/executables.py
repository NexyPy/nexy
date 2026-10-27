"""Finding a command-line tool the same way on Windows, macOS and Linux."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def find_tool(name: str) -> str | None:
    """The path of the tool *name*, or None.

    The PATH comes first. Then the folder of the interpreter that runs Nexy: a tool installed in a
    virtual environment sits there (`bin` or `Scripts`) even when the environment is not activated.
    """
    found = shutil.which(name)
    if found:
        return found
    folder = Path(sys.executable).parent
    suffix = ".exe" if os.name == "nt" else ""
    for candidate in (folder / f"{name}{suffix}", folder / "Scripts" / f"{name}{suffix}"):
        if candidate.is_file():
            return str(candidate)
    return None
