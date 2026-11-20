"""What the list of orders shows, as text: the view only lays it out."""

from urllib.parse import urlencode

from src.apps.format import day, exact
from src.apps.orders.order_model import CHANNELS
from src.apps.orders.order_service import Page


def link(channel: str, number: int = 1) -> str:
    query = {"channel": channel} if channel else {}
    if number > 1:
        query["page"] = str(number)
    return "/orders/" + ("?" + urlencode(query) if query else "")


def rows(page: Page) -> list[dict]:
    return [
        {
            "number": f"#{row.id:05d}",
            "day": day(row.placed_on),
            "channel": row.channel,
            "region": row.region,
            "product": row.product,
            "units": row.units,
            "revenue": exact(row.revenue_cents),
        }
        for row in page.rows
    ]


def orders_page(page: Page, channel: str) -> dict:
    channel = channel if channel in CHANNELS else ""
    return {
        "rows": rows(page),
        "total": f"{page.total:,}",
        "number": page.number,
        "pages": page.pages,
        "previous": link(channel, page.number - 1) if page.number > 1 else "",
        "next": link(channel, page.number + 1) if page.number < page.pages else "",
        "channel_links": [
            {"label": name or "All channels", "href": link(name), "current": name == channel}
            for name in ("", *CHANNELS)
        ],
    }
