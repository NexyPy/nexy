# 10 — Data Layer · Loaders (superseded)

## Status: Closed — never shipped

This sub-epic proposed a Remix-style per-route `loader()` callable exposed as
`GET /<route>.data` for the client router. It was **reverted** before shipping:

- Nexy is a **server-first** framework — server-rendered HTML is the source of truth.
- There is **no loader protocol**. Data comes from `.nexy` frontmatter (render-time
  Python), `@Action` (POST RPC), and `.py` API handlers.
- The client router re-fetches server HTML on navigation; it does not fetch per-route
  JSON payloads.

## What happened

An experimental implementation added `loader()` detection, a `.data` endpoint, and
`data-nexy-props` serialization in `fbrouter` and `frontend_route.py`, backed by
`tests/unit/nexy/routers/test_loaders.py`. All of it was **removed** after the
server-first decision. See [the parent README](./README.md) for the full list of
reverted artifacts.

## References

- [10-data-layer README](./README.md) — parent epic, decision record.