from nexy.decorators import Controller

from src.apps.orders.metrics_service import MetricsService
from src.apps.orders.window import window_of


@Controller("/api/revenue")
class RevenueController:
    """The revenue and the orders of each day, as JSON, for the chart of the overview."""

    def __init__(self, metrics: MetricsService) -> None:
        self.metrics = metrics

    def get(self, days: str = "30", channel: str = "") -> dict:
        window = window_of(days, channel, self.metrics.as_of())
        series = self.metrics.daily(window)
        return {
            "days": window.days,
            "channel": window.channel,
            "series": [
                {
                    "day": point.day.isoformat(),
                    "revenue_cents": point.revenue_cents,
                    "orders": point.orders,
                }
                for point in series
            ],
        }
