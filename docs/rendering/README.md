# Rendering

Nexy renders a page on the server by default and hydrates the interactive parts in the browser.

| Mode | Where the HTML comes from | Enabled by |
|---|---|---|
| [SSR](ssr.md) | the server, on every request | default |
| [ISR](isr.md) | the server, cached with stale-while-revalidate | `revalidate = N` in a `.nexy` page |
| [CSR](csr.md) | the browser, after the first load | `useCSR = True` in `nexyconfig.py` |
| [Islands](islands.md) | the server, hydrated on demand | `directive` prop on a client component |

## Which one

- **Content and marketing pages**: SSR, plus ISR when the content changes rarely.
- **Mostly static page with one interactive widget**: SSR with an [island](islands.md) that
  hydrates when visible.
- **App-like navigation (dashboards, editors)**: CSR with React, Vue, Svelte, Solid or Preact
  routes.

Server rendering, ISR and islands belong to server mode, where `layout.nexy` owns the HTML
document. CSR is client mode, where the root `layout.tsx` does. A project is in one mode: see
[Server mode and client mode](../routing/fbr/modes.md) and
[Layouts](../routing/fbr/layouts/README.md).

## Next steps

- [SSR](ssr.md)
- [Islands](islands.md)
- [Performance](../deployment/performance.md)
