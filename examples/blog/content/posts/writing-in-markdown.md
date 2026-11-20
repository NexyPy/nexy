---
title: Writing posts in Markdown
date: 2026-11-09
tags: writing, markdown
summary: The header every post starts with, what each field does, and how headings become a table of contents.
---

A post is one Markdown file. Its name is its address: `writing-in-markdown.md` is served at
`/posts/writing-in-markdown`.

## The header

Every post starts with a few lines between two `---`:

```text
---
title: Writing posts in Markdown
date: 2026-11-09
tags: writing, markdown
summary: One sentence for the list and the feed.
---
```

`title` and `date` are required. `tags` is a list separated by commas; each tag gets its page under
`/tags/`. `summary` is the sentence the list of posts and the RSS feed show.

## Headings and the table of contents

Each second-level heading (`## Like this`) gets an id and a line in the table of contents beside
the post, so a reader can jump to it and share a link to it.

## Reading time

The minutes shown under the title count 220 words a minute. They are worked out when the post is
read, so they always match the text.
