"""`/rss`: an RSS 2.0 feed of every post, for feed readers."""

from xml.sax.saxutils import escape

from nexyconfig import NexyConfig

from nexy.http import Response
from src.blog.posts import Post, all_posts

SITE = NexyConfig.useSiteUrl  # one address for the feed and the sitemap, set in nexyconfig.py
TITLE = "Notes, a Nexy example blog"


def _item(post: Post) -> str:
    link = f"{SITE}/posts/{post.slug}"
    return (
        f"<item><title>{escape(post.title)}</title><link>{link}</link><guid>{link}</guid>"
        f"<pubDate>{post.date.strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate>"
        f"<description>{escape(post.summary)}</description></item>"
    )


def feed() -> str:
    items = "".join(_item(post) for post in all_posts())
    return (
        '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
        f"<title>{escape(TITLE)}</title><link>{SITE}</link>"
        f"<description>Markdown files rendered by Python on the server.</description>{items}"
        "</channel></rss>"
    )


async def GET() -> Response:  # noqa: N802 - Nexy routes a handler by its HTTP method
    return Response(feed(), media_type="application/rss+xml")
