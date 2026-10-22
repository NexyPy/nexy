# 09 — SSR Pipeline · Streaming SSR

## Objective

Stream the HTML shell before the body to reduce TTFB, following the Next.js
`chainStreams`/`createDocumentClosingStream` model. Only applies to async-capable
components; synchronous `-> str` components remain buffered for backward compatibility.

## Current state

- `_make_request_handler` (`fbrouter/__init__.py:113-139`) wraps every component in a
  `StreamingResponse`; `_stream_body` (L101-110) turns a plain string into a single
  chunk (byte-identical to the old buffered `HTMLResponse`) and streams generator
  components chunk-by-chunk as produced.
- Tests: `tests/unit/nexy/routers/test_streaming_response.py` covers single-chunk
  sync output, multi-chunk generator output, and type of the response.

## Target architecture

```
ASGI stream
  ├─ flush <head> + layout opening
  ├─ component body generator  ──►  yield chunks
  └─ flush <body/> close + </html>
```

The generator path is implemented (component yields chunks). An explicit
shell/head-before-body flush (Next.js `chainStreams` split inside the wrapper)
is not yet a separate concern — the component decides chunk boundaries.

## TDD phases

1. **Red** — test: generator component yields head before body; client receives head
   bytes first. **Done** (`test_streaming_response.py`).
2. **Green** — `StreamingHTMLResponse` iterable wrapping a component that may be a
   generator; head flush before body. **Done** via `_make_request_handler` +
   `_stream_body`.
3. **Green** — `createDocumentClosingStream` equivalent that emits the closing tags.
   **Partial** — generator can yield closing tags; no dedicated closing-stream
   helper.
4. **Refactor** — sync `-> str` components wrapped into a single-chunk stream (no
   behavior change). **Done.**
5. **Gates** — ruff, mypy, pytest, `nexy build` EXIT=0.

## Definition of Done

- Sync pages: identical output, EXIT=0.
- Generator pages: head streamed before body on Uvicorn; measurably lower TTFB.
- Backward compatible with existing `.nexy`/`.py` routes.

## References

- Next.js `chainStreams`/`continueFizzStream` (`app-render.tsx`).
- [Route-tree README](../08-route-tree/README.md) — streaming pairs with the shared
  manifest so the client knows which segments are still arriving.