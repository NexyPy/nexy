# Matrix Synthesis — 6 Mechanisms × 6 Frameworks

| Mechanism | Next.js (app-render.tsx) | Nuxt (renderer.ts) | Remix/RR (single-fetch.ts) | TanStack (router-plugin) | Astro (astro-island) | **Nexy** |
|---|---|---|---|---|---|---|
| **Route tree** | `LoaderTree` nested tuple built at build time, full-tree/diff-walk/transport-tree walkers | Scan pages + Nitro manifest | `routes.ts` → `RouteManifest` walk | `Generator.run()` → `routeTree.ts` via unplugin | `RoutesList` manifest (create-manifest) | FS scan → `modules_meta`, sort `_path_sort_key` |
| **SSR render** | **Two streams**: Flight RSC + Fizz HTML shell | `renderToString` → `<div id="__nuxt">` buffered | `renderHtml` one pass + TurboStream handoff | route loader + client | `renderToString` per page (SSG-first) | **synchronous Python** `def Index(...) -> str` buffered |
| **Data protocol** | RSC payload `{t,h,q,i,S,...}` | `devalue` → `window.__NUXT__` | **Single-fetch** `.data` URL + `X-Remix-Response` + TurboStream | `createServerFn` (3 impls) | baked at build time | `@Action` POST + coerced path params |
| **Hydration** | `<AppRouter>` hydrate | `createApp.mount` | client `hydrateRoot` | — | **`astro-island` custom element** + `client:*` directives | `<ncc>` islands `hydrateRoot` (React/Vue/Svelte) |
| **Streaming/TTFB** | `chainStreams`/`continueFizzStream`, shell before body | **NO** (streaming experimental nuxt#4753) | `encodeViaTurboStream` | NO | `server:defer` islands | **NO** — everything buffered |
| **Static/PPR** | PPR: prospective+finale passes, `postponed` holes | prerender + payload extraction | build pre-render | SSG | static-first by default | esbuild SSG per framework |
| **Dev/HMR** | Turbopack + dev-validation-worker + WS | vite-node + sockets | vite plugin | unplugin `watchChange` + chokidar | vite | watchdog + vite + **body-swap WS** |
| **Cache** | AsyncLocalStorage `work-unit` + `CacheSignal` | `PAYLOAD_CACHE` Map | — | SWR staleTime | — | **build-cache JSON only**, zero runtime cache |

## Key Findings

1. **Nexy is the only framework doing synchronous Python SSR** — no Flight/Fizz, no
   TurboStream. Strength (startup speed) and weakness (no streaming, no partial rendering).
2. **Gap #1 = data layer**: Next has RSC payload, Remix has single-fetch (`.data` +
   TurboStream), TanStack has `createServerFn`. Nexy has only `@Action` POST — no loaders,
   no GET data fetch. → `TASKS/10-data-layer/`
3. **Gap #2 = streaming**: everyone streams except Nuxt (will) and Nexy. Nexy buffers
   everything. → `TASKS/09-ssr-pipeline/streaming-ssr/`
4. **Astro has the only true custom-element island** (`astro-island` + load/idle/visible/
   media directives) — Nexy has `<ncc>` but everything is eager. → `TASKS/11-hydration/`
5. **Nuxt `renderPayloadResponse`** (devalue + `_payload.js` extraction) is a mechanism
   Nexy does not have at all.
6. **Client routing**: Next.js ships App Router client navigation; Nexy `runtime.ts`
   only swaps `<main>` innerHTML after a full document fetch. → `TASKS/08-route-tree/client-side-routing/`

## Header Protocol Comparison

| Header | Next.js | Remix | Nexy |
|---|---|---|---|
| Router state tree | `NEXT_ROUTER_STATE_TREE_HEADER` | — | — |
| Current URL | `NEXT_URL` | — | — |
| RSC request | `RSC_HEADER` | — | — |
| Prefetch | `NEXT_ROUTER_PREFETCH_HEADER` | — | — |
| HMR refresh | `NEXT_HMR_REFRESH_HEADER` | — | — |
| Single-fetch response | — | `X-Remix-Response` | — |
| HMR in-body | — | — | `X-Nexy-HMR: 1` |

Full analysis per framework: [nextjs](./nextjs.md) · [nuxt](./nuxt.md) · [remix](./remix.md) ·
[tanstack](./tanstack.md) · [astro](./astro.md).