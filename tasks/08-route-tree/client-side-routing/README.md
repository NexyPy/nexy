# 08 — Route Tree · Client-Side Routing (Hybrid Routing)

## Objective

Every `routes/*.tsx` is routed **from the server** with generated Python functions
(current behavior) **and** **between routes on the client** like Next.js App Router —
without reloading the whole document — following the **same code principles** on both
sides.

## Rule

When the view routing in `src/routes/` uses framework components (`.tsx`, `.vue`), Nexy
must provide hybrid routing: server-side navigation (current) + client-side navigation
(component-level, App Router model). `.nexy` routes continue to work via full reload.

## Current state (verified)

`nexy/frontend/runtime.ts:34-88` — client "SPA" nav is actually:

1. `fetch(href)` the **full HTML document**
2. `DOMParser` + `currentMain.innerHTML = newMain.innerHTML`
3. re-run `<script>` tags by cloning nodes
4. `window.history.pushState`

`popstate` → `window.location.reload()` (`runtime.ts:90-92`) — no real back/forward.

## Target architecture

```
server (Python)                        client (TS)
  modules_meta  ──build──►  routes.auto.ts   ──import──►  ClientRouter
  fbrouter:304-318            (shared tree)                   │
       │                                                      ├─ match URL → route
       │                                                      ├─ import() target comp
       │                                                      ├─ render into shared layout
       │                                                      └─ pushState/popstate
  @Action (decorators.py:411)  ◄───────────── fetch() data
```

## TDD phases

1. **Red** — test: `Link` between two `.tsx` routes swaps the rendered component
   **without** a document-HTML `fetch`.
2. **Green — shared manifest**: `fbrouter` exports the same `modules_meta` (pathname,
   layout chain, params, component ref) to `__nexy__/src/routes.auto.ts`, regenerated at
   each build. The server and client walk the **same** tree.
3. **Green — client router**: URL → route match using the same ordering logic as
   `_path_sort_key` (`fbrouter/__init__.py:304`), `import()` the target component entry
   (`entries.ts`), render it inside the shared layout, manage `pushState`/`popstate`.
4. **Green — actions**: `@Action` (`nexy/decorators.py:411`) callable from the router
   for async data.
5. **Refactor** — replace the `<main>` swap in `runtime.ts` with the component router;
   `Link` (`nexy/link.py`) triggers the router; preserve `__nexy_prefetch` prefetching.
6. **Gates** — ruff, mypy `--strict`, pytest, `nexy build` EXIT=0.

## Definition of Done

- Navigating between two `.tsx` routes changes the component **without** full reload.
- URL and params are correct after navigation.
- Browser back/forward work (real `popstate` handling, not reload).
- `.nexy` routes still render via full server reload.
- The same route-tree source feeds both server and client (no duplication).

## References

- [Next.js analysis](../competitive/nextjs.md) — LoaderTree walkers + Flight payload.
- [TanStack analysis](../competitive/tanstack.md) — URL-as-state, route tree.
- [Remix analysis](../competitive/remix.md) — single-fetch data contract.