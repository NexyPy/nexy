# 09 — SSR Pipeline · Streaming SSR

## Objective

Stream the HTML shell before the body to reduce TTFB, following the Next.js
`chainStreams`/`createDocumentClosingStream` model. Only applies to async-capable
components; synchronous `-> str` components remain buffered for backward compatibility.

## Current state

- All HTML produced via `HTMLResponse` (`fbrouter/__init__.py:10` import, L371/L394)
  with fully materialized strings.
- `_make_request_handler` (`fbrouter/__init__.py:99-121`) calls the sync component and
  returns the response in one shot.

## Target architecture

```
ASGI stream
  ├─ flush <head> + layout opening
  ├─ component body generator  ──►  yield chunks
  └─ flush <body/> close + </html>
```

## TDD phases

1. **Red** — test: generator component yields head before body; client receives head
   bytes first.
2. **Green** — `StreamingHTMLResponse` iterable wrapping a component that may be a
   generator; head flush before body.
3. **Green** — `createDocumentClosingStream` equivalent that emits the closing tags.
4. **Refactor** — sync `-> str` components wrapped into a single-chunk stream (no
   behavior change).
5. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0.

## Definition of Done

- Sync pages: identical output, EXIT=0.
- Generator pages: head streamed before body on Uvicorn; measurably lower TTFB.
- Backward compatible with existing `.nexy`/`.py` routes.

## References

- Next.js `chainStreams`/`continueFizzStream` (`app-render.tsx`).
- [Route-tree README](../08-route-tree/README.md) — streaming pairs with the shared
  manifest so the client knows which segments are still arriving.