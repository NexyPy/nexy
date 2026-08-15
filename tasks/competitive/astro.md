# Astro — Islands + Build Mechanism

Deep dive into `withastro/astro/packages/astro` (captured mid-2026).

## 1. Build pipeline

`src/core/build/index.ts`:

- `runHookBuildSetup`, `runHookBuildConfigDone`, `runHookBuildStart`,
  `runHookBuildDone` — a lifecycle hook system around the build.
- `createRoutesList` builds the `RoutesList` manifest; `collectPagesData` groups pages by
  static vs server (`getPrerenderDefault`).
- `viteBuild` (`static-build`) handles static pages; server pages are deferred to a
  runtime renderer (Node/Deno/edge adapters).

**Nexy gap**: Nexy build is `Builder().build()` (`nexy/builder/__init__.py:114`) with no
hook lifecycle, single-shot `esbuild.build`, and a client-only `Promise.all` over jobs
(`nexy/frontend/scripts/ssg.ts:84`).

## 2. The island custom element

`src/runtime/client/astro-island.ts`:

- `<astro-island>` custom element wraps every interactive component.
- `client:load|idle|visible|media|only` directives control when hydration runs.
- The element holds `props`, `ssr` (server-rendered HTML), and the component URL; it
  mounts via `astro:hydrate` event.

**Nexy gap**: Nexy `<ncc>` (`nexy/compiler/frontend_route.py:133-147`) carries
`data-nexy-*` attributes and mounts eagerly at `DOMContentLoaded`
(`nexy/frontend/react.py:24-50`). No directive-controlled hydration. See
`TASKS/11-hydration/`.

## 3. Hydration directives

`src/runtime/client/idle.ts`:

- `requestIdleCallback`, falling back to `setTimeout` (200ms default).

`src/runtime/client/visible.ts`:

- `IntersectionObserver` on the element's children (because `astro-island` has
  `display: contents`), `rootMargin` option, disconnects after hydration.

**Nexy gap**: no idle/visible/media hydration triggers. Astro's headline number: islands
cut JS from 180kb → 35kb and FCP from 2.1s → 0.8s.

## 4. Server islands

- `server:defer` — server-rendered islands that stream in post-shell (Astro 4.10+).

**Nexy gap**: no server islands; `server:defer` equivalent absent.

## Nexy gaps → epics

- Islands directives → `TASKS/11-hydration/islands-directives/`
- Streaming via deferred server islands → `TASKS/09-ssr-pipeline/streaming-ssr/`
- Build lifecycle hooks → `TASKS/12-dev-hmr/perf-benchmarks/` (observability)