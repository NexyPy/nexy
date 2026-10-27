# File-based routing

A route is a file. The URL is the file path relative to `src/routes/`, minus the extension.

## File to URL

| File | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` maps to its directory, not to `/index`. A directory in parentheses is a **group**: it
organises files without appearing in the URL.

In client mode the page files are `.tsx`, `.vue` or `.svelte` instead of `.nexy`; the URL rules are
the same.

## Two modes

`useCSR` decides what the pages are. The two cannot be mixed in one project: Nexy refuses to start
when a server page sits next to a client route.

| Mode | Pages | Root layout | See |
|---|---|---|---|
| Server (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [Server mode and client mode](modes.md) |
| Client (`useCSR = True`) | framework files | `layout.tsx` | [layout.tsx](layouts/layout.tsx.md) |

`.py` files are API handlers in both modes.

## What is not a route

- Reserved filenames: `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`,
  `dependencies.py`, `middleware.py`, `__init__.py`.
- Files and folders starting with `_` or `.`: use them for partials and drafts.
- Extensions that are not active for your project. A file whose extension is inactive is skipped with
  a warning.

## One file per URL

Two files that resolve to the same URL both register. Do not create `blog.nexy` next to
`blog/index.nexy`, and do not mix `index.nexy` and `index.py` for the same path. Pick one.

## In this section

| Folder | What it covers |
|---|---|
| [pages/](pages/README.md) | pages, [dynamic routes](pages/dynamic-routes.md), route groups |
| [layouts/](layouts/README.md) | one page per layout file type |
| [handlers/](handlers/README.md) | `.py` handlers, validation and errors |
| [dependencies/](dependencies/README.md) | `dependencies.py`, guards |
| [middleware/](middleware/README.md) | `middleware.py` |
| [errors/](errors/README.md) | not-found and error pages |
| [navigation/](navigation/linking-and-navigating.md) | links, hooks |
| [realtime/](realtime/websocket.md) | WebSocket |
| [inheritance](inheritance.md) | the inheritance rules in one table |

## Next steps

- [Server mode and client mode](modes.md)
- [Layouts](layouts/README.md)
- [Modular routing](../modular/README.md)
