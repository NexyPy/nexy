---
title: Hello, world
date: 2026-08-03
summary: What this blog is, what it is made of, and where each part of it lives.
tags: meta, nexy
---

This is the first post of Plain Text, a small blog about building for the web with Python. It is
also its own example: every page you read here comes from the code next to it, in the
`examples/blog` folder of Nexy.

## What it is made of

- **Markdown files.** Each post is a file in `content/posts/`. There is no database and no admin
  page: you write a post in your editor and commit it.
- **Python pages.** A page is a `.nexy` file: a few lines of Python at the top, HTML below. The
  server renders it, so the browser gets the whole page with the first answer.
- **One stylesheet.** `src/globale.css` holds every style, in plain CSS.

## Where to look

| To change | Open |
|---|---|
| How a post is read | `src/blog/posts.py` |
| The list of posts | `src/routes/index.nexy` |
| One post | `src/routes/posts/[slug].nexy` |
| The tags | `src/routes/tags/` |
| The feed | `src/routes/rss.py` |

## What comes next

Each of the next posts explains one part: how a post is written, why the pages need no
JavaScript, how the feed is made, how tags work without a database, and how dark mode avoids the
white flash.
