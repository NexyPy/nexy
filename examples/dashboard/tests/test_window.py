from datetime import date

from src.apps.orders.window import Window, window_of

LAST = date(2026, 11, 15)


def test_a_window_of_7_days_starts_6_days_before_its_last():
    assert Window(7, "", LAST).first == date(2026, 11, 9)


def test_the_window_before_ends_the_day_before_the_first():
    assert Window(7, "", LAST).before().last == date(2026, 11, 8)


def test_a_period_the_page_offers_is_kept():
    assert window_of("90", "", LAST).days == 90


def test_a_period_the_page_does_not_offer_falls_back_to_30_days():
    assert window_of("365", "", LAST).days == 30


def test_a_period_that_is_not_a_number_falls_back_to_30_days():
    assert window_of("-7", "", LAST).days == 30


def test_a_known_channel_is_kept():
    assert window_of("30", "Cafe", LAST).channel == "Cafe"


def test_an_unknown_channel_means_every_channel():
    assert window_of("30", "' OR 1=1 --", LAST).channel == ""
