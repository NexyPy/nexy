"""The rules of the list: what is an email, and what joining twice does."""

import pytest

from src.services.waitlist import clean, join, problem


def test_an_email_is_kept_in_lower_case_without_spaces_around():
    assert clean("  Ada@Example.COM ") == "ada@example.com"


def test_an_email_can_join():
    assert problem("ada@example.com") == ""


def test_an_empty_email_is_asked_for():
    assert problem("") == "empty"


def test_an_email_longer_than_an_address_is_refused():
    assert problem("a" * 250 + "@example.com") == "long"


@pytest.mark.parametrize(
    "written",
    [
        "ada",
        "ada@",
        "@example.com",
        "ada@example",
        "ada@@example.com",
        "a da@example.com",
        "<script>@example.com",
        "ada@example.",
        "ada@.com",
    ],
)
def test_what_is_not_an_email_is_refused(written):
    assert problem(written) == "invalid"


def test_joining_stores_the_cleaned_email(emails):
    join(" Ada@Example.com ")
    assert emails() == ["ada@example.com"]


def test_joining_twice_keeps_one_row(emails):
    join("ada@example.com")
    join("ADA@example.com")
    assert emails() == ["ada@example.com"]


def test_joining_twice_answers_as_the_first_time():
    join("ada@example.com")
    assert join("ada@example.com") == "joined"


def test_a_refused_email_is_not_stored(emails):
    join("not an email")
    assert emails() == []
