# ISR (stale-while-revalidate)

Set `revalidate = N` in the frontmatter of a `.nexy` page to cache it with a stale-while-revalidate
policy.

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

## What Nexy does

- Sends `Cache-Control: public, s-maxage={revalidate}, stale-while-revalidate={revalidate}` on cached
  responses.
- Caches in-process (an in-memory cache) per path.
- Applies the policy only when `revalidate` is a positive integer on the module.

> [!NOTE]
> `.py` API handlers are not pages. Use a different strategy for API caching.

## Next steps

- [SSR](ssr.md): how pages are rendered before caching
- [Pages](../routing/fbr/pages/README.md): layouts and dynamic segments
- [.nexy files](../views/nexyfile.md): frontmatter reference
