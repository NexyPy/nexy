from src.actions.cart import COOKIE


def test_a_browser_without_a_cart_gets_an_empty_one(call):
    assert call("cart").json()["lines"] == []


def test_reading_the_cart_sets_no_cookie(call):
    assert "set-cookie" not in call("cart").headers


def test_adding_to_the_cart_gives_the_browser_its_cookie(call, browser):
    call("add_to_cart", slug="ceramic-mug")
    assert COOKIE in browser.cookies


def test_the_cookie_is_out_of_reach_of_scripts(call):
    assert "HttpOnly" in call("add_to_cart", slug="ceramic-mug").headers["set-cookie"]


def test_the_cart_follows_the_cookie(call):
    call("add_to_cart", slug="ceramic-mug", quantity=2)
    assert call("cart").json()["count"] == 2


def test_another_browser_has_a_cart_of_its_own(call, app):
    from fastapi.testclient import TestClient

    call("add_to_cart", slug="ceramic-mug")
    with TestClient(app) as other:
        assert call("cart", client=other).json()["count"] == 0


def test_the_cart_adds_delivery_below_fifty_dollars(call):
    assert call("add_to_cart", slug="pencil-set").json()["total_cents"] == 900 + 500


def test_the_cart_ships_free_from_fifty_dollars(call):
    assert call("add_to_cart", slug="field-bag").json()["shipping_cents"] == 0


def test_a_quantity_replaces_the_one_in_the_cart(call):
    call("add_to_cart", slug="ceramic-mug", quantity=3)
    assert call("set_quantity", slug="ceramic-mug", quantity=1).json()["count"] == 1


def test_a_product_can_be_taken_out(call):
    call("add_to_cart", slug="ceramic-mug")
    assert call("remove_from_cart", slug="ceramic-mug").json()["lines"] == []


def test_the_cart_says_why_it_kept_fewer(call):
    note = call("add_to_cart", slug="wool-beanie").json()["note"]
    assert note == "Wool beanie is sold out."
