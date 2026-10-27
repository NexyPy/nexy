# Performance

What `nx start` does by default, what to switch on, and what was measured.

## Defaults

| Concern | Default | Change it |
|---|---|---|
| Processes | one Uvicorn worker per CPU on Linux and macOS, one on Windows | `nx start` runs the app through Uvicorn |
| Compression | off | `useGZip = {"minimum_size": 1000}` in [Config](../reference/config.md), or compress at the reverse proxy |
| Static files | served with `ETag` and `Last-Modified`, no `Cache-Control` | set long-lived caching at the reverse proxy or CDN for hashed bundles |
| HTML pages | rendered per request, no cache | [ISR](../rendering/isr.md) with `revalidate = N` |
| API docs | on | `useDocs = False` in production |
| Node at runtime | none | `nx build` pre-renders client components |

## Measured

A local run, one Uvicorn worker, Windows, Python 3.13, keep-alive connections from a Python load
generator on the same machine. Treat the numbers as a baseline for comparing changes, not as a
benchmark against other frameworks.

| Route | Concurrency | Requests per second | p50 | p99 |
|---|---|---|---|---|
| Bare FastAPI JSON route | 16 | ~4,500 | 3.4 ms | 5.1 ms |
| Nexy JSON route (`src/routes/api/ping.py`) | 16 | ~2,900 | 5.2 ms | 9.8 ms |
| Nexy SSR page (16 KB, 16 components) | 1 | ~500 | 1.9 ms | 3.0 ms |
| Nexy SSR page (16 KB, 16 components) | 64 | ~670 | 94 ms | 126 ms |

Reading the table:

- Nexy's own layers (path context, middleware) cost about a third of the throughput of a bare
  FastAPI route.
- A server-rendered page costs about 2 ms of CPU, spread over roughly 16 template renders (one per
  component). Pages with fewer components are proportionally cheaper.
- Throughput scales with workers. On Linux, `nx start` already starts one per CPU.

## Practical advice

1. Put Nginx, Caddy or your platform's edge in front: TLS, HTTP/2, Brotli and long-lived caching for
   `/__nexy__/client/` assets are their strengths. See [Deploy](README.md).
2. Use [ISR](../rendering/isr.md) for pages that change less than once a minute.
3. Hydrate lazily with [islands](../rendering/islands.md) so the first load ships less JavaScript.
4. Keep the number of `.nexy` components per page reasonable: each one is a separate template
   render.
5. Measure your own routes. A local load generator that keeps connections alive is enough to compare
   two versions of a page.

## Next steps

- [Deploy](README.md)
- [Rendering](../rendering/README.md)
- [Config](../reference/config.md)
