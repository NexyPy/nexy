---
title: Following this blog with RSS
date: 2026-11-18
tags: rss, nexy
summary: The feed is a Python route that answers XML: twenty lines, and every reader app can follow the blog.
---

`/rss` answers an RSS 2.0 feed of every post. Copy that address into a feed reader to follow the
blog.

## A route that is not a page

`src/routes/rss.py` is a Python route handler: its `GET` function answers the request, here with
XML instead of a page. It reads the same posts as the pages, so the feed never falls behind.

## What each entry holds

The title, the address of the post, its date and its summary. A reader app shows the summary and
opens the post on the blog for the rest.
