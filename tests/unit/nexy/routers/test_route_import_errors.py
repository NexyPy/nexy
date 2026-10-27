"""A route file that fails to import must say what failed and where, not only `'src'`."""

from __future__ import annotations

from nexy.modules.routers.fbrouter.scanner import describe_import_error


def _raise_key_error() -> None:
    {}["src"]  # noqa: B018


def test_the_description_names_the_exception_type_and_message():
    try:
        _raise_key_error()
    except KeyError as error:
        text = describe_import_error(error)
    assert text.startswith("KeyError: 'src'")


def test_the_description_points_at_the_line_that_raised():
    try:
        _raise_key_error()
    except KeyError as error:
        text = describe_import_error(error)
    assert "test_route_import_errors.py:" in text


def test_an_exception_without_a_traceback_is_still_described():
    assert describe_import_error(ValueError("boom")) == "ValueError: boom"
