# TanStack Router — Route Tree Generation + Server Functions

Deep dive into `TanStack/router/packages/router-plugin` (captured mid-2026).

## 1. Unplugin factory

`packages/router-plugin/src/index.ts`:

- Exports `unpluginRouterCodeSplitterFactory`, `unpluginRouterGeneratorFactory`, and
  `createRouterPluginContext`.
- Both are unplugin factories → work in Vite, esbuild, webpack, Rollup, and others.
- The code-splitter breaks the route tree into lazy chunks; the generator produces the
  typed route tree.

## 2. Route tree generator

`packages/router-plugin/src/core/router-generator-plugin.ts`:

- Watches `routesDirectory` (chokidar). On create/update/delete of a route file it
  re-runs `Generator.run()` and regenerates `routeTree.ts`.
- `enableRouteGeneration` gates the feature; `routeGenerationDisabled` opts out per file.
- The generated `routeTree.ts` is a typed object tree: `Route` nodes with `path`,
  `getParentRoute`, `getRouteApi`, `children`. Link `to` values are validated at compile
  time (`Link` receives a union of route ids).

**Nexy gap**: Nexy has `keys.auto.ts` (md5 → path mapping,
`nexy/frontend/__init__.py:114-131`) but **no** typed route tree. Links are plain
strings (`nexy/link.py:11`).

## 3. Server functions

- `createServerFn({ type: 'server' })` — three implementations: RPC, stub, and SSR
  wrapper. The SSR wrapper uses an env var (`NEXY_`-style) to decide whether to call the
  server or reuse inlined data.

**Nexy gap**: `@Action` (`nexy/decorators.py:411`) is a single POST implementation — no
RPC/stub/SSR variants, no SSR wrapper that inlines data.

## 4. Caching

- SWR `staleTime`/`gcTime` on route loaders — client-side revalidation window.
- URL-as-state: search params are the single source of truth for filters/pagination.

**Nexy gap**: no client-side SWR; no URL-as-state contract.

## Nexy gaps → epics

- Typed route tree → `TASKS/08-route-tree/type-safe-routes/`
- Client router + URL-as-state → `TASKS/08-route-tree/client-side-routing/`
- Server functions multi-protocol → `TASKS/10-data-layer/`