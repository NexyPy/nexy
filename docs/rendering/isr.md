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
| Storage | selected by `useISRCache`: memory by default, file, Redis, or a custom store |
| Bound | 256 entries for the memory store, least recently used evicted; file and Redis keep entries until invalidated |
| Response header | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

Every ISR response carries that header, including the first render and a fallback render when the
store is down. A CDN can use it to keep its own copy of the same public URL.

## Rendering lifecycle

1. A request arrives for a page that declares `revalidate`.
2. No entry yet: the page is rendered, stored, and returned.
3. Entry younger than `N` seconds: returned as is, the page is not rendered.
4. Entry older than `N` seconds: the **stale** entry is returned immediately, and a background task
   renders a fresh one.
5. If that background render fails, the stale entry stays and the next stale request tries again.
6. If the store fails, the page is rendered and returned without a cached entry. The request still
   succeeds.

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

## Choose a store

Set `useISRCache` in `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useISRCache = "file"
```

| Value | Store | Shared by |
|---|---|---|
| not set, `None`, or `"memory"` | process memory, bounded to 256 entries | one worker |
| `"file"` | JSON files in `.nexy/isr` | workers on one host |
| `{"type": "file", "directory": ".cache/isr"}` | JSON files in the given directory | workers on one host |
| `"redis"` | Redis at `redis://localhost:6379/0` | any worker that reaches the server |
| `{"type": "redis", "url": "redis://cache:6379/0"}` | Redis at that URL | any worker that reaches the server |
| `{"type": "redis", "client": client}` | the Redis client you pass | any worker that reaches the server |
| an object with `get`, `set` and `invalidate` | your own store | whatever it shares |

The Redis store needs the client package: `uv add redis`. It is not installed with Nexy. A custom
store implements the `ISRCache` protocol from `nexy.modules.runtime.cache`; its `get` returns a
`CacheEntry` or `None`.

File entries are written atomically, so a worker never reads a half-written page. Workers that use
the same directory or the same Redis server read the same entry. A broken store only costs a render:
it never answers the request with an error.

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

The first request to `/blog/hello` renders and stores. The next 300 seconds are served from the
selected store. `/blog/other` is a separate entry, rendered and stored on its own. In a real project
`posts` comes from a database or a service, called once per regeneration.

## What a CDN can and cannot share

A CDN that honours `cache-control` can keep one copy of `/blog/hello` for `s-maxage` seconds and
serve it while it revalidates. It shares that copy between visitors and workers because the response
says `public`.

A CDN does not know the Nexy store. `revalidate()` in an [Action](../guides/actions.md) removes the
entry from the configured Nexy store, but it does not purge a CDN. The CDN keeps its copy until its
own window ends, or until you configure its purge.

Do not give a CDN a page whose HTML depends on a visitor. The response says `public`, and Nexy's key
is the path alone: two query strings on one path share one entry. A session, a cookie, or a user id
in the HTML can be served to another visitor.

## Limitations

**Nexy guarantees** the cache key is the path, the stale copy is served during regeneration, and a
store failure falls back to a render.

**By convention**, a page that declares `revalidate` is public content. Write it as if every visitor
sees the same HTML.

**Your application is responsible for** everything else:

| Limit | What it means |
|---|---|
| Query string ignored | `/search?q=a` and `/search?q=b` share one entry. Do not cache a search page. |
| Session not isolated | The response says `public`, and the first visitor's HTML is served to all. Never read the session in a page with `revalidate`. |
| CDN not purged | `revalidate()` purges the Nexy store, not a CDN or another proxy in front of it. |
| No TTL in file and Redis stores | Entries stay until `revalidate()` or your own cleanup removes them. The memory store evicts the least recently used entry after 256. |
| Concurrent regenerations | Nothing deduplicates them: ten stale requests can start ten renders. |
| Errors are silent | A failing regeneration or store operation keeps serving the page; the failure is not returned. |

## Next steps

- [SSR](ssr.md): how the page is rendered before it is cached
- [Actions](../guides/actions.md): the `revalidate` header and store invalidation
- [Config](../reference/config.md#server): `useISRCache`
- [Performance](../deployment/performance.md)
- [Pages](../routing/fbr/pages/README.md): layouts and dynamic segments
