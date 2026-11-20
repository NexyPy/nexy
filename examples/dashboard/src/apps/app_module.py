from nexy.decorators import Module

from src.apps.api.revenue_controller import RevenueController
from src.apps.orders.metrics_service import MetricsService
from src.apps.orders.order_service import OrderService
from src.apps.orders.orders_controller import OrdersController
from src.apps.overview.overview_controller import OverviewController


@Module()
class AppModule:
    controllers = [OverviewController, OrdersController, RevenueController]
    providers = [MetricsService, OrderService]
