import re

DELIMITER = "---"

_FRONTMATTER_RE = re.compile(
    rf"^\s*{DELIMITER}\s*(?P<logic>.*?)\s*{DELIMITER}\s*(?P<template>.*)",
    re.DOTALL,
)


def split_frontmatter(source: str) -> tuple[str, str]:
    """Split *source* into (logic, template) at the opening '---' pair."""
    match = _FRONTMATTER_RE.match(source)
    if not match:
        return "", source
    return match.group("logic"), match.group("template")


def reassemble_frontmatter(logic: str, template: str) -> str:
    """Join logic and template back into a canonical .nexy document."""
    if not logic:
        return template
    return f"{DELIMITER}\n{logic.strip()}\n{DELIMITER}\n{template.strip()}\n"
