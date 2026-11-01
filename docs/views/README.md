# Views

Before choosing a file format, it is important to distinguish between how Nexy handles resources and how it renders them.

| Term | Definition |
|---|---|
| **Page** | An URL-addressable resource of the application. It is defined by a file under `src/routes/`. |
| **View** | The process of producing the response body for a page. A view transforms logic and data into HTML or JSON. |
| **Component** | A reusable UI building block used to compose a view. Components can be native Nexy helpers or framework-specific (React, Vue, etc.). |
| **Route handler** | A Python function that handles an HTTP request for a specific method (e.g., `GET`, `POST`). |
| **Endpoint** | The unique combination of a URL and an HTTP method that a route handler answers. |

**Not sure? Write a `.nexy` file.** It needs no client framework, and you can add a React, Vue, Svelte, Solid or Preact component inside it later, as an island.

```diagram filename="Which file for which page"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## Formats

| Format | File | Server render | Client framework | Notes |
|---|---|---|---|---|
| `.nexy` | [.nexy files](nexy/README.md) | Jinja2 + Python logic, streamed | optional | Native Nexy page format |
| `.md` | [Markdown and MDX](nexy/markdown.md) | cmarkgfm at request time | optional via layout | Pure Markdown, GFM, layout-wrapped |
| `.mdx` | [Markdown and MDX](nexy/markdown.md) | framework SSR | React or Preact | Markdown with components |
| `.tsx` | [React](react/README.md), [Solid](solid/README.md) or [Preact](preact/README.md) | client mode: the framework, rendered in Node | React, Solid or Preact | Component routes |
| `.vue` | [Vue](vue/README.md) | client mode: the framework, rendered in Node | Vue | SFC routes |
| `.svelte` | [Svelte](svelte/README.md) | client mode: the framework, rendered in Node | Svelte | SFC routes |

Built-in `Image`, `Link`, `Audio`, `Video` and `Import` helpers: [Components](nexy/components.md).

## Mixing formats

You can mix different technologies within the same project:
- **Islands**: You can import a React or Vue component inside a `.nexy` page. The server renders the shell, and the framework hydrates the component on the client.
- **Shared Logic**: Route handlers in `.py` files can provide data to pages in any format via the shared application state or API calls.

## Enable a framework

Set `useFF` in `nexyconfig.py` and run `nexy new` to add dependencies:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

With a framework enabled, Vite handles its client bundles. In client mode its extensions become
routes; in server mode the same files are components you import as islands - a framework file under
`src/routes/` is rejected there. See [server mode and client mode](../routing/fbr/modes.md).

> [!NOTE]
> in [CSR](../rendering/csr.md) mode, only framework route files are navigable
> client-side.

## Layouts

A `layout.*` in a directory wraps pages below it. See [layouts](../routing/fbr/layouts/README.md).

## Next steps

- [.nexy files](nexy/README.md): Python + Jinja2 + props
- [Markdown and MDX](nexy/markdown.md): content pages
- [Components](nexy/components.md): built-in HTML helpers
