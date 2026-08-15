# 09 — SSR Pipeline

## Objective

Nexy renders server-side HTML with **synchronous Python functions** returning a complete
string. This is a strength (startup) but a weakness: zero streaming means no TTFB win
on dynamic pages. The first optimization is to unlock selective streaming of the HTML
shell before the body, matching the Next.js Fizz model.

## Current state (verified)

- `nexy/routers/fbrouter/__init__.py:99-121` (`_make_request_handler`) — awaits the
  component, returns `HTMLResponse` (fully buffered).
- Components are sync Python `def Page(...) -> str` — the entire string is produced
  before the response starts.
- `nexy/core/config.py:27` — `ROUTE_FILE_EXTENSIONS` enables `.py`, `.nexy`, `.tsx`...
  all uniformly; no notion of streaming boundary.

## Competitive target

- Next.js: `chainStreams`/`continueFizzStream` flush the HTML shell first, then the body
  (`app-render.tsx`). `createDocumentClosingStream` closes the document.
- Nuxt: streaming is experimental (`nuxt#4753`).
- Astro: `server:defer` islands stream in post-shell.

## TDD phases

1. **Red** — test: a page whose head renders faster than its body emits the head bytes
   first on the wire (response is a stream, not a complete string).
2. **Green — stream wrapper** — `HTMLResponse` subclass / ASGI `StreamingResponse` from
   an iterable yielded by a component that supports generators.
3. **Green — shell split** — flush `<head>` + opening `<body>` before invoking the
   component body; component can yield body chunks.
4. **Refactor** — keep sync `-> str` components working unchanged; only generator
   components get streamed.
5. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0.

## Definition of Done

- Sync `-> str` pages still work (backward compatible).
- Generator-capable components stream head first on ASGI (Uvicorn).
- Measurable TTFB improvement on a body-heavy page.

## References

- [Next.js analysis](../competitive/nextjs.md) — Fizz streaming (§3).
- [Astro analysis](../competitive/astro.md) — `server:defer`.
- Sub-epic streaming detail in [streaming-ssr](./streaming-ssr/).

---

### Streaming SSR (sub-epic)

See [./streaming-ssr/README.md](./streaming-ssr/README.md).