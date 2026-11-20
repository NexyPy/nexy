from datetime import date

from nexy.decorators import Container

from src.apps.orders.metrics_service import MetricsService
from src.apps.orders.window import Window

LAST = date(2026, 11, 15)


def metrics() -> MetricsService:
    return Container.resolve(MetricsService)


def test_the_data_ends_on_the_last_day_of_the_migration():
    assert metrics().as_of() == LAST


def test_the_migration_records_orders_on_every_one_of_120_days():
    days = metrics().daily(Window(120, "", LAST))
    assert all(day.orders for day in days)


def test_without_orders_the_last_day_is_today(empty):
    assert metrics().as_of() == date.today()


def test_totals_add_the_revenue_of_the_window(order):
    order("2026-11-15", revenue_cents=1500)
    order("2026-11-14", revenue_cents=3000)
    order("2026-11-01", revenue_cents=9900)
    assert metrics().totals(Window(7, "", LAST)).revenue_cents == 4500


def test_totals_keep_to_the_chosen_channel(order):
    order("2026-11-15", channel="Online")
    order("2026-11-15", channel="Cafe")
    assert metrics().totals(Window(7, "Cafe", LAST)).orders == 1


def test_the_average_order_is_the_revenue_over_the_orders(order):
    order("2026-11-15", revenue_cents=1000)
    order("2026-11-15", revenue_cents=2000)
    assert metrics().totals(Window(7, "", LAST)).average_cents == 1500


def test_a_window_with_no_order_has_an_average_of_zero(empty):
    assert metrics().totals(Window(7, "", LAST)).average_cents == 0


def test_daily_gives_one_value_per_day(empty):
    assert len(metrics().daily(Window(30, "", LAST))) == 30


def test_a_day_with_no_order_counts_zero(order):
    order("2026-11-15")
    assert metrics().daily(Window(7, "", LAST))[0].orders == 0


def test_a_day_adds_its_orders(order):
    order("2026-11-15", revenue_cents=1000)
    order("2026-11-15", revenue_cents=500)
    assert metrics().daily(Window(7, "", LAST))[-1].revenue_cents == 1500


def test_channels_list_every_channel_even_without_orders(order):
    order("2026-11-15", channel="Online")
    assert [share.name for share in metrics().channels(Window(7, "", LAST))] == [
        "Online",
        "Wholesale",
        "Cafe",
    ]


def test_channels_ignore_the_chosen_channel(order):
    order("2026-11-15", channel="Online", revenue_cents=700)
    shares = metrics().channels(Window(7, "Cafe", LAST))
    assert shares[0].revenue_cents == 700


def test_products_come_best_seller_first(order):
    order("2026-11-15", product="Decaf 250g", revenue_cents=1500)
    order("2026-11-15", product="Gift box", revenue_cents=5500)
    assert metrics().products(Window(7, "", LAST))[0].name == "Gift box"


def test_products_stop_at_the_limit(empty):
    assert len(metrics().products(Window(120, "", LAST), limit=3)) <= 3
