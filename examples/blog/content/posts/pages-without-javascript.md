---
title: Pages that need no JavaScript
date: 2026-09-14
summary: Every page of this blog is HTML from the server. Two small scripts make it nicer, and the text never waits for them.
tags: html, performance
---

Open any post with JavaScript turned off and reload: the text, the table of contents, the tags
and the links between posts are all there. They are HTML, written by Python on the server before
the answer leaves it.

## What the server sends

A request for `/posts/hello-world` runs `src/routes/posts/[slug].nexy`. Its Python finds the post,
its template writes the HTML, and the layout wraps it with the header and the footer. The browser
receives one document it can show at once.

Nothing on the page waits for a script to fetch data. There is no data to fetch: the page is the
data.

## The two scripts

Two scripts ship with the layout, and both are small enough to read in a minute:

1. **The theme.** A few lines in the `<head>` pick light or dark before the first paint. The
   [dark mode post](/posts/dark-mode-without-a-flash) explains them.
2. **The menu.** On a phone, the links of the header move into a sheet that a button opens. The
   script opens it, closes it on Escape, and keeps the focus inside while it is open.

Without them, the page is light and the menu button does nothing. The footer still links to the
posts, the tags and the About page, so every page stays one tap away.

## Why it matters

A page that is complete on the first answer is fast on a slow phone, reads in any browser, and is
indexed by search engines as it is. It is also simpler to test: the tests of this blog ask for a
page and read its HTML, with no browser at all.
