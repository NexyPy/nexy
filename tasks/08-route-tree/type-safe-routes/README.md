# 08 — Route Tree · Type-Safe Routes

## Objective

Generate a **typed route tree** at build time so `Link` targets and route params are
checked at compile time (TanStack `routeTree.ts` model), replacing the stringly-typed
`Link` and the opaque md5 `keys.auto.ts` mapping.

## Current state

- `nexy/link.py:3-22` — `Link(href: str, ...)`; href is an unchecked string.
- `nexy/frontend/__init__.py:114-131` — `keys.auto.ts` maps `md5(path) → path`; it is a
  lookup table, not a type-safe tree.

## Target

- From `modules_meta` (`fbrouter/__init__.py:129`), emit `routes.auto.ts` with a typed
  `Route` union: every pathname, its params (`{id}`), and its parent layout.
- `Link` accepts `to: Route` + `params` object; invalid targets fail `tsc -b`.
- Generate the file incrementally (only rewrite when content changes), same pattern as
  `keys.auto.ts` (`frontend/__init__.py:130`).

## TDD phases

1. **Red** — test: `routes.auto.ts` contains every pathname from `modules_meta` with
   its param names.
2. **Green** — `fbrouter` (or a new generator) emits the typed tree at build time.
3. **Green** — `Link` accepts the typed union; `tsc -b` fails on a wrong target.
4. **Green** — incremental write (skip if unchanged).
5. **Gates** — ruff, mypy, pytest, `tsc -b`, `nexy build` EXIT=0.

## Definition of Done

- `tsc -b` catches an invalid `Link` target or missing param.
- The generated tree matches `modules_meta` 1:1.
- No behavior change for `.nexy` routes.

## References

- [TanStack analysis](../competitive/tanstack.md) — `routeTree.ts` generation.
- Depends on the shared manifest from [client-side-routing](./client-side-routing/).