"""`/rss`: the posts as an RSS 2.0 feed, newest first, for feed readers."""

from datetime import UTC, datetime, time
from email.utils import format_datetime
from xml.sax.saxutils import escape

from nexy.http import Response

from nexyconfig import NexyConfig
from src.blog.posts import Post, all_posts

TITLE = "Plain Text"
DESCRIPTION = "Notes on building for the web with Python, written in Markdown."


def site() -> str:
    """The address the blog is published at: feed readers need absolute links."""
    return (NexyConfig.useSiteUrl or "http://localhost:3000").rstrip("/")


def _item(post: Post, origin: str) -> str:
    link = escape(f"{origin}/posts/{post.slug}")
    published = format_datetime(datetime.combine(post.date, time(), UTC))
    return (
        f"<item><title>{escape(post.title)}</title><link>{link}</link>"
        f'<guid isPermaLink="true">{link}</guid><pubDate>{published}</pubDate>'
        f"<description>{escape(post.summary)}</description></item>"
    )


def feed() -> str:
    """The channel of the blog, then one item per post."""
    origin = site()
    items = "".join(_item(post, origin) for post in all_posts())
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
        f"<title>{TITLE}</title><link>{origin}</link><description>{DESCRIPTION}</description>"
        f'<language>en</language><atom:link href="{origin}/rss" rel="self" '
        f'type="application/rss+xml"/>{items}</channel></rss>\n'
    )


async def GET() -> Response:
    return Response(feed(), media_type="application/rss+xml")
