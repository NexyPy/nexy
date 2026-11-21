"""The days a page looks at: the last 7, 30 or 90 days of the data, and the same length before."""

from dataclasses import dataclass
from datetime import date, timedelta

from src.models.order_model import CHANNELS

PERIODS = (7, 30, 90)
DEFAULT_PERIOD = 30


@dataclass(frozen=True)
class Window:
    days: int
    channel: str  # one of CHANNELS, or "" for all of them
    last: date

    @property
    def first(self) -> date:
        return self.last - timedelta(days=self.days - 1)

    def before(self) -> "Window":
        """The same number of days, just before this window: what a change is measured against."""
        return Window(self.days, self.channel, self.first - timedelta(days=1))


def window_of(days: str, channel: str, last: date) -> Window:
    """A window from the query string. A value the page does not offer falls back to its default."""
    # Compared as text: int() would refuse a digit such as "\u00b2" and a number 5000 digits long.
    period = int(days) if days in {str(offered) for offered in PERIODS} else DEFAULT_PERIOD
    return Window(period, channel if channel in CHANNELS else "", last)
