import re

from nexy.core.models import ScanResult


class Scanner:
    """
    Separates Python logic from HTML/Jinja template.
    Logic is only extracted if enclosed by two '---' markers.
    """

    # The block closes on a line that is only `---`: a `---` inside a line of Python (a string,
    # a comment) stays Python.
    _PATTERN = re.compile(
        r"\A\s*---\s*(?P<logic>.*?)^[ \t]*---[ \t]*\r?$\s*(?P<template>.*)",
        re.DOTALL | re.MULTILINE,
    )

    def scan(self, source: str) -> ScanResult:
        """Split a .nexy file into its logic block and its template.

        Only a file that opens with ``---`` has logic, and the block must be closed. A ``---``
        anywhere else (a Markdown rule, a comment) belongs to the template.
        """
        content = (source or "").strip()
        match = self._PATTERN.match(content)
        if match:
            return ScanResult(
                logic_block=match.group("logic").strip(),
                template_block=match.group("template").strip(),
            )
        if content.startswith("---"):
            raise ValueError("Unclosed '---' delimiter")
        return ScanResult(logic_block="", template_block=content)

    def process(self, source: str) -> ScanResult:
        return self.scan(source)
