# File conventions

Reserved names and rules under `src/routes/`.

## Route files

| File | Becomes |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | the route of its directory |
| `about.nexy` | `/about` |
| `[slug].nexy` | dynamic segment `{slug}` |
| `[...path].nexy` | catch-all `{path:path}` |
| `(group)/page.nexy` | `/page`: the group does not appear in the URL |
| `name.py` | API handler; function names `GET`, `POST`, ... are the methods |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | client route when the framework is enabled with `useFF` |

## Reserved files

| File | Role | Details |
|---|---|---|
| `layout.nexy` | server mode: wraps every page below it; the root one owns the HTML document | [layout.nexy](../routing/fbr/layouts/layout.nexy.md) |
| `layout.tsx` | client mode (React): the root one owns the HTML document, nested ones wrap pages | [layout.tsx](../routing/fbr/layouts/layout.tsx.md) |
| `layout.vue`, `layout.svelte` | client mode: nested layouts | [layout.vue](../routing/fbr/layouts/layout.vue.md), [layout.svelte](../routing/fbr/layouts/layout.svelte.md) |
| `notfound.nexy` | 404 page for its directory | [Error pages](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 page for its directory | [Error pages](../routing/fbr/errors/README.md) |
| `loading.nexy` | reserved; no runtime effect yet | [Error pages](../routing/fbr/errors/README.md) |
| `middleware.py` | an `async def middleware(request, call_next)` wrapping the requests of the directory and below | [Middleware files](../routing/fbr/middleware/README.md) |
| `dependencies.py` | a `dependencies = [fn, ...]` list applied to the directory and its children | [Dependencies](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python package marker | |
| `favicon.ico` | served at `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions` and `useLoadingExtensions`
reserve more extensions for these names. See [Config](config.md).

## Ignored files

- A file or folder starting with `_` or `.`: use it for partials, drafts and helpers.
- A file whose extension is not active for the project: it is skipped with a warning.

## One file per URL

Two files that resolve to the same URL both register. Do not put `blog.nexy` next to
`blog/index.nexy`.

## Outside `src/routes/`

| Folder | Purpose |
|---|---|
| `src/components/` | components imported by pages; never routes |
| `src/apps/` | controllers and modules of the [modular router](../routing/modular/README.md) |
| `public/` | static files, served at the root: `public/logo.svg` is `/logo.svg` (also under `/public/`) |
| `__nexy__/` | generated output; do not commit |

## Next steps

- [Routing](../routing/README.md)
- [Project structure](../getting-started/project-structure.md)
