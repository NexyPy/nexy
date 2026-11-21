"""The form with JavaScript: the island calls the `join_waitlist` action."""


def test_the_action_puts_an_email_on_the_list(call, emails):
    call("join_waitlist", email="ada@example.com")
    assert emails() == ["ada@example.com"]


def test_the_action_says_the_email_joined(call):
    assert call("join_waitlist", email="ada@example.com").json()["joined"] is True


def test_the_action_says_what_is_wrong(call):
    answer = call("join_waitlist", email="ada").json()
    assert answer == {
        "joined": False,
        "message": "That does not look like an email. Check it and try again.",
    }


def test_a_huge_email_is_refused_not_a_crash(call):
    assert call("join_waitlist", email="a" * 5000).json()["joined"] is False


def test_an_email_that_is_not_text_is_a_bad_request(call):
    assert call("join_waitlist", email=["ada@example.com"]).status_code == 422
