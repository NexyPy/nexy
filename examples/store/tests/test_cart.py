from src.store.cart import FREE_SHIPPING, MAX_QUANTITY, SHIPPING, add, put, summary


def test_adding_a_product_puts_one_in_the_cart():
    assert add({}, "ceramic-mug") == {"ceramic-mug": 1}


def test_adding_again_adds_to_the_quantity():
    assert add({"ceramic-mug": 1}, "ceramic-mug", 2) == {"ceramic-mug": 3}


def test_an_unknown_product_is_not_added():
    assert add({}, "nope") == {}


def test_a_quantity_stops_at_the_maximum():
    assert add({}, "ceramic-mug", 99) == {"ceramic-mug": MAX_QUANTITY}


def test_a_quantity_of_zero_removes_the_product():
    assert put({"ceramic-mug": 2}, "ceramic-mug", 0) == {}


def test_a_negative_addition_changes_nothing():
    assert add({"ceramic-mug": 2}, "ceramic-mug", -5) == {"ceramic-mug": 2}


def test_a_cart_counts_every_item():
    assert summary({"ceramic-mug": 2, "pencil-set": 1}).count == 3


def test_a_product_gone_from_the_catalog_is_left_out():
    assert summary({"retired-thing": 1}).lines == []


def test_a_small_order_pays_shipping():
    assert summary({"pencil-set": 1}).shipping == SHIPPING


def test_shipping_is_free_from_the_threshold():
    big = summary({"field-bag": 1})
    assert (big.subtotal >= FREE_SHIPPING, big.shipping) == (True, 0)


def test_an_empty_cart_costs_nothing():
    assert summary({}).total == 0


def test_the_total_is_the_subtotal_and_shipping():
    assert summary({"pencil-set": 2}).total == 2 * 900 + SHIPPING
