"""Python types become the TypeScript types of `@nexy/actions`."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

import pytest
from pydantic import BaseModel

from nexy.modules.routers.actions.typescript import ts_type


class Role(StrEnum):
    admin = "admin"
    member = "member"


class Opaque:
    pass


class Address(BaseModel):
    city: str


class User(BaseModel):
    name: str
    age: int | None = None
    address: Address
    tags: list[str] = []


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (int, "number"),
        (float, "number"),
        (str, "string"),
        (bool, "boolean"),
        (None, "null"),
        (list[int], "number[]"),
        (list[int | str], "(number | string)[]"),
        (dict[str, int], "{ [key: string]: number }"),
        (str | None, "string | null"),
        (Literal["a", "b"], '"a" | "b"'),
        (tuple[int, str], "[number, string]"),
        (Any, "unknown"),
    ],
)
def test_a_builtin_type_maps_to_its_typescript_type(annotation, expected):
    assert ts_type(annotation, {}) == expected


def test_a_model_becomes_a_named_type():
    declarations: dict[str, str] = {}
    assert ts_type(User, declarations) == "User"
    assert "name: string" in declarations["User"]


def test_a_nested_model_is_declared_once_and_referenced_by_name():
    declarations: dict[str, str] = {}
    ts_type(User, declarations)
    assert declarations["Address"] == "{ city: string }"
    assert "address: Address" in declarations["User"]


def test_a_field_with_a_default_is_optional_for_an_input():
    declarations: dict[str, str] = {}
    ts_type(User, declarations, mode="validation")
    assert "age?:" in declarations["User"]


def test_an_enum_is_a_union_of_its_values():
    declarations: dict[str, str] = {}
    ts_type(Role, declarations)
    assert declarations["Role"] == '"admin" | "member"'


def test_a_type_pydantic_cannot_describe_is_unknown():
    assert ts_type(Opaque, {}) == "unknown"
