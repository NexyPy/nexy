from nexy.decorators import Controller
from nexy.hooks import useViews

from src.apps.orders.order_service import OrderService
from src.apps.orders.orders_page import orders_page

LAYOUT = "src/apps/layout.nexy"
VIEW = "src/apps/orders/orders_view.nexy"


@Controller("/orders")
class OrdersController:
    """Every order, newest first: `?channel=` keeps one channel, `?page=` turns the pages."""

    def __init__(self, orders: OrderService) -> None:
        self.orders = orders

    def get(self, channel: str = "", page: str = "1"):
        # Six ASCII digits at most: int() refuses "\u00b2", and a longer number is past the last page.
        number = int(page) if page.isascii() and page.isdigit() and len(page) <= 6 else 1
        shown = orders_page(self.orders.page(channel, number), channel)
        view = useViews(VIEW, context={"page": shown})
        return useViews(LAYOUT, context={"children": view, "title": "Orders"})
