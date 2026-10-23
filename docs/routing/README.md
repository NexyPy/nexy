# Routing

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

## What is not a route

- Reserved filenames: `layout.nexy`, `loading.nexy`, `errors.nexy`, `notfound.nexy`,
  `dependencies.py`, `__init__.py`.
- Files and folders starting with `_` or `.`: use them for partials and drafts.
- Extensions that are not active for your project. Without a client framework a route is `.nexy`,
  `.md`, `.mdx` or `.py`; configuring `useFF` adds that framework's extensions (`.tsx` and `.jsx`
  for React, `.vue`, `.svelte`). A file whose extension is inactive is skipped with a warning.

## One file per URL

Two files that resolve to the same URL both register. Do not create `blog.nexy` next to
`blog/index.nexy`, and do not mix `index.nexy` and `index.py` for the same path. Pick one.

## Choose a router

| Router | Source | Enabled by |
|---|---|---|
| File-based (FBR) | every file under `src/routes/` | the directory exists |
| Modular | controllers and modules | `useRouter = AppModule` in `nexyconfig.py` |

They coexist. FBR is scanned whenever `src/routes/` exists, even with a modular router mounted.

## Next steps

- [Pages](pages.md): dynamic segments, layouts, error pages
- [Hooks](hooks.md): read the path, query, cookies and session inside a page
- [Rendering: SSR](fbr/ssr.md), [CSR](fbr/csr.md), [ISR](fbr/isr.md)
- [WebSocket handlers](fbr/websocket.md)
- [Modular routing](modular.md)
- [Views](../views/README.md): what goes inside the files
