"""The names a developer types after `nx add` for a registry module."""

from __future__ import annotations

import re
from dataclasses import dataclass

_REFERENCE = re.compile(
    r"@(?P<scope>[a-z0-9][a-z0-9-]{0,38})/(?P<name>[a-z0-9][a-z0-9-]{0,48})"
    r"(?:@(?P<version>[0-9]+\.[0-9]+\.[0-9]+))?"
)


@dataclass(frozen=True)
class ModuleReference:
    """A registry module name and its optional exact version."""

    name: str
    version: str | None


def parse_reference(value: str) -> ModuleReference | None:
    """Read `@scope/name` or `@scope/name@1.2.0`; other arguments are not module names."""
    if not value.startswith("@"):
        return None
    match = _REFERENCE.fullmatch(value)
    if match is None:
        raise ValueError(f"invalid module reference: {value}")
    name = f"@{match.group('scope')}/{match.group('name')}"
    return ModuleReference(name, match.group("version"))
