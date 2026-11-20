---
title: One file, one post
date: 2026-08-24
summary: A post is a Markdown file with a short header, and the name of the file is its address.
tags: markdown, writing
---

Writing a post here means adding one file to `content/posts/`. Its name is its address:
`one-file-one-post.md` is served at `/posts/one-file-one-post`.

## The header

A post opens with a few lines between two `---`, one `key: value` per line:

```text
---
title: One file, one post
date: 2026-08-24
summary: One sentence for the list of posts and for the feed.
tags: markdown, writing
---
```

`title`, `date` and `summary` are required. `tags` is a list separated by commas, and may be left
out. When a field is missing, the blog names the file and the field instead of showing a broken
page.

## The text

Below the header is Markdown: paragraphs, lists, links, tables, `code` and fenced blocks. Raw HTML
is shown as text, so a post can quote a `<script>` tag without running it.

Each `## Section` gets an anchor, and the page of the post lists them under "On this page". This
post has four, so you see four links there.

## Reading time

The blog counts the words of the text and divides by 220, the pace of an adult reading on a
screen, then rounds up. A post is never shorter than one minute.

## Changing a post

`src/blog/posts.py` reads a file again as soon as it changes, so a reload shows your edit while
`nx dev` runs. Nothing else is cached.
