# ISR (stale-while-revalidate)

## Definition

ISR caches the HTML of one page, per URL, and serves it until its window expires. The expired copy
is still served while a new one is rendered in the background: that is *stale-while-revalidate*.

## How it works

`revalidate = N` in the frontmatter of a `.nexy` page turns it on. `N` is a number of seconds; a
missing, zero or negative value means no cache at all.

The cache key is the **request path only** - `request.scope["path"]`. The query string is not part
of it.

| What | Value |
|---|---|
| Key | the URL path (`/blog/hello`) |
| Storage | in memory, in the process that renders the page |
| Bound | 256 entries per process, least recently used evicted |
| Response header | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

## Rendering lifecycle

1. A request arrives for a page that declares `revalidate`.
2. No entry yet: the page is rendered, stored, and returned.
3. Entry younger than `N` seconds: returned as is, the page is not rendered.
4. Entry older than `N` seconds: the **stale** entry is returned immediately, and a background task
   renders a fresh one.
5. If that background render raises, the stale entry stays and the next stale request tries again.

## When to use

- The same HTML for every visitor: a blog post, a product page, a documentation page.
- The page is read often and changes rarely.
- The data can be a few seconds old without anyone noticing.

## Configuration

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

`N` is a plain integer. There is no per-route override elsewhere, and `.py` handlers are not pages:
they never enter this cache.

## Example

A blog post that reads a database:

```nexy filename="src/routes/blog/[slug].nexy"
---
revalidate = 300
slug: prop[str] = "untitled"
posts = {"hello": {"title": "Hello"}, "other": {"title": "Other"}}
post = posts.get(slug, {"title": "Untitled"})
---
<h1>{{ post.title }}</h1>
```

The first request to `/blog/hello` renders and stores. The next 300 seconds are served from memory.
`/blog/other` is a separate entry, rendered and stored on its own. In a real project `posts` comes
from a database or a service, called once per regeneration.

## Limitations

**Nexy guarantees** the cache key is the path, the stale copy is served during regeneration, and the
store is bounded and thread-safe.

**By convention**, a page that declares `revalidate` is public content. Write it as if every visitor
sees the same HTML.

**Your application is responsible for** everything else:

| Limit | What it means |
|---|---|
| Query string ignored | `/search?q=a` and `/search?q=b` share one entry. Do not cache a search page. |
| Session not isolated | The response says `public`, and the first visitor's HTML is served to all. Never read the session in a page with `revalidate`. |
| No server-side invalidation | Nothing purges an entry before its window ends. `revalidate(...)` inside an [Action](../guides/actions.md) only tells the **browser** to reload a path; it does not touch this cache. |
| One cache per process | Several workers keep several caches, with different contents. |
| Concurrent regenerations | Nothing deduplicates them: ten stale requests can start ten renders. |
| Errors are silent | A failing regeneration keeps serving the old page; the failure is logged, not returned. |

## Next steps

- [SSR](ssr.md): how the page is rendered before it is cached
- [Actions](../guides/actions.md): the `revalidate` header, and what it does not do
- [Performance](../deployment/performance.md)
- [Pages](../routing/fbr/pages/README.md): layouts and dynamic segments
