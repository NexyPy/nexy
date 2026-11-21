"""The form without JavaScript: the browser posts it to /waitlist and goes back to the form."""

FORM = {"content-type": "application/x-www-form-urlencoded"}


def test_the_form_puts_an_email_on_the_list(client, emails):
    client.post("/waitlist", content="email=Ada%40Example.com", headers=FORM)
    assert emails() == ["ada@example.com"]


def test_the_form_goes_back_to_the_form_with_its_outcome(client):
    answer = client.post("/waitlist", content="email=ada%40example.com", headers=FORM)
    assert answer.headers["location"] == "/?waitlist=joined#join"


def test_the_form_answers_with_a_see_other(client):
    assert (
        client.post("/waitlist", content="email=ada%40example.com", headers=FORM).status_code == 303
    )


def test_a_form_without_email_asks_for_one(client):
    answer = client.post("/waitlist", content="", headers=FORM)
    assert answer.headers["location"] == "/?waitlist=empty#join"


def test_a_body_longer_than_the_form_is_cut_not_stored(client, emails):
    client.post("/waitlist", content="email=" + "a" * 100_000 + "%40example.com", headers=FORM)
    assert emails() == []
