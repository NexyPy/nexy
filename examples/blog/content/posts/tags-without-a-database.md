---
title: Tags without a database
date: 2026-10-26
summary: Tags are one line in the header of each post. The blog counts them when it reads the files.
tags: python, design
---

Every post can carry tags in its header:

```text
tags: python, design
```

That line is the whole data model. There is no table of tags to keep in step with the posts.

## Counting

When the blog reads the posts, it already has every tag. `Counter` from the standard library
counts them in one line, and a sort puts the most used first, then the rest by name:

```python
counts = Counter(tag for post in all_posts() for tag in post.tags)
return sorted(counts.items(), key=lambda item: (-item[1], item[0]))
```

## Two pages

[/tags](/tags) lists every tag with its number of posts. `/tags/python` lists the posts of one
tag, and answers 404 for a tag no post carries, so a typo in an address never shows an empty page.

Tags are read in lower case: `Python` and `python` are one tag.

## When a database earns its place

Files are enough while one person writes and the posts number in the hundreds. A database starts
to pay when readers write too, with comments or likes, when several authors edit at once, or when
search has to rank thousands of posts. Until then, a folder of Markdown files is easy to back up,
to review in a pull request, and to move anywhere.
