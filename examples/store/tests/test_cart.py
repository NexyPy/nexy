from src.services.cart_service import CartService, shipping_for


def held(cart="mine"):
    return {line.product.slug: line.quantity for line in CartService.lines(cart)}


def test_a_new_cart_is_empty():
    assert CartService.lines("mine") == []


def test_adding_a_product_puts_one_in_the_cart():
    CartService.add("mine", "ceramic-mug")
    assert held() == {"ceramic-mug": 1}


def test_adding_it_again_adds_to_its_line():
    CartService.add("mine", "ceramic-mug")
    CartService.add("mine", "ceramic-mug", 2)
    assert held() == {"ceramic-mug": 3}


def test_lines_keep_the_order_they_were_added_in():
    CartService.add("mine", "pencil-set")
    CartService.add("mine", "ceramic-mug")
    assert list(held()) == ["pencil-set", "ceramic-mug"]


def test_a_quantity_replaces_the_one_held():
    CartService.add("mine", "ceramic-mug", 4)
    CartService.put("mine", "ceramic-mug", 2)
    assert held() == {"ceramic-mug": 2}


def test_a_quantity_of_zero_takes_the_product_out():
    CartService.add("mine", "ceramic-mug")
    CartService.put("mine", "ceramic-mug", 0)
    assert held() == {}


def test_a_negative_quantity_takes_the_product_out():
    CartService.add("mine", "ceramic-mug")
    CartService.put("mine", "ceramic-mug", -3)
    assert held() == {}


def test_a_cart_never_holds_more_than_the_shelves():
    CartService.add("mine", "field-bag", 5)
    assert held() == {"field-bag": 3}


def test_holding_the_whole_stock_says_so():
    note = CartService.add("mine", "field-bag", 5)
    assert note == "Only 3 left of Field bag: your cart holds them all."


def test_a_quantity_the_shelves_have_says_nothing():
    assert CartService.add("mine", "field-bag", 3) == ""


def test_a_sold_out_product_stays_out_of_the_cart():
    CartService.add("mine", "wool-beanie")
    assert held() == {}


def test_a_sold_out_product_says_so():
    assert CartService.add("mine", "wool-beanie") == "Wool beanie is sold out."


def test_a_product_the_shop_does_not_sell_is_refused():
    assert CartService.add("mine", "nowhere") == "This product is not sold here."


def test_two_carts_do_not_share_their_lines():
    CartService.add("theirs", "ceramic-mug")
    assert held("mine") == {}


def test_delivery_is_free_from_fifty_dollars():
    assert shipping_for(5000) == 0


def test_delivery_costs_five_dollars_below():
    assert shipping_for(4999) == 500


def test_an_empty_cart_pays_no_delivery():
    assert shipping_for(0) == 0
