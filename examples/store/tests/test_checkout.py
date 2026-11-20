from src.store.cart import summary
from src.store.checkout import place, problems, receipt

FORM = {
    "name": "Ada",
    "email": "ada@example.com",
    "address": "12 Harbour Road",
    "city": "Lisbon",
    "postal_code": "1100-001",
}


def test_a_complete_form_has_no_problem():
    assert problems(FORM) == {}


def test_an_empty_field_is_asked_for():
    assert problems({**FORM, "city": "  "}) == {"city": "Fill this in."}


def test_an_email_without_a_domain_is_refused():
    assert "email" in problems({**FORM, "email": "ada@nowhere"})


def test_a_very_long_field_is_refused():
    assert problems({**FORM, "address": "x" * 201}) == {
        "address": "Keep each field under 200 characters."
    }


def test_a_placed_order_can_be_read_back():
    number = place(FORM, summary({"ceramic-mug": 2}))
    assert receipt(number)[0].name == "Ada"


def test_an_order_keeps_its_lines():
    number = place(FORM, summary({"ceramic-mug": 2, "pencil-set": 1}))
    assert [(line.slug, line.quantity) for line in receipt(number)[1]] == [
        ("ceramic-mug", 2),
        ("pencil-set", 1),
    ]


def test_an_order_keeps_the_price_it_was_bought_at():
    number = place(FORM, summary({"ceramic-mug": 1}))
    assert receipt(number)[1][0].price_cents == 1800


def test_an_unknown_order_is_none():
    assert receipt("FS-NOPE") is None
