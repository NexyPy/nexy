import re

import pytest

from src.accounts import store, throttle

EMAIL = "ada@example.com"
PASSWORD = "correct horse battery"


def forms(client, page):
    """The addresses the forms of `page` post to, in the order of the page."""
    return re.findall(r'<form method="post" action="([^"]+)"', client.get(page).text)


def sign_up(client, email=EMAIL, password=PASSWORD, then=""):
    data = {"email": email, "password": password, "then": then}
    return client.post(forms(client, "/signup")[0], data=data)


def sign_in(client, email=EMAIL, password=PASSWORD, then=""):
    data = {"email": email, "password": password, "then": then}
    return client.post(forms(client, "/signin")[0], data=data)


@pytest.fixture
def signed_in(client):
    sign_up(client)
    return client


def test_the_account_page_sends_a_visitor_to_sign_in(client):
    assert client.get("/account").headers["location"] == "/signin?error=signin&then=/account"


def test_the_sign_in_page_says_why_it_was_opened(client):
    assert "Sign in to see your account." in client.get("/signin?error=signin&then=/account").text


def test_signing_up_lands_on_the_account(client):
    assert sign_up(client).headers["location"] == "/account"


def test_a_new_account_sees_its_email(signed_in):
    assert EMAIL in signed_in.get("/account").text


def test_signing_up_twice_says_the_email_is_taken(client):
    store.create(EMAIL, PASSWORD)
    location = sign_up(client).headers["location"]
    assert "already has an account" in client.get(location).text


def test_a_refused_sign_up_keeps_the_email(client):
    location = sign_up(client, password="short").headers["location"]
    assert f'value="{EMAIL}"' in client.get(location).text


def test_signing_in_goes_back_where_it_was_asked(client):
    store.create(EMAIL, PASSWORD)
    assert sign_in(client, then="/account").headers["location"] == "/account"


def test_a_wrong_password_says_wrong_email_or_password(client):
    store.create(EMAIL, PASSWORD)
    location = sign_in(client, password="not the password").headers["location"]
    assert "Wrong email or password." in client.get(location).text


def test_an_unknown_email_says_the_same_as_a_wrong_password(client):
    location = sign_in(client, email="nobody@example.com").headers["location"]
    assert "Wrong email or password." in client.get(location).text


def test_too_many_wrong_passwords_stop_even_the_right_one(client):
    store.create(EMAIL, PASSWORD)
    for _ in range(throttle.LIMIT):
        sign_in(client, password="not the password")
    assert "error=slow" in sign_in(client).headers["location"]


@pytest.mark.parametrize(
    "then", ["https://evil.example", "//evil.example", "/\\evil.example", "javascript:alert(1)"]
)
def test_signing_in_never_goes_to_another_site(client, then):
    store.create(EMAIL, PASSWORD)
    assert sign_in(client, then=then).headers["location"] == "/account"


def test_a_signed_in_visitor_skips_the_sign_in_page(signed_in):
    assert signed_in.get("/signin").headers["location"] == "/account"


def test_signing_out_ends_the_session(signed_in):
    signed_in.post(forms(signed_in, "/account")[1])
    assert signed_in.get("/account").status_code == 307


def test_signing_out_says_so(signed_in):
    location = signed_in.post(forms(signed_in, "/account")[1]).headers["location"]
    assert "You are signed out." in signed_in.get(location).text


def test_the_password_is_changed_from_the_account(signed_in):
    data = {"current_password": PASSWORD, "new_password": "a brand new password"}
    signed_in.post(forms(signed_in, "/account")[0], data=data)
    assert store.authenticate(EMAIL, "a brand new password") is not None


def test_a_wrong_current_password_changes_nothing(signed_in):
    data = {"current_password": "not it at all", "new_password": "a brand new password"}
    location = signed_in.post(forms(signed_in, "/account")[0], data=data).headers["location"]
    assert "The current password is not right." in signed_in.get(location).text


def test_a_session_cookie_signed_with_another_key_signs_no_one_in(client):
    client.cookies.set("session", "eyJhY2NvdW50X2lkIjogMX0=.forged.signature")
    assert client.get("/account").status_code == 307


def test_an_error_key_that_does_not_exist_shows_nothing(client):
    assert "made-up" not in client.get("/signin?error=<b>made-up</b>").text


def test_an_email_in_the_address_is_printed_as_text(client):
    assert '"><script>' not in client.get('/signin?email="><script>alert(1)</script>').text


def test_an_unknown_page_answers_404(client):
    assert client.get("/nothing-here").status_code == 404
