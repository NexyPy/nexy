# 11 — Hydration · Islands Directives

## Objective

Implement Astro-style `client:load | idle | visible | media | only` directives for Nexy
islands, so hydration can be deferred or visibility-triggered instead of eager.

## Current state

- `<ncc>` tags are hydrated eagerly at `DOMContentLoaded`
  (`nexy/frontend/react.py:24-50`); runtime entry point mounts unconditionally
  (`react.py:77` `hydrateRoot`, `vue.py:72-73`).
- No directive parsing anywhere.

## Target attributes on `<ncc>`

| Directive | Behavior |
|---|---|
| `client:load` | hydrate on `window load` |
| `client:idle` | hydrate on `requestIdleCallback` (fallback `setTimeout 200ms`) |
| `client:visible` | `IntersectionObserver`, disconnect after hydrate |
| `client:media="(min-width:640px)"` | `matchMedia` |
| `client:only` | client-only, no server HTML — emit `<div id="{id}-root"></div>` placeholder |

## TDD phases

1. **Red** — test: a `<ncc client:idle>` is **not** hydrated immediately; test that a
   `requestIdleCallback` stub triggers hydration.
2. **Green** — runtime dispatcher reads the directive attribute, registers the right
   trigger per framework entry (`react.py`, `vue.py`, `svelte.py`, `solid.py`,
   `preact.py`).
3. **Green** — `frontend_route.py:133-147` (`_make_island_tag`) copies valid
   `client:*` attributes onto the `<ncc>` element.
4. **Green** — `client:only` → emit placeholder (`ssg.html.ts:32` already warns for
   client-only files).
5. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0.

## Definition of Done

- All five directives work on at least React + one other framework.
- Eager (default) still works — backward compatible.
- Astro's headline win reproduced: measurable drop in initial hydration JS/time.

## References

- Astro `astro-island.ts`, `idle.ts`, `visible.ts` — see
  [astro.md](../competitive/astro.md).
- Placeholder pattern exists: `nexy/frontend/scripts/ssg.html.ts:32`.