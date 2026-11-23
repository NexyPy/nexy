import sqlite3

import pytest

from src.accounts import store

EMAIL = "ada@example.com"
PASSWORD = "correct horse battery"


def test_a_new_account_can_sign_in():
    store.create(EMAIL, PASSWORD)
    assert store.authenticate(EMAIL, PASSWORD) is not None


def test_an_email_is_kept_in_lower_case():
    store.create("  Ada@Example.COM ", PASSWORD)
    assert store.authenticate(EMAIL, PASSWORD) is not None


def test_a_second_account_with_the_same_email_is_refused():
    store.create(EMAIL, PASSWORD)
    assert store.create(EMAIL.upper(), PASSWORD)[1] == "taken"


@pytest.mark.parametrize("email", ["", "ada", "ada@", "@example.com", "a da@example.com"])
def test_an_email_that_is_not_one_is_refused(email):
    assert store.create(email, PASSWORD)[1] == "email"


@pytest.mark.parametrize("password", ["short", "x" * (store.LONGEST_PASSWORD + 1)])
def test_a_password_too_short_or_too_long_is_refused(password):
    assert store.create(EMAIL, password)[1] == "password"


def test_the_password_is_never_stored(database):
    store.create(EMAIL, PASSWORD)
    rows = sqlite3.connect(database).execute("select * from account").fetchall()
    assert PASSWORD not in repr(rows)


def test_two_accounts_with_one_password_get_two_hashes():
    assert store.hash_password(PASSWORD) != store.hash_password(PASSWORD)


def test_a_wrong_password_does_not_sign_in():
    store.create(EMAIL, PASSWORD)
    assert store.authenticate(EMAIL, "wrong password") is None


def test_an_unknown_email_does_not_sign_in():
    assert store.authenticate("nobody@example.com", PASSWORD) is None


def test_an_account_is_found_by_its_id():
    account = store.create(EMAIL, PASSWORD)[0]
    assert store.find(account.id).email == EMAIL


def test_a_password_is_changed_with_the_current_one():
    account = store.create(EMAIL, PASSWORD)[0]
    store.change_password(account.id, PASSWORD, "a new long password")
    assert store.authenticate(EMAIL, "a new long password") is not None


def test_a_password_is_not_changed_without_the_current_one():
    account = store.create(EMAIL, PASSWORD)[0]
    assert store.change_password(account.id, "not it at all", "a new long password") == "current"


def test_a_new_password_too_short_is_refused():
    account = store.create(EMAIL, PASSWORD)[0]
    assert store.change_password(account.id, PASSWORD, "short") == "password"
