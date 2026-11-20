from nexy.decorators import Container

from src.apps.orders.order_service import PAGE_SIZE, OrderService


def orders() -> OrderService:
    return Container.resolve(OrderService)


def test_a_page_holds_20_orders():
    assert len(orders().page().rows) == PAGE_SIZE


def test_the_newest_order_comes_first(order):
    order("2026-11-01", product="Decaf 250g")
    order("2026-11-15", product="Gift box")
    assert orders().page().rows[0].product == "Gift box"


def test_a_channel_keeps_only_its_orders():
    assert {row.channel for row in orders().page("Wholesale").rows} == {"Wholesale"}


def test_an_unknown_channel_shows_every_order():
    assert orders().page("nowhere").total == orders().page().total


def test_a_page_past_the_last_gives_the_last(order):
    order("2026-11-15")
    assert orders().page(number=9).number == 1


def test_a_page_before_the_first_gives_the_first():
    assert orders().page(number=-3).number == 1


def test_no_order_still_makes_one_page(empty):
    assert orders().page().pages == 1
