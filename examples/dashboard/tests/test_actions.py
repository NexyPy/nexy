"""The actions, called the way the pages call them: a POST of JSON."""

import pytest

from src.actions.dashboard import page_number


def test_the_overview_covers_30_days_by_default(call):
    assert len(call("overview").json()["daily"]) == 30


def test_the_overview_keeps_a_period_it_offers(call):
    assert call("overview", days="7").json()["period"]["days"] == 7


def test_the_overview_ends_on_the_last_day_with_orders(call):
    assert call("overview").json()["period"]["last"] == "2026-11-15"


def test_the_overview_compares_with_the_days_before(call, order):
    order("2026-11-15")
    order("2026-11-05", revenue_cents=4200)
    assert call("overview", days="7").json()["before"]["revenue_cents"] == 4200


def test_the_overview_of_a_channel_counts_only_its_orders(call):
    every = call("overview").json()["totals"]["orders"]
    assert call("overview", channel="Cafe").json()["totals"]["orders"] < every


def test_the_overview_lists_the_three_channels(call):
    names = [share["name"] for share in call("overview").json()["channels"]]
    assert names == ["Online", "Wholesale", "Cafe"]


def test_the_overview_lists_five_best_sellers(call):
    assert len(call("overview").json()["best"]) == 5


def test_the_products_list_more_than_the_five_best(call):
    assert len(call("products").json()["products"]) > 5


def test_the_products_put_the_best_seller_first(call):
    found = call("products").json()["products"]
    assert found[0]["revenue_cents"] == max(share["revenue_cents"] for share in found)


def test_the_orders_come_20_to_a_page(call):
    assert len(call("orders").json()["rows"]) == 20


def test_the_orders_of_a_channel_name_it(call):
    assert call("orders", channel="Wholesale").json()["channel"] == "Wholesale"


def test_an_unknown_channel_gives_every_order(call):
    assert call("orders", channel="nowhere").json()["channel"] == ""


def test_a_page_past_the_last_gives_the_last(call):
    body = call("orders", page="999999").json()
    assert body["number"] == body["pages"]


@pytest.mark.parametrize("hostile", ["²", "1" * 5000, "-3", " 2", "", "<b>"])
def test_a_page_that_is_not_a_plain_number_is_the_first(hostile):
    assert page_number(hostile) == 1


@pytest.mark.parametrize("hostile", ["²", "9" * 5000, "-7", "7.0", "<script>"])
def test_a_period_the_page_does_not_offer_falls_back_to_30_days(call, hostile):
    assert call("overview", days=hostile).json()["period"]["days"] == 30


def test_a_period_sent_as_a_huge_json_number_is_refused_not_a_crash(app):
    from fastapi.testclient import TestClient
    from nexy.decorators import ACTIONS_STORE

    path = ACTIONS_STORE.template_context()["__actions_path"]["overview"]
    with TestClient(app, raise_server_exceptions=False) as client:
        answer = client.post(
            path,
            content='{"days": ' + "9" * 5000 + "}",
            headers={"content-type": "application/json"},
        )
    assert answer.status_code < 500
