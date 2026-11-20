from src.apps.orders.metrics_service import Share
from src.apps.overview.overview_page import shares


def test_a_share_is_its_part_of_the_whole():
    rows = shares([Share("Online", 300, 1), Share("Cafe", 100, 1)])
    assert rows[1]["share"] == "25%"


def test_the_largest_share_fills_its_bar():
    rows = shares([Share("Online", 300, 1), Share("Cafe", 100, 1)])
    assert rows[0]["width"] == 100


def test_shares_of_nothing_have_empty_bars():
    assert shares([Share("Online", 0, 0)])[0]["width"] == 0


def test_the_chosen_channel_is_marked():
    assert shares([Share("Cafe", 1, 1)], chosen="Cafe")[0]["chosen"] is True
