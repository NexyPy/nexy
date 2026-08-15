# 08 — Route Tree

## Objective

Make the route tree the **shared contract** between the server and the client. Today
Nexy builds `modules_meta` once for the server (`nexy/routers/fbrouter/__init__.py:129`)
but the client has no tree — only a `<main>` innerHTML swap
(`nexy/frontend/runtime.ts:34-88`).

## Sub-epics

1. **[Client-Side Routing](./client-side-routing/)** — hybrid routing: every
   `routes/*.tsx` is served by generated Python functions on the server **and**
   navigable between routes on the client (App Router model) via a shared
   `routes.auto.ts` manifest.
2. **[Type-Safe Routes](./type-safe-routes/)** — generate a typed route tree
   (TanStack `routeTree.ts` model) so `Link` targets and params are checked at compile
   time.

## Competitive anchors

- Next.js: pre-compiled `LoaderTree` embedded in the module
  (`ComponentMod.routeModule.userland.loaderTree`), three walkers (full-tree,
  diff-walk, transport-tree). See [nextjs analysis](../competitive/nextjs.md).
- TanStack: `Generator.run()` → `routeTree.ts` via unplugin, watcher-driven
  regeneration. See [tanstack analysis](../competitive/tanstack.md).
- Remix: declarative `RouteConfigEntry` manifest, no runtime FS scan.
  See [remix analysis](../competitive/remix.md).

## Nexy anchors

- `modules_meta` list + `_path_sort_key` sort: `nexy/routers/fbrouter/__init__.py:304-318`.
- `keys.auto.ts` md5→path mapping: `nexy/frontend/__init__.py:114-131`.
- `data-nexy-link` + `__nexy_prefetch`: `nexy/link.py:11`, `nexy/frontend/runtime.ts:23-31`.
- Client `import()` of components: `nexy/frontend/scripts/entries.ts:102-172`.