"""The status card of the hero is made up, but it must still add up."""

from src.content.preview import DAYS, Monitor, average, monitors, sparkline


def test_each_monitor_shows_45_days():
    assert {len(monitor.days) for monitor in monitors()} == {DAYS}


def test_today_is_the_last_day():
    api = next(monitor for monitor in monitors() if monitor.name == "API")
    assert api.days[-1 - 12] == "down"


def test_a_monitor_always_up_shows_100_percent():
    assert Monitor("Site", "site.example", ("up",) * 10).uptime == "100.00%"


def test_a_down_day_lowers_the_uptime():
    assert Monitor("Site", "site.example", ("up",) * 9 + ("down",)).uptime == "99.85%"


def test_a_slow_day_keeps_the_uptime():
    assert Monitor("Site", "site.example", ("up",) * 9 + ("slow",)).uptime == "100.00%"


def test_the_sparkline_starts_at_the_left():
    assert sparkline([1, 2, 3], width=10, height=10).startswith("M0.0 ")


def test_the_sparkline_puts_the_highest_value_at_the_top():
    assert sparkline([1, 3], width=10, height=10) == "M0.0 10.0 L10.0 0.0"


def test_a_flat_sparkline_does_not_divide_by_zero():
    assert sparkline([5, 5], width=10, height=10) == "M0.0 10.0 L10.0 10.0"


def test_the_average_response_time_is_rounded():
    assert average([1, 2, 2]) == 2
