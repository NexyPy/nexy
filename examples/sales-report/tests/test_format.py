from datetime import date

from src.apps.format import change, day, exact, money, span


def test_money_shows_whole_dollars_with_a_comma():
    assert money(7022850) == "$70,228"


def test_exact_shows_dollars_and_cents():
    assert exact(9132) == "$91.32"


def test_exact_keeps_a_zero_in_the_cents():
    assert exact(105) == "$1.05"


def test_a_rise_is_written_with_a_plus():
    assert change(110, 100) == ("+10.0%", "up")


def test_a_fall_is_written_with_a_minus():
    assert change(90, 100) == ("-10.0%", "down")


def test_the_same_number_is_no_change():
    assert change(100, 100) == ("no change", "flat")


def test_something_from_nothing_is_new():
    assert change(5, 0) == ("new", "up")


def test_nothing_from_nothing_is_no_change():
    assert change(0, 0) == ("no change", "flat")


def test_a_day_is_written_in_words():
    assert day(date(2026, 11, 5)) == "Nov 5, 2026"


def test_a_span_in_one_year_writes_the_year_once():
    assert span(date(2026, 10, 17), date(2026, 11, 15)) == "Oct 17 to Nov 15, 2026"


def test_a_span_across_two_years_writes_both():
    assert span(date(2025, 12, 20), date(2026, 1, 3)) == "Dec 20, 2025 to Jan 3, 2026"
