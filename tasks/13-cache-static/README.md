# 13 — Cache & Static

## Objective

Nexy has a build-time cache (`__nexy__/build-cache.json`) but **zero runtime cache**.
The epics introduce runtime revalidation (ISR) and a cache hierarchy, matching
Next.js `resumeDataCache`/`INFINITE_CACHE` and Nuxt `PAYLOAD_CACHE`.

## Current state (verified)

- `nexy/builder/__init__.py:51` — `_get_file_fingerprint` (mtime_ns, size).
- `nexy/builder/__init__.py:77` — `_get_config_fingerprint`.
- `nexy/builder/__init__.py:92` — cache file `__nexy__/build-cache.json`.
- `nexy/builder/__init__.py:114-128` — `build(incremental=True)` skips files whose hash
  matches (L128); `_save_cache()` at L176.
- SSG output: `nexy/frontend/scripts/utils.ts:270-305` (`writeComponent` →
  `__nexy__/client/static`).
- No HTTP caching headers, no runtime revalidation, no per-route `staleTime`.

## Competitive anchors

| Framework | Runtime cache mechanism |
|---|---|
| Next.js | `resumeDataCache`, `INFINITE_CACHE`, `CacheSignal` + `work-unit-async-storage` |
| Nuxt | `PAYLOAD_CACHE` Map + `useNitroApp().hooks` |
| TanStack | SWR `staleTime`/`gcTime` on loaders |

## Target

- Per-route `revalidate` config (ISR) at build/scan time.
- A small runtime cache in the response path that serves revalidated HTML when fresh and
  regenerates in background when stale.
- Respect `Cache-Control`/ETag; keep the static file output as the fast path.

## TDD phases

1. **Red** — test: route with `revalidate = 5` returns HTML once, then a second request
   after 5s triggers background regen but still returns cached HTML immediately.
2. **Green** — runtime cache store keyed by pathname; async revalidation task per route.
3. **Green** — `revalidate` config read from route frontmatter/`modules_meta` at scan
   (`fbrouter/__init__.py:189-318`).
4. **Green** — `Cache-Control` header + ETag from build fingerprint
   (`builder/__init__.py:51`).
5. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0.

## Definition of Done

- A static `.tsx`/`.nexy` route with `revalidate` re-renders in background; clients get
  stale-while-revalidate behavior.
- No cache for dynamic routes by default; no behavior change to existing builds.
- Cache store has a TTL and is bounded.

## References

- [Next.js analysis](../competitive/nextjs.md) §5 — cache scoping via AsyncLocalStorage.
- [Nuxt analysis](../competitive/nuxt.md) §6 — `PAYLOAD_CACHE`.
- [TanStack analysis](../competitive/tanstack.md) §4 — SWR windows.

---

### ISR Revalidation (sub-epic)

See [./isr-revalidate/README.md](./isr-revalidate/README.md).