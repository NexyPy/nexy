import pytest

ADA = {
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "address": "12 St James's Square",
    "city": "London",
    "postcode": "SW1Y 4JH",
}


@pytest.fixture
def filled(call):
    call("add_to_cart", slug="dot-notebook", quantity=2)


def errors(call, **changed):
    return call("place_order", **{**ADA, **changed}).json()["errors"]


@pytest.mark.usefixtures("filled")
class TestTheCheckout:
    def test_places_the_order(self, call):
        assert call("place_order", **ADA).json() == {"number": 1001, "errors": {}}

    def test_names_a_field_left_empty(self, call):
        assert errors(call, name="  ") == {"name": "Write the name the parcel goes to."}

    def test_refuses_an_email_without_a_domain(self, call):
        assert errors(call, email="ada@") == {
            "email": "Write an email address, such as ada@example.com."
        }

    def test_refuses_a_postal_code_too_long(self, call):
        assert errors(call, postcode="1" * 13) == {"postcode": "Keep it under 12 characters."}

    def test_names_every_field_to_fix_at_once(self, call):
        assert set(errors(call, city="", postcode="")) == {"city", "postcode"}

    def test_an_order_lists_its_lines(self, call):
        call("place_order", **ADA)
        lines = call("order", number=1001).json()["lines"]
        assert [(line["slug"], line["quantity"]) for line in lines] == [("dot-notebook", 2)]

    def test_the_orders_of_the_browser_are_listed(self, call):
        call("place_order", **ADA)
        assert [order["number"] for order in call("orders").json()] == [1001]

    def test_another_browser_cannot_read_the_order(self, call, app):
        from fastapi.testclient import TestClient

        call("place_order", **ADA)
        with TestClient(app) as other:
            assert call("order", client=other, number=1001).status_code == 404


def test_an_empty_cart_is_refused(call):
    assert errors(call) == {"cart": "Your cart is empty."}


def test_a_browser_that_placed_nothing_has_no_orders(call):
    assert call("orders").json() == []


@pytest.mark.usefixtures("filled")
def test_an_order_says_it_was_placed_in_utc(call):
    call("place_order", **ADA)
    assert call("order", number=1001).json()["placed_at"].endswith("Z")
