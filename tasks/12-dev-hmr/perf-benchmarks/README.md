# 12 — Dev & HMR · Perf Benchmarks

## Objective

Regression tests for the performance claims: sub-second startup, sub-100ms HMR
broadcast, and fast builds. These belong in `tests/` marked `@pytest.mark.slow`, not in
the README as unverified claims.

## Current state (verified)

- **Done**: perf benchmarks exist in `tests/` marked `@pytest.mark.slow` for builder,
  HMR, and SSG (`tests/unit/nexy/builder/test_builder_benchmark.py`,
  `tests/unit/nexy/runtime/test_hmr_benchmark.py`,
  `tests/unit/nexy/frontend/test_ssg_benchmark.py`).
- **Done**: SSG render loop parallelized. `nexy/frontend/scripts/utils.ts` gained
  `mapPool(files, concurrency=cpuCount())`; `ssg.{react,preact,solid}.ts` process each
  file through it (bounded concurrency = `os.cpus().length`). Dispatcher
  `nexy/frontend/scripts/ssg.ts` measures elapsed time and writes it to
  `__nexy__/client/ssg-report.json` (`{ timingMs, entries }`).
- The old README claim (`Promise.all(jobs)` at `ssg.ts:84`) predates the pool; the
  dispatcher now fans out per-framework jobs in parallel and each framework render
  loop is pooled internally.

## TDD phases

1. **Red** — test: building N=50 synthetic routes completes under a threshold (e.g. 1s),
   `@pytest.mark.slow`.
2. **Green — benchmark harness** — `tests/unit/nexy/builder/test_builder_benchmark.py`
   scaffolding 50 routes in a temp workspace, assert elapsed.
3. **Red** — test: `HMRManager.broadcast` round-trip `< 100ms`.
4. **Green** — `tests/unit/nexy/runtime/test_hmr_benchmark.py` using the capture stub
   (`_capture_broadcast` pattern), assert elapsed.
5. **Green — SSG worker pool** — `nexy/frontend/scripts/utils.ts` gains `mapPool(files,
   concurrency=os.cpus().length)`; `ssg.{react,preact,solid}.ts` use it around the
   `renderToString` import loop; timing logged to `ssg-report.json`. **Done.**
6. **Gates** — ruff, mypy, pytest `-m "not slow"` in CI fast lane + `-m slow` nightly.

## Definition of Done

- `@pytest.mark.slow` benchmarks exist for builder, HMR, SSG.
- SSG actually parallelizes via `os.cpus().length` (matching the README claim).
- CI green: `pytest -m "not slow"` fast; nightly runs `-m slow`.
- Thresholds documented in the test files.

## References

- [Next.js analysis](../competitive/nextjs.md) — sub-second startup is the whole point
  of Nexy; assert it or drop the claim.
- [Astro analysis](../competitive/astro.md) §1 — build lifecycle hooks to instrument
  timing cleanly.