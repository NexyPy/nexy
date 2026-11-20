---
title: Hello from a blog made with Nexy
date: 2026-11-02
tags: nexy, meta
summary: What this blog is, how it is built, and where to look in the code.
---

This blog is an example you can copy. Every page is rendered by Python on the server, and a reader
gets complete HTML before a single line of JavaScript runs.

## What is in the project

The posts are Markdown files in `content/posts/`. `src/blog/posts.py` reads them once, renders
them with `markdown-it-py`, and keeps them in memory. The pages under `src/routes/` ask it for what
they show:

| Page | File |
|---|---|
| The list of posts | `src/routes/index.nexy` |
| One post | `src/routes/posts/[slug].nexy` |
| The posts of a tag | `src/routes/tags/[tag].nexy` |
| The feed | `src/routes/rss.py` |

## Why server-rendered

A blog is read far more often than it is written. Rendering on the server means the text is there
on the first byte, search engines read it as it is, and a slow phone does no extra work.

## Where to start

Write a new file in `content/posts/`, restart `nx dev`, and it is on the home page.
