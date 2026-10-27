"""Terminal setup the CLI needs before it prints: UTF-8 output and a console without ASCII boxes."""

from __future__ import annotations

import contextlib
import functools
import sys
from typing import Any

import typer.rich_utils


def use_utf8_streams() -> None:
    """Switch stdout and stderr to UTF-8: the CLI prints arrows and bars legacy code pages lack."""
    for stream in (sys.stdout, sys.stderr):
        encoding = (stream.encoding or "").lower()
        if encoding and encoding not in ("utf-8", "utf8"):
            with contextlib.suppress(Exception):
                stream_any: Any = stream
                stream_any.reconfigure(encoding="utf-8")


def keep_unicode_boxes() -> None:
    """Typer's help screens draw boxes with Unicode; stop Rich from degrading them to ASCII."""
    original = typer.rich_utils._get_rich_console

    @functools.wraps(original)
    def console_with_unicode_boxes(stderr: bool = False) -> Any:
        console = original(stderr=stderr)
        console.safe_box = False
        return console

    typer.rich_utils._get_rich_console = console_with_unicode_boxes
