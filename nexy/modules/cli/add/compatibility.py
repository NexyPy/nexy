"""Check the version ranges a module declares against the versions of the project."""

from __future__ import annotations

import operator
import re
from collections.abc import Callable

_COMPARATOR = re.compile(r"(>=|<=|==|!=|>|<)?\s*([0-9]+(?:\.[0-9]+){1,2})")
_OPERATORS: dict[str, Callable[[tuple[int, ...], tuple[int, ...]], bool]] = {
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
    "==": operator.eq,
    "!=": operator.ne,
}


def _numbers(value: str) -> tuple[int, ...]:
    parts = [int(part) for part in value.split(".")]
    return (*parts, *([0] * (3 - len(parts))))


def _holds(current: tuple[int, ...], comparison: str) -> bool:
    match = _COMPARATOR.fullmatch(comparison.strip())
    if match is None:
        return False
    symbol, value = match.groups()
    return _OPERATORS[symbol](current, _numbers(value)) if symbol else current == _numbers(value)


def is_compatible(constraint: str, version: str) -> bool:
    """Whether *version* satisfies every comma-separated comparator in *constraint*."""
    if not constraint.strip():
        return True
    current = _numbers(version)
    return all(_holds(current, item) for item in constraint.split(","))
