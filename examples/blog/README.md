# Blog

A blog written in Markdown and rendered by Python on the server: a list of posts, one page per
post with its table of contents and reading time, tags, an About page and an RSS feed. Every page
is complete HTML on the first byte and reads the same with JavaScript turned off.

![Blog](../../docs/assets/examples/blog.png)

## What it shows

| Nexy feature | Where |
|---|---|
| `.nexy` pages: Python frontmatter, Jinja template | `src/routes/index.nexy` |
| A dynamic segment, and a 404 for an unknown one (`notFound()`) | `src/routes/posts/[slug].nexy`, `src/routes/tags/[tag].nexy` |
| A Markdown page inside the layout of the site | `src/routes/about.md` |
| A route that answers XML instead of a page | `src/routes/rss.py` |
| `/sitemap.xml` from `useSiteUrl` | `nexyconfig.py` |
| A component with a prop | `src/components/PostCard.nexy` |
| Tests of the posts and the feed | `tests/test_posts.py` |

## Run it

```bash
git clone https://github.com/NexyPy/nexy && cd nexy/examples/blog
uv sync
bun install          # or npm install, pnpm install
uv run nx dev
```

Open the address `nx dev` prints.

## Write a post

Add a file to `content/posts/`; its name is its address (`my-post.md` is `/posts/my-post`):

```text
---
title: My post
date: 2026-12-01
tags: nexy, notes
summary: One sentence for the list and the feed.
---

The text, in Markdown. Each `## Heading` gets a line in the table of contents.
```

The posts are read once, when the server starts: restart `nx dev` to see a new one. Set
`useSiteUrl` in `nexyconfig.py` to the address the blog is published at, for the feed and the
sitemap.

## Test it

```bash
uv run pytest
```

## Files

```text
content/posts/           the posts, one Markdown file each
src/
  blog/posts.py          reads the posts: header, HTML, table of contents, reading time, tags
  routes/index.nexy      the list of posts
  routes/posts/[slug].nexy  one post
  routes/tags/           every tag, and the posts of one
  routes/about.md        the About page
  routes/rss.py          the RSS feed
  components/PostCard.nexy  one post in a list
tests/test_posts.py      the posts and the feed
```
