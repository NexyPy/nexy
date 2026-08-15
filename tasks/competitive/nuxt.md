# Nuxt — SSR Renderer Mechanism (renderer.ts)

Deep dive into `nuxt/nuxt/packages/nuxt/src/core/runtime/nitro/renderer.ts`
(commit `71ef8bd3`, captured mid-2026).

## 1. Bundle renderer

- `createRenderer` from `vue-bundle-renderer/runtime` — pairs the **server bundle**
  (`#build/dist/server/server.mjs`) with the **client manifest**
  (`#build/dist/server/client.manifest.mjs`).
- `lazyCachedFunction` loads both artifacts lazily and caches them — the renderer does
  not touch disk per request.

**Nexy gap**: Nexy inlines pre-rendered component HTML from `__nexy__/client/static/`
(`nexy/frontend/scripts/utils.ts:286-288`) and hydrates via `<ncc>`; it has no
server-bundle + client-manifest pairing and re-reads per compile cycle.

## 2. Render path

- `defineRenderHandler` (Nitro) → `renderToString` from `vue/server-renderer`.
- Output: a single buffered HTML string wrapped in `<div id="__nuxt">`.

**Nexy gap**: identical shape (`renderToString` per framework in
`nexy/frontend/scripts/ssg.*.ts`), but Nexy pre-renders at build time and serves static
HTML; Nuxt renders at request time.

## 3. Payload extraction

- `renderPayloadResponse` — server-rendered data is serialized with `devalue` into
  `window.__NUXT__` (plus `_payload.js` route payload extraction).
- This gives Nuxt a hydration contract: the client reuses the exact server state.

**Nexy gap**: Nexy has **no** equivalent. Props are serialized into `data-nexy-props`
attributes on `<ncc>` tags (`nexy/compiler/frontend_route.py:133-147`) and parsed on the
client (`nexy/frontend/react.py:30-38`), but there is no `devalue`-style reusable payload.

## 4. Streaming

- `renderToString` is fully buffered — **no streaming** by default.
- Streaming is an experimental epic (`nuxt/nuxt#4753`, open 7 years; PR `#34411`
  experimental). Nexy is in the same boat.

## 5. HMR / dev

- `vite-node` executes the server bundle in-process; WebSocket sockets push updates.
- No cold restart of the Nitro server.

**Nexy gap**: Nexy watchdog recompiles per file (`nexy/utils/dev/watcher.py`); HMR is
3-tier (Vite + body-swap WS `/_nexy/hmr` + watchdog). See `TASKS/12-dev-hmr/`.

## 6. Cache

- `PAYLOAD_CACHE` Map (devalue of payload) plus `useNitroApp().hooks` lifecycle.
- No AsyncLocalStorage work-unit scoping (unlike Next).

**Nexy gap**: zero runtime cache. See `TASKS/13-cache-static/`.

## Nexy gaps → epics

- Payload serialization contract → `TASKS/10-data-layer/`
- Streaming → `TASKS/09-ssr-pipeline/streaming-ssr/`
- Runtime cache → `TASKS/13-cache-static/`
- Dev/HMR → `TASKS/12-dev-hmr/`