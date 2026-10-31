# Rendering

Rendering answers one question: **who produces the HTML, and when**. Nexy has four answers and one
default.

**Not sure? Keep SSR.** Change a page only when you can name the reason: content that rarely changes
(ISR), one widget that needs the browser (island), or app-like navigation (CSR).

## How it works

```diagram filename="Who produces the HTML, and when"
SSR       request ──► server renders ────────────────► HTML ──► browser
ISR       request ──► cached HTML? ──► browser, regenerated in the background
CSR       request ──► document rendered by the server ──► browser takes over navigation
Islands   request ──► server renders the page ──► one widget hydrates on demand
```

## The four modes

| | SSR | ISR | CSR | Islands |
|---|---|---|---|---|
| Data is read | on every request | on each regeneration | in the browser | on every request |
| The HTML comes from | the server | the server, then a cache | the server for the first document, the browser afterwards | the server |
| JavaScript | only for islands | only for islands | the framework bundle | only the island |
| Hydration | none | none | the whole document | the island |
| Cache | none | per URL, in memory | none | none |
| Decided by | default | `revalidate = N` in the page | `useCSR = True` in the project | `directive` on the component |
| Grain | page | page | **project** | component |

## Rendering lifecycle

Two facts explain most surprises.

1. **A project is in one mode.** `useCSR` chooses between server mode (SSR, ISR, islands, `.nexy`,
   `.md`, `.mdx` routes) and client mode (framework routes and a client router). The two cannot be
   mixed: see [server mode and client mode](../routing/fbr/modes.md).
2. **Inside server mode, the mode is per page.** One page can be cached with `revalidate`, another
   can hold an island, a third can do neither.

Client mode still sends a real document: Nexy renders it in Node for the first response, then the
browser takes over navigation. A CSR page is not a blank page waiting for a bundle.

## When to use

- **Content, marketing, documentation**: SSR, plus ISR when the content changes rarely.
- **A mostly static page with one interactive widget**: SSR with an island.
- **Dashboards, editors, app-like navigation**: CSR.
- **A page read constantly and changed rarely**: ISR.

## Configuration

| Mode | Where |
|---|---|
| SSR | nowhere: it is the default |
| ISR | `revalidate = 60` in the frontmatter of a `.nexy` page |
| CSR | `useCSR = True` in `nexyconfig.py`, with `useFF` set |
| Islands | `directive="client:visible"` on the component tag |

## Example

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

The same page without the frontmatter line is SSR.

## Limitations

- **There is no SSG mode.** Nexy prerenders HTML at build time (component HTML, client documents),
  but always reads it back through the server: no export command, no standalone folder to host
  statically. For frozen content, use ISR with a long window.
- **ISR is not a CDN.** The cache lives in the process that renders the page; several workers keep
  several caches. See [ISR](isr.md).
- **CSR is a project decision.** You cannot make one page CSR and keep the rest SSR.
- **Islands hydrate the island, not the page.** A page whose islands all depend on each other is a
  CSR page in disguise.

## Next steps

- [SSR](ssr.md): the default
- [ISR](isr.md): cache a page per URL
- [CSR](csr.md): hand navigation to the browser
- [Islands](islands.md): hydrate one widget
- [Performance](../deployment/performance.md)
