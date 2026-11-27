"""A module reference is `@scope/name`, optionally pinned to one exact version."""

from __future__ import annotations

import pytest

from nexy.modules.cli.add.reference import ModuleReference, parse_reference


def test_parse_reference_ignores_a_built_in_component_name():
    assert parse_reference("button") is None


def test_parse_reference_reads_a_namespaced_module():
    assert parse_reference("@acme/auth") == ModuleReference("@acme/auth", None)


def test_parse_reference_reads_an_exact_version():
    assert parse_reference("@acme/auth@1.2.0") == ModuleReference("@acme/auth", "1.2.0")


@pytest.mark.parametrize("value", ["@Acme/auth", "@acme/../auth", "@acme/auth@latest", "@acme/"])
def test_parse_reference_refuses_a_malformed_name(value):
    with pytest.raises(ValueError, match="invalid module reference"):
        parse_reference(value)
