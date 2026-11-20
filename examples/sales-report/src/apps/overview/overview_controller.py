from nexy.decorators import Controller
from nexy.hooks import useViews

from src.apps.orders.metrics_service import MetricsService
from src.apps.orders.window import window_of
from src.apps.overview.overview_page import overview

LAYOUT = "src/apps/layout.nexy"
VIEW = "src/apps/overview/overview_view.nexy"


@Controller()
class OverviewController:
    """The overview: `?days=7|30|90` and `?channel=` choose what it adds up."""

    def __init__(self, metrics: MetricsService) -> None:
        self.metrics = metrics

    def get(self, days: str = "30", channel: str = ""):
        window = window_of(days, channel, self.metrics.as_of())
        page = useViews(VIEW, context={"page": overview(self.metrics, window)})
        return useViews(LAYOUT, context={"children": page, "title": "Overview"})
