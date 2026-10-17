# 08 — Route Tree · Type-Safe Routes

## Objective

Generate a **typed route tree** at build time so `Link` targets and route params are
checked at compile time (TanStack `routeTree.ts` model), replacing the stringly-typed
`Link` and the opaque md5 `keys.auto.ts` mapping.

## Current state

- `nexy/frontend/__init__.py` generates a typed `routes.auto.ts` contract:
  `export type NexyRoute = { path; file; layout; params }` +
  `export const NEXY_ROUTES`, derived from `src/routes` with layout-chain and
  dynamic params marking. Written incrementally (skip when unchanged).
- The generated `runtime.ts` consumes `NEXY_ROUTES` via `matchRoute()` (dynamic
  `{slug}`/`{...rest}` segments + params), `navigate()`, `renderRoute()`, and
  `popstate` handling — client-side routing without full reload.
- `keys.auto.ts` (md5 lookup) is retained for component lazy-loading
  (`__nexy_import`).
- Layout files are recognized for every active route extension (`layout.tsx`,
  `layout.vue`, ...) even when no framework registry is configured.

## Target

- From `modules_meta` (`fbrouter/__init__.py:129`), emit `routes.auto.ts` with a typed
  `Route` union: every pathname, its params (`{id}`), and its parent layout.
  **Done** — manifest generated from `src/routes` with layout chain + params.
- `Link` accepts a typed `href: Route` (Next.js API); invalid targets fail `tsc -b`.
  **Done** — `routes.auto.ts` emits `export type Route` (pathname literals, dynamic
  segments as `` `${string}` `` template literals); a typed client `Link` component
  (`__nexy__/src/Link.tsx`) accepts `href: Route`, renders `data-nexy-link` and
  prefetches on hover (`__nexy_prefetch`). The server `Link` stays stringly-typed
  (server-first); the client router performs typed matching via `matchRoute`/`NEXY_ROUTES`.
- Generate the file incrementally (only rewrite when content changes), same pattern as
  `keys.auto.ts` (`frontend/__init__.py:130`). **Done**.

## TDD phases

1. **Red** — test: `routes.auto.ts` contains every pathname from `modules_meta` with
   its param names. **Done.**
2. **Green** — `fbrouter` (or a new generator) emits the typed tree at build time.
   **Done** (`frontend/__init__.py` `generate_route_manifest`).
3. **Green** — `Link` accepts the typed union; `tsc -b` fails on a wrong target.
   **Done** — typed client `Link` (`__nexy__/src/Link.tsx`, `href: Route`) emitted by
   `_generate_client_link`; verified via `tsc` (invalid `href` → `TS2322`).
4. **Green** — incremental write (skip if unchanged). **Done.**
5. **Gates** — ruff, mypy, pytest, `tsc -b`, `nexy build` EXIT=0.

## Definition of Done

- `tsc -b` catches an invalid `Link` target or missing param. **Done.**
- The generated tree matches `modules_meta` 1:1. **Done** (from `src/routes`).
- No behavior change for `.nexy` routes. **Done.**

## References

- [TanStack analysis](../competitive/tanstack.md) — `routeTree.ts` generation.
- Depends on the shared manifest from [client-side-routing](./client-side-routing/).