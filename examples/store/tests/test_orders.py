import pytest

from src.services.cart_service import CartService
from src.services.catalog_service import CatalogService
from src.services.order_service import Delivery, OrderService

ADA = Delivery("Ada Lovelace", "ada@example.com", "12 St James's Square", "London", "SW1Y 4JH")


@pytest.fixture
def placed():
    CartService.add("mine", "ceramic-mug", 2)
    CartService.add("mine", "field-bag")
    return OrderService.place("mine", ADA)


def test_an_order_takes_the_lines_of_the_cart(placed):
    assert [(line.slug, line.quantity) for line in placed.lines] == [
        ("ceramic-mug", 2),
        ("field-bag", 1),
    ]


def test_the_first_order_is_number_1001(placed):
    assert placed.number == 1001


def test_an_order_adds_up_its_lines(placed):
    assert placed.subtotal_cents == 2 * 1800 + 6400


def test_an_order_of_fifty_dollars_ships_free(placed):
    assert placed.total_cents == placed.subtotal_cents


def test_placing_an_order_empties_the_cart(placed):
    assert CartService.lines("mine") == []


def test_placing_an_order_takes_its_products_off_the_shelves(placed):
    assert CatalogService.find("field-bag").stock == 2


def test_an_order_goes_to_the_address_given(placed):
    assert placed.city == "London"


def test_an_empty_cart_places_no_order():
    assert OrderService.place("mine", ADA) == "Your cart is empty."


def test_a_product_that_ran_out_stops_the_order():
    CartService.add("mine", "field-bag", 3)
    CartService.add("theirs", "field-bag", 3)
    OrderService.place("theirs", ADA)
    assert OrderService.place("mine", ADA) == (
        "Only 0 left of Field bag: change the quantity in your cart."
    )


@pytest.mark.usefixtures("placed")
class TestAPlacedOrder:
    def test_is_found_by_its_number(self):
        assert OrderService.find("mine", 1001).name == "Ada Lovelace"

    def test_is_not_found_by_another_browser(self):
        assert OrderService.find("theirs", 1001) is None

    def test_an_unknown_number_finds_nothing(self):
        assert OrderService.find("mine", 9999) is None

    def test_orders_come_newest_first(self):
        CartService.add("mine", "pencil-set")
        OrderService.place("mine", ADA)
        assert [order.number for order in OrderService.of("mine")] == [1002, 1001]

    def test_keeps_the_price_of_the_day(self):
        from sqlalchemy import update
        from sqlalchemy.orm import Session

        from src.configs.db import engine
        from src.models.product_model import ProductModel

        with Session(engine) as session:
            session.execute(update(ProductModel).values(price_cents=1))
            session.commit()
        assert OrderService.find("mine", 1001).subtotal_cents == 2 * 1800 + 6400


def test_a_product_taken_meanwhile_stops_the_order():
    from src.services import order_service

    CartService.add("mine", "field-bag", 3)
    real = order_service.take
    order_service.take = lambda session, line: False
    try:
        problem = OrderService.place("mine", ADA)
    finally:
        order_service.take = real
    assert problem == "A product of your cart just ran out: look at your cart again."


def test_an_order_that_did_not_go_through_leaves_the_cart_as_it_was():
    from src.services import order_service

    CartService.add("mine", "field-bag", 3)
    real = order_service.take
    order_service.take = lambda session, line: False
    try:
        OrderService.place("mine", ADA)
    finally:
        order_service.take = real
    assert len(CartService.lines("mine")) == 1
