# 11 — Hydration · Islands Directives

## Objective

Implement Astro-style `client:load | idle | visible | media | only` directives for Nexy
islands, so hydration can be deferred or visibility-triggered instead of eager.

## Current state

- Islands runtime (`nexy/frontend/islands.py`) implements all five directives:
  `client:load` (default), `client:idle`, `client:visible`, `client:media`,
  `client:only`, plus `client:manual`.
- Every framework entry (`react.py`, `vue.py`, `svelte.py`, `solid.py`,
  `preact.py`) embeds `ISLANDS_RUNTIME` and wires `nexyIslands.init(document)` in
  its mount path; each `init()` defines `el.__nexyHydrate` per node and lets the
  runtime schedule hydration per directive. `client:only` is skipped everywhere.
- `NexyClientComponent` (`nexy/utils/imports/ncc.py`) accepts `directive` and
  `media` props and emits `data-nexy-island`, `data-nexy-directive`, and (for
  `client:media`) `data-nexy-media` onto the `<ncc>` element.
- Tests: `tests/unit/nexy/frontend/test_framework_islands.py`,
  `tests/unit/nexy/frontend/test_islands.py`,
  `tests/unit/nexy/utils/test_ncc_directive.py`.

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
   `preact.py`). **Done.**
3. **Green** — `frontend_route.py:133-147` (`_make_island_tag`) copies valid
   `client:*` attributes onto the `<ncc>` element. **Done** via
   `NexyClientComponent` (`directive`/`media` props).
4. **Green** — `client:only` → emit placeholder (`ssg.html.ts:32` already warns for
   client-only files). **Done** — `client:only` is skipped by every framework.
5. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0.

## Definition of Done

- All five directives work on at least React + one other framework. **Done — all five
  frameworks.**
- Eager (default) still works — backward compatible.
- Astro's headline win reproduced: measurable drop in initial hydration JS/time.

## References

- Astro `astro-island.ts`, `idle.ts`, `visible.ts` — see
  [astro.md](../competitive/astro.md).
- Placeholder pattern exists: `nexy/frontend/scripts/ssg.html.ts:32`.