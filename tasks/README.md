# Nexy Roadmap — Task Board

This directory contains the structured plan to evolve Nexy into a world-class framework.

## Vision & Objectives
Nexy must surpass Django, Next.js, and Astro in **DX** and **Performance**.
- **KISS** (Keep It Simple, Stupid)
- **TDD** (Test-Driven Development)
- **SOLID** (Clean Architecture)

## Architecture Roadmap

*(Phases 00 to 04 have been completed and cleaned up)*

### [05. The Next.js Killer (Road to 10/10)](./05-nextjs-killer/)
These are the advanced architectural changes required to bring Nexy from an 8.5/10 to a perfect 10/10, enabling true Serverless deployment and instant HMR.

1. **[AST Template Compiler](./05-nextjs-killer/01-ast-template-compiler.md)**: Replace regex parsing with a robust HTML AST to handle deeply nested components safely.
2. **[In-Memory VFS](./05-nextjs-killer/02-in-memory-vfs.md)**: Eliminate physical disk writes (`__nexy__/`). Compile Python and HTML directly into RAM for Serverless compatibility.
3. **[True Python HMR](./05-nextjs-killer/03-true-hmr-reload.md)**: Stop cold-killing Uvicorn. Invalidate `sys.modules` in real-time to preserve Vite WebSocket connections and achieve sub-100ms hot reloads.

### [06. CLI Quality Commands](./06-cli-quality-commands/)
Unified CLI commands for type checking, formatting, and testing across Python and frontend files.

1. **[`nexy check`](./06-cli-quality-commands/01-check.md)**: Run mypy, tsc, and compile+check for .nexy/.mdx
2. **[`nexy format`](./06-cli-quality-commands/02-format.md)**: Format .py, .ts, .vue, .svelte, .nexy/.mdx
3. **[`nexy test`](./06-cli-quality-commands/03-test.md)**: Run pytest (--server) and/or vitest (--client)
4. **[Register in CLI](./06-cli-quality-commands/04-register.md)**: Wire up commands + update welcome banner

### [07. Framework Config — Single Framework](./07-framework-config/)
Enforce one frontend framework per project (`useFF`), warn-and-skip out-of-set files, keep `.nexy`/`.md`/`.mdx`/`.py` always active.

1. **[Single Framework Enforcement](./07-framework-config/single-framework/)**: `useFF: FrontendFramework | None`, active extension set derived from the configured framework.

### [08. Route Tree](./08-route-tree/)
The route tree is the shared contract between server and client.

1. **[Client-Side Routing](./08-route-tree/client-side-routing/)**: Hybrid routing — every `routes/*.tsx` is served by generated Python functions on the server AND navigable between routes on the client (App Router model) using a shared `routes.auto.ts` manifest.
2. **[Type-Safe Routes](./08-route-tree/type-safe-routes/)**: Generate a typed route tree (TanStack `routeTree.ts` model) so links and params are checked at compile time.

### [09. SSR Pipeline](./09-ssr-pipeline/)
From synchronous Python rendering to streaming-first output.

1. **[Streaming SSR](./09-ssr-pipeline/streaming-ssr/)**: Flush the HTML shell before the body to improve TTFB, following the Fizz/`chainStreams` model.

### [10. Data Layer](./10-data-layer/)
Nexy must match the data protocols of the big three (RSC, single-fetch, `createServerFn`).

1. **[Loaders](./10-data-layer/loaders/)**: Typed GET data loading per route (Remix loader model), usable by both server and client router.

### [11. Hydration](./11-hydration/)
From eager `<ncc>` mounting to selective hydration.

1. **[Islands Directives](./11-hydration/islands-directives/)**: `client:load/idle/visible/media/only` directives (Astro `astro-island` model) applied to Nexy islands.

### [12. Dev & HMR](./12-dev-hmr/)
Close the gap between what Nexy documents and what it actually ships.

1. **[Browser Error Overlay](./12-dev-hmr/error-overlay/)**: Real overlay for compile failures (`broadcast_error` on the HMR socket).
2. **[Perf Benchmarks](./12-dev-hmr/perf-benchmarks/)**: Regression tests for startup, HMR broadcast latency, and build time.

### [13. Cache & Static](./13-cache-static/)
From build-time cache to runtime revalidation.

1. **[ISR Revalidation](./13-cache-static/isr-revalidate/)**: Runtime revalidation (Next `resumeDataCache` / Nuxt `PAYLOAD_CACHE` model) on top of `build-cache.json`.

## Competitive Analysis
- [Competitive README](./competitive/README.md) — how to read the source analyses.
- [Matrix Synthesis](./competitive/ANALYSIS.md) — 6 mechanisms × 6 frameworks.
- [Next.js](./competitive/nextjs.md) · [Nuxt](./competitive/nuxt.md) · [Remix](./competitive/remix.md) · [TanStack](./competitive/tanstack.md) · [Astro](./competitive/astro.md)

## Quality Gates (Mandatory)
Before completing any task, ensure:
```bash
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v
```
All tasks must maintain 100% backward compatibility with native Nexy functionality.
