# Next.js — App Router Mechanism (app-render.tsx)

Deep dive into `vercel/next.js/packages/next/src/server/app-render/app-render.tsx`,
~10,556 lines (copy captured mid-2026).

## Entry points

- `renderToHTMLOrFlight` (l.3344) — dev mode, single unified path.
- `prerenderToHTMLOrFlight` (l.3388) — production / static prerender.

Both converge on a `LoaderTree` walk that produces a Flight payload **and** an HTML stream
simultaneously.

## 1. Loader Tree

- Built at build time and embedded in the module: `ComponentMod.routeModule.userland.loaderTree`
  (~l.695). Nexy equivalent: `modules_meta` list in `nexy/routers/fbrouter/__init__.py:129`.
- `LoaderTree` is a **nested tuple**: `[segment, parallelRoutes, components, staticSiblings?]`.
- Three walkers: full-tree, diff-walk (only changed segments), transport-tree (prefetch).
- The tree is compiled ahead of time — the server never re-scans the filesystem at request time.

**Nexy gap**: Nexy scans `src/routes` at import time (`fbrouter/__init__.py:184-187`) and
builds a flat `modules_meta`. No nested parallel-route tree, no pre-compiled tuple.

## 2. Flight / RSC protocol

- Serializes component trees to a Flight payload: `{ t, h, q, i, S, ... }` field codes.
- `flightRouterState` diffing lets the client update only changed segments.
- The HTML stream and the RSC stream are produced together from the same walk.

**Nexy gap**: no RSC; Nexy renders to HTML only and returns it via `HTMLResponse`.

## 3. Streaming (Fizz)

- `chainStreams` / `continueFizzStream`: the HTML shell flushes first, then the body streams.
- `createDocumentClosingStream` closes the document when the last segment resolves.
- Provides sub-100ms TTFB on dynamic routes.

**Nexy gap**: all responses are buffered `HTMLResponse`. See `TASKS/09-ssr-pipeline/streaming-ssr/`.

## 4. PPR / dynamic

- `StaticGenBailoutError` + postponing: static segments render proactively, dynamic holes
  are postponed and resumed. PPR runs two passes (prospective + finale).

**Nexy gap**: no partial pre-rendering; pages are either fully static (SSG) or fully dynamic.

## 5. Cache

- `resumeDataCache`, `INFINITE_CACHE`, `CacheSignal` — all scoped via
  `work-unit-async-storage` (AsyncLocalStorage).
- The cache is per-request-work-unit, not a global map.

**Nexy gap**: `nexy/builder/__init__.py:92` writes `__nexy__/build-cache.json` (mtime+size
fingerprint, l.51) at build time only; zero runtime cache. See `TASKS/13-cache-static/`.

## 6. Actions

- `handleAction` in the same render path as pages — actions are POSTs routed through the
  App Router. Redirects and errors are special throwable objects (`isRedirectError`,
  `isDynamicServerError`).

**Nexy gap**: `@Action` (`nexy/decorators.py:411`) is a separate POST-only path with no
router integration.

## 7. Error handling

- `createErrorHandler` converts render exceptions into flight/HTML error responses.
- Custom error boundaries via `error.tsx`.

**Nexy gap**: Nexy has `errors.nexy`/`notfound.nexy` scoped handlers
(`fbrouter/__init__.py`), but the app-level handler registration order currently
overrides the FBR ones (`nexy/routers/app.py`).

## 8. Headers

`NEXT_ROUTER_STATE_TREE_HEADER`, `NEXT_URL`, `RSC_HEADER`, `NEXT_ROUTER_PREFETCH_HEADER`,
`NEXT_HMR_REFRESH_HEADER`.

**Nexy gap**: no router-state tree header; client navigation is not tree-aware.

## Nexy gaps → epics

- Route tree structure → `TASKS/08-route-tree/`
- Streaming / TTFB → `TASKS/09-ssr-pipeline/streaming-ssr/`
- Data protocol (no RSC, only `@Action`) → `TASKS/10-data-layer/`
- Runtime cache → `TASKS/13-cache-static/`