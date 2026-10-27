# SSR (server rendering)

By default, Nexy renders pages on the server for each request. No flag is required.

## What each file type does

| Route | Rendering |
|---|---|
| `.nexy` | compiled to a Python module, rendered with Jinja2 per request |
| `.md` | rendered by `cmarkgfm` at request time, wrapped in the nearest layout |
| `.tsx`, `.jsx`, `.vue`, `.svelte`, `.mdx` | server-rendered by the framework; at `nx build`, pre-rendered to static HTML |
| `.py` | returns JSON or a `Response` directly, not an HTML page |

HTML can be streamed when possible.

> **Good to know**: autoescaping is off in `.nexy` templates. Use `| e` on untrusted values.

API errors such as `500` are rendered by `errors.nexy` when that file exists - see
[error pages](../routing/fbr/pages/README.md#error-pages).

## Next steps

- [ISR](isr.md): cache a page per path with stale-while-revalidate
- [CSR](csr.md): navigate on the client after the first load
- [Views](../views/README.md): choose a page format
