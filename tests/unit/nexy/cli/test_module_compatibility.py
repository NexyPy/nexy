"""A module installs only when its declared version ranges contain the project's versions."""

from __future__ import annotations

import pytest

from nexy.modules.cli.add.compatibility import is_compatible


@pytest.mark.parametrize(
    ("constraint", "version", "expected"),
    [
        (">=2.0.0", "2.11.2", True),
        ("<=2.11.2", "2.11.2", True),
        (">2.11.2", "2.11.2", False),
        ("<3.0.0", "2.11.2", True),
        ("==2.11.2", "2.11.2", True),
        ("!=2.11.2", "2.11.2", False),
        (">=2.0.0,<3.0.0", "2.11.2", True),
        (">=3.12", "3.13.0", True),
        ("2.11.2", "2.11.2", True),
        ("", "2.11.2", True),
        ("latest", "2.11.2", False),
    ],
)
def test_is_compatible_applies_each_comparator(constraint, version, expected):
    assert is_compatible(constraint, version) is expected
