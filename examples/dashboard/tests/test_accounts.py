from src.services.accounts import authenticate
from src.services.demo import DEMO_EMAIL, DEMO_PASSWORD
from src.services.passwords import hash_password, password_matches


def test_the_demo_user_signs_in():
    assert authenticate(DEMO_EMAIL, DEMO_PASSWORD).email == DEMO_EMAIL


def test_the_email_is_read_without_case_or_spaces():
    assert authenticate(" Demo@Example.com ", DEMO_PASSWORD) is not None


def test_a_wrong_password_signs_nobody_in():
    assert authenticate(DEMO_EMAIL, "nope") is None


def test_an_unknown_email_signs_nobody_in():
    assert authenticate("nobody@example.com", DEMO_PASSWORD) is None


def test_the_hash_is_not_the_password():
    assert "secret-words" not in hash_password("secret-words")


def test_a_hash_matches_its_password():
    assert password_matches("secret-words", hash_password("secret-words"))


def test_the_same_password_hashes_twice_differently():
    assert hash_password("secret-words") != hash_password("secret-words")
