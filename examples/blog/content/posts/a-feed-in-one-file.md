---
title: An RSS feed in one Python file
date: 2026-10-05
summary: The feed of this blog is one route file that writes XML. Here is what each part of it does.
tags: rss, python
---

Feed readers still are the best way to follow a blog without an account anywhere. This one serves
its feed at [/rss](/rss), from a single file: `src/routes/rss.py`.

## A route that answers XML

A `.py` file in `src/routes/` is a route like a page is, and a function named after an HTTP method
answers it. This one returns a `Response` with the type feed readers expect:

```python
async def GET() -> Response:
    return Response(feed(), media_type="application/rss+xml")
```

## One item per post

`feed()` writes the channel, then one `<item>` per post, newest first: the title, the link, the
date and the summary.

Every piece of text goes through `escape()` from the standard library. A title such as
`Q&A: <html> in posts` would otherwise break the XML, and a feed reader drops a feed it cannot
parse.

## Dates the way RSS wants them

RSS dates follow an old mail format, `Mon, 05 Oct 2026 00:00:00 +0000`. The standard library
writes it too: `email.utils.format_datetime`. There is no date to format by hand.

## Absolute links

A feed reader does not know the address of the blog, so each link is absolute. The origin comes
from `useSiteUrl` in `nexyconfig.py`, the same setting Nexy reads to serve `/sitemap.xml`. Set it
once to the address the blog is published at, and the feed and the sitemap both follow.
