"""What the overview shows, as text: the view only lays it out."""

from urllib.parse import urlencode

from src.apps.format import change, exact, money, span
from src.apps.orders.metrics_service import MetricsService, Share, Totals
from src.apps.orders.order_model import CHANNELS
from src.apps.orders.window import PERIODS, Window


def link(days: int, channel: str) -> str:
    query = {"days": days, "channel": channel} if channel else {"days": days}
    return "/?" + urlencode(query)


def tile(label: str, now: int, before: int, shown: str) -> dict:
    text, trend = change(now, before)
    return {"label": label, "value": shown, "change": text, "trend": trend}


def tiles(now: Totals, before: Totals) -> list[dict]:
    return [
        tile("Revenue", now.revenue_cents, before.revenue_cents, money(now.revenue_cents)),
        tile("Orders", now.orders, before.orders, f"{now.orders:,}"),
        tile("Average order", now.average_cents, before.average_cents, exact(now.average_cents)),
        tile("Units sold", now.units, before.units, f"{now.units:,}"),
    ]


def shares(rows: list[Share], chosen: str = "") -> list[dict]:
    """Each row with its part of the whole, and its bar as a percent of the largest one."""
    whole = sum(row.revenue_cents for row in rows) or 1
    largest = max((row.revenue_cents for row in rows), default=0) or 1
    return [
        {
            "name": row.name,
            "revenue": money(row.revenue_cents),
            "units": f"{row.units:,}",
            "share": f"{row.revenue_cents / whole:.0%}",
            "width": round(row.revenue_cents / largest * 100),
            "chosen": row.name == chosen,
        }
        for row in rows
    ]


def filters(window: Window) -> dict:
    return {
        "period_links": [
            {
                "label": f"{days} days",
                "href": link(days, window.channel),
                "current": days == window.days,
            }
            for days in PERIODS
        ],
        "channel_links": [
            {
                "label": name or "All channels",
                "href": link(window.days, name),
                "current": name == window.channel,
            }
            for name in ("", *CHANNELS)
        ],
    }


def overview(metrics: MetricsService, window: Window) -> dict:
    return {
        "days": window.days,
        "channel": window.channel,
        "range": span(window.first, window.last),
        "tiles": tiles(metrics.totals(window), metrics.totals(window.before())),
        "channels": shares(metrics.channels(window), window.channel),
        "products": shares(metrics.products(window)),
        **filters(window),
    }
