# 10 — Data Layer

## Status: Closed — server-first decision

**Decision (2026-06)**: Nexy has **no loader / `.data` protocol**. Nexy is a
server-first framework: the server-rendered HTML is the single source of truth, and
dynamic data flows through the mechanisms that already exist:

- **Page data** is declared in the `.nexy` frontmatter (Python executed at render time,
  see `nexy/compiler/generator/logic.py`).
- **Mutations / RPC** go through `@Action` (POST, `nexy/decorators.py`,
  `nexy/routers/actions/`).
- **Custom endpoints** are plain `.py` route handlers (`GET`/`POST`).

The Remix single-fetch `.data` model, Next RSC payload, and TanStack `createServerFn`
were evaluated and **rejected**: they introduce a parallel client data protocol that
conflicts with the server-first philosophy. The client router therefore navigates by
re-fetching server HTML, and never fetches per-route JSON payloads.

## What was implemented then removed

An experimental `loader()` + `GET /<route>.data` single-fetch implementation was
added (server side only: `_make_request_handler_with_loader`, `_register_data_endpoint`,
`data-nexy-props` serialization) and then **reverted** after the server-first decision.

Removed artifacts:

- `nexy/routers/fbrouter/__init__.py` — `_make_request_handler_with_loader`,
  `_has_loader`, `_register_data_endpoint`, `_register_data_endpoint` call in
  `_register_all_routes`, `JSONResponse` import.
- `nexy/compiler/frontend_route.py` — `__nexy_props_json` module-body code; the
  `<ncc>` template keeps a static `data-nexy-props="{}"`.
- `tests/unit/nexy/routers/test_loaders.py` — deleted (6 tests).

## What remains in place

- `data-nexy-props` on `<ncc>` (`nexy/compiler/frontend_route.py:145`) is a **static**
  empty placeholder; the client runtime parses props on mount
  (`nexy/frontend/react.py:30-38`), which for SPA-style hydration receives props passed
  by the runtime, not loader data.
- `@Action` POST routes, API handlers, and the ISR cache (`nexy/runtime/cache.py`) are
  the data mechanisms. `revalidate` frontmatter (ISR) is unaffected.

## References

- [Remix analysis](../competitive/remix.md) — `.data` URL + single-fetch (rejected).
- [Next.js analysis](../competitive/nextjs.md) — RSC payload (rejected).
- [TanStack analysis](../competitive/tanstack.md) — `createServerFn` (rejected).
- Client consumption lives in [client-side-routing](../08-route-tree/client-side-routing/).