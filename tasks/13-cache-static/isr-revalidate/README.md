# 13 — Cache & Static · ISR Revalidation

## Objective

Stale-while-revalidate (ISR) for static Nexy routes: serve cached HTML instantly while a
background task regenerates the page once its `revalidate` TTL expires.

## Current state

- Build cache only: `nexy/builder/__init__.py:92` (`build-cache.json`), fingerprint
  skip at L128.
- Every request re-renders or serves a fixed static file — no revalidation cycle.

## Target architecture

```
request ──► runtime cache store ──fresh?──► serve HTML (fast)
                     │ stale
                     └─► background regen ──► update store + static file
```

## TDD phases

1. **Red** — test: `revalidate = 5` route — 1st request builds HTML; immediate 2nd
   request serves cached; after 6s, a request triggers background regen and still
   returns the old HTML instantly.
2. **Green** — cache store (dict with TTL per pathname) added to the response handler
   (`fbrouter/__init__.py:367-394` HTMLResponse path).
3. **Green** — read `revalidate` from route frontmatter during
   `_scan_modules` (`fbrouter/__init__.py:189-318`).
4. **Green** — background task re-renders and atomically swaps the cached HTML.
5. **Green** — `Cache-Control: stale-while-revalidate` header.
6. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0.

## Definition of Done

- `revalidate` config honored per route; default = no caching (dynamic).
- Stale HTML served immediately; regen happens in background exactly once.
- Cache store bounded (max entries / TTL sweep).
- No change to the build-cache path (`builder/__init__.py:114`).

## References

- Next.js ISR stampede issue (`vercel/next.js#93210`) — avoid thundering herd by
  single-flight regen (one regen per TTL).
- [13-cache-static README](./README.md) — parent epic.
- [Next.js analysis](../competitive/nextjs.md) §5.