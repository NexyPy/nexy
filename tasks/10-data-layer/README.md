# 10 — Data Layer

## Objective

Nexy has no loaders and a single `@Action` POST handler. The big three expose a typed
**GET data protocol** per route (Remix loaders, Next RSC payload, TanStack
`createServerFn`). This epic delivers a typed loader model callable from both server
render and the client router.

## Current state (verified)

- `nexy/decorators.py:411` — `@Action` decorator (POST-only).
- `nexy/routers/actions/store.py:5` (`ActionsStore`), `nexy/routers/actions/engine.py:13`
  (`ActionEngine`) — action engine, POST-only, returns plain data.
- No `@Loader`; route data is baked into `data-nexy-props` on `<ncc>`
  (`nexy/compiler/frontend_route.py:133-147`) and the client re-parses it
  (`nexy/frontend/react.py:30-38`).

## Competitive anchors

| Protocol | Model | Where |
|---|---|---|
| Next RSC | Flight payload `{t,h,q,i,S,...}` passed through render | `app-render.tsx` |
| Remix | single-fetch `.data` URL + TurboStream, CSRF guard | `single-fetch.ts` |
| TanStack | `createServerFn` (RPC / stub / SSR wrapper) | `router-plugin` |
| Nuxt | `devalue` → `window.__NUXT__` | `renderer.ts` |

## Target

- `@Loader` decorator symmetric to `@Action`, returning typed data resolved **before**
  render (server) or on-demand (client router).
- Server render passes loader data into `data-nexy-props` (reuse existing channel).
- Client router fetches `.data`-style payload via `@Loader` before rendering the target
  component (single-fetch model).

## TDD phases

1. **Red** — test: a route file with a `@loader` function runs it before the page
   component, injecting result into props.
2. **Green** — `@Loader` decorator in `decorators.py`, registered like `@Action` in the
   engine/store.
3. **Green** — server render resolves loader data and serializes it into `data-nexy-props`
   (`frontend_route.py:136-147`).
4. **Green** — client router (`08-route-tree/client-side-routing`) calls the loader
   endpoint before `import()` of the component.
5. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0.

## Definition of Done

- `@Loader` route data flows server→props→client without a second fetch on initial load.
- Client-side navigation fetches only the loader payload (`.data`), not full HTML.
- Backward compatible with `@Action` POST routes.

## References

- [Remix analysis](../competitive/remix.md) — `.data` URL + single-fetch.
- [Next.js analysis](../competitive/nextjs.md) — RSC payload.
- [TanStack analysis](../competitive/tanstack.md) — `createServerFn`.
- Client consumption lives in [client-side-routing](../08-route-tree/client-side-routing/).

---

### Loaders (sub-epic)

See [./loaders/README.md](./loaders/README.md).