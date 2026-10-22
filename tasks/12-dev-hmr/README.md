# 12 — Dev & HMR

## Objective

Close the gap between what Nexy documents (Sub-100ms HMR, browser error overlay) and
what it ships. The HMR layer is 3-tier today (Vite HMR + body-swap WebSocket + file
watcher); the **browser error overlay is claimed in README but unimplemented**, and the
SSG pipeline claims a worker pool (`os.cpus().length`) that does not exist.

## Current state (verified)

- `nexy/runtime/hmr.py:6` — `HMRManager` singleton.
- `nexy/runtime/hmr.py:27` — `_send` hardcodes message `{"type": "nexy:reload", "path": path}`
  (`hmr.py:29`); only `broadcast_reload` exists — **no `broadcast_error`**.
- `nexy/vite.py:62-68` — client WS listens for `nexy:reload`, sends `X-Nexy-HMR: 1`
  header on body-swap; **no error case handler in the browser**.
- `nexy/utils/dev/watcher.py` — compiles per file, prints errors to console but never
  broadcasts them to the browser.
- `nexy/frontend/scripts/ssg.ts:84` — `Promise.all(jobs)` sequential-ish over files;
  **no worker pool**, README claim untrue.

## Competitive anchors

- Next.js: dev-validation-worker + HMR refresh header (`NEXT_HMR_REFRESH_HEADER`).
- Nuxt: vite-node + socket push.
- Vite/Esbuild dev servers ship error overlays natively — the expectation.

## Sub-epics

1. [Browser Error Overlay](./error-overlay/) — surface compile errors as an overlay.
2. [Perf Benchmarks](./perf-benchmarks/) — regression tests for startup/HMR/build.

## Definition of Done (epic)

- `nx dev` shows a browser overlay on a `.nexy`/`.mdx` compile error.
- HMR + build timings are asserted in CI (`< 100ms` broadcast, `< 1s` build).
- `ruff`, `mypy --strict`, `pytest`, `nexy build` all green.

## References

- [Next.js analysis](../competitive/nextjs.md) §7 (error handling), §8 (HMR header).
- [Astro analysis](../competitive/astro.md) §4 (build hooks for instrumentation).

---

### Browser Error Overlay

See [./error-overlay/README.md](./error-overlay/README.md).

---

### Perf Benchmarks

See [./perf-benchmarks/README.md](./perf-benchmarks/README.md).