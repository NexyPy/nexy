# 12 — Dev & HMR · Browser Error Overlay

## Objective

Display compile errors in the **browser** (like Vite's red box), not only in the
terminal. This is claimed by the README ("Browser error overlay for compilation
failures") but is currently unimplemented.

## Current state

- `nexy/runtime/hmr.py` (`hmr.py:6-33`) — `HMRManager` with `_send` (`hmr.py:27`) that
  hardcodes `{"type": "nexy:reload", ...}` and `broadcast_reload` (`hmr.py:33`).
  **No `broadcast_error` method.**
- `nexy/vite.py:62-68` — client WS: `if (data.type === 'nexy:reload')` and swaps body
  when `X-Nexy-HMR` is set. **No error case in the browser.**
- `nexy/utils/dev/watcher.py` — on compile error prints to console, no WS broadcast.

## Target

```
watcher.py (compile error) ──broadcast_error──► WS ──► browser runtime
                                                              │
                                                              ▼
                            overlay.ts (iframe or DOM) renders red box
```

## TDD phases

1. **Red** — test: `HMRManager.broadcast_error` emits a message `{"type":"nexy:error",
   "errors":[...]}` (use `tests/unit/nexy/runtime/test_hmr.py` capture stub pattern).
2. **Green** — `hmr.py`: add `broadcast_error(errors)` parallel to `broadcast_reload`.
3. **Green** — `watcher.py`: on `NexyCompileError`, call `HMRManager().broadcast_error`
   instead of only `console.print`.
4. **Green** — `runtime.ts`: handle `data.type === 'nexy:error'` → inject a DOM overlay
   (or iframe, like Vite's `vite-error-overlay`).
5. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0.

## Definition of Done

- A syntax error in a `.nexy`/`.mdx`/`.py` route shows an in-browser overlay during
  `nx dev`.
- Terminal still logs the error.
- `broadcast_error` covered by unit tests (≥1 assertion via the capture stub).
- Existing `broadcast_reload` behavior unchanged.

## References

- Vite error overlay (`vite/client` `error` event + `@vite/client` overlay).
- Next.js dev-validation-worker for error propagation model.
- Template message contract mirrors Next `NEXT_HMR_REFRESH_HEADER` refresh path
  (see [nextjs analysis](../competitive/nextjs.md) §8).