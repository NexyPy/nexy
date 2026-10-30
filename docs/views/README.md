# Views

A view renders the response body for a page. Choose one format and put the file under
`src/routes/`.

**Not sure? Write a `.nexy` file.** It needs no client framework, and you can add a React, Vue,
Svelte, Solid or Preact component inside it later, as an island.

```diagram filename="Which file for which page"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
Python endpoint              →  .py        (GET, POST, …)
```

## Formats

| Format | File | Server render | Client framework | Notes |
|---|---|---|---|---|
| `.nexy` | [.nexy files](nexy/README.md) | Jinja2 + Python logic, streamed | optional | Native Nexy page format |
| `.md` | [Markdown and MDX](nexy/markdown.md) | cmarkgfm at request time | optional via layout | Pure Markdown, GFM, layout-wrapped |
| `.mdx` | [Markdown and MDX](nexy/markdown.md) | framework SSR | React or Preact | Markdown with components |
| `.tsx` | [React](react/README.md), [Solid](solid/README.md) or [preact.md](preact.md) | framework SSR / SSG | React, Solid or Preact | Component routes |
| `.vue` | [Vue](vue/README.md) | framework SSR / SSG | Vue | SFC routes |
| `.svelte` | [Svelte](svelte/README.md) | framework SSR / SSG | Svelte | SFC routes |

Built-in `Image`, `Link`, `Audio`, `Video` and `Import` helpers: [Components](nexy/components.md).

## Enable a framework

Set `useFF` in `nexyconfig.py` and run `nexy new` to add dependencies:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

With a framework enabled, its extensions become active routes and Vite handles client bundles.

> [!NOTE]
> in [CSR](../rendering/csr.md) mode, only framework route files are navigable
> client-side.

## Layouts

A `layout.*` in a directory wraps pages below it. See [layouts](../routing/fbr/layouts/README.md).

## Next steps

- [.nexy files](nexy/README.md): Python + Jinja2 + props
- [Markdown and MDX](nexy/markdown.md): content pages
- [Components](nexy/components.md): built-in HTML helpers
