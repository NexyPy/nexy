# 10 — Data Layer · Loaders

## Objective

Typed GET data loading per route — resolved before server render and available to the
client router — mirroring the Remix loader model.

## Current state

- Route data is only the `@Action` POST path (`nexy/decorators.py:411`).
- No per-route loader function in `.nexy` / `.py` / `.tsx` route files.

## Target

- A route file may export a `loader` callable:
  ```python
  # routes/blog.py
  from dataclasses import dataclass
  @dataclass
  class BlogData:
      posts: list[Post]

  def loader() -> BlogData: ...
  ```
- Server: `loader()` is invoked during render; result is JSON-serialized into
  `data-nexy-props` on the route's output (reuses `frontend_route.py` channel at
  `nexy/compiler/frontend_route.py:133-147`, client parse at
  `nexy/frontend/react.py:30-38`).
- Client router: calls `GET /<route>.data` (single-fetch style) to get only the loader
  payload before rendering.

## TDD phases

1. **Red** — test: route with `loader()` → component receives typed result as a prop.
2. **Green** — loader resolved in `_make_request_handler`
   (`fbrouter/__init__.py:99-121`); result merged into component props.
3. **Green** — generate a `.data` endpoint per loadable route (Remix `.data` convention).
4. **Green** — client router fetches `.data` on navigation without full HTML.
5. **Gates** — ruff, mypy --strict, pytest, `nexy build` EXIT=0.

## Definition of Done

- A `@Loader`-style `loader()` runs on server before render; typed.
- Initial HTML contains the data in `data-nexy-props`.
- Client navigation hits `<route>.data` and returns JSON only.
- Existing `@Action` POST routes unchanged.

## References

- [Remix analysis](../competitive/remix.md) — single-fetch `.data`,
  `throwIfPotentialCSRFAttack`, `skipRevalidation`.
- [10-data-layer README](./README.md) — parent epic.