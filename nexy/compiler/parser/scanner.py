import re
from nexy.core.models import ScanResult
class Scanner:
    _PATTERN = re.compile(
        r"^\s*---\s*(?P<frontmatter>.*?)\s*---\s*(?P<template>.*)",
        re.DOTALL,
    )

    def scan(self, source: str) -> ScanResult:
        match = self._PATTERN.match(source)

        if match:
            return ScanResult(
                logic_block=match.group("frontmatter").strip(),
                template_block=match.group("template").strip(),
            )

        # If no frontmatter, treat the entire source as the template block
        return ScanResult(
            logic_block="",
            template_block=source.strip(),
        )

    def process(self, source: str) -> ScanResult:
        return self.scan(source)