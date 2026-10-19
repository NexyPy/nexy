import re

from nexy.core.models import ScanResult


class Scanner:
    """
    Separates Python logic from HTML/Jinja template.
    Logic is only extracted if enclosed by two '---' markers.
    """

    _PATTERN = re.compile(
        r"^\s*---\s*(?P<logic>.*?)\s*---\s*(?P<template>.*)",
        re.DOTALL,
    )

    def scan(self, source: str) -> ScanResult:
        source_content = (source or "").strip()

        if not source_content:
            return ScanResult(logic_block="", template_block="")

        if "---" not in source_content:
            return ScanResult(
                logic_block="",
                template_block=source_content,
            )

        parts = source_content.split("---")

        if len(parts) < 3:
            if source_content.startswith("---"):
                raise ValueError("Unclosed '---' delimiter")
            else:
                return ScanResult(
                    logic_block="",
                    template_block=source_content,
                )

        match = self._PATTERN.match(source_content)

        if match:
            logic = match.group("logic").strip()
            template = match.group("template").strip()
            return ScanResult(
                logic_block=logic,
                template_block=template,
            )

        if source_content.startswith("---"):
            raise ValueError("Malformed .nexy file: content found before opening '---' delimiter")

        return ScanResult(
            logic_block="",
            template_block=source_content,
        )

    def process(self, source: str) -> ScanResult:
        return self.scan(source)
