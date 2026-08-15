# 11 — Hydration

## Objective

Move from eager `<ncc>` mounting to **selective hydration** with island directives,
following the Astro `astro-island` + `client:load/idle/visible/media/only` model. Today
every component mounts at `DOMContentLoaded`; islands should be deferred or
visibility-triggered to cut initial JS and improve Lighthouse.

## Current state (verified)

- `<ncc>` container carries server HTML + `data-nexy-*` props, then is hydrated eagerly
  (`nexy/compiler/frontend_route.py:133-147`, `nexy/frontend/react.py:24-50`).
- React entry: `hydrateRoot` always (`react.py:77`), Vue `createApp(...).mount` always
  (`vue.py:72-73`), etc.
- No directive attributes (`client:idle`, `client:visible`...).

## Competitive anchor

- Astro `astro-island` custom element + directives:
  - `client:load` → hydrate on `load` event.
  - `client:idle` → `requestIdleCallback` (`idle.ts`).
  - `client:visible` → `IntersectionObserver` (`visible.ts`).
  - `client:media` → `matchMedia`.
  - `client:only` → client-only, no SSR HTML.

## Target

- `<ncc>` gains a `client:directive` attribute (or a data attribute consumed by the
  runtime).
- The `<ncc>` runtime (`react.py` / `vue.py` / `svelte.py` / `solid.py` / `preact.py`)
  honors the directive instead of mounting at `DOMContentLoaded`.
- Reuse the existing `__nexy_import` for lazy module loading
  (`nexy/frontend/__init__.py:132-159`).

## TDD phases

1. **Red** — test: `<ncc client:idle>` is not hydrated on `DOMContentLoaded`; hydrated
   on `requestIdleCallback`.
2. **Green** — runtime respects `client:idle`/`load`/`visible`/`media`/`only`.
3. **Green** — `<ncc>` generator (`frontend_route.py:136-147`) passes through the
   directive attribute.
4. **Green** — `client:only` skips server HTML, emits placeholder.
5. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0, Lighthouse FCP delta.

## Definition of Done

- `client:idle` island hydrates after idle; `client:visible` hydrates on IntersectionObserver;
  `client:only` emits a `<div id="x-root">` placeholder (`ssg.html.ts:32` pattern already
  exists).
- Eager default unchanged for backward compatibility.
- Measurable reduction in hydration work on a mixed page.

## References

- [Astro analysis](../competitive/astro.md) — `astro-island`, `idle.ts`, `visible.ts`.
- [11-hydration README](./README.md) — parent.
- Sub-detail in [islands-directives](./islands-directives/README.md).