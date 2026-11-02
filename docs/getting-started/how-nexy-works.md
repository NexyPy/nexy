# How Nexy works

The mental model in one page: what Nexy builds, what Vite builds, and what happens between a file
and a page in your browser. Read it once; the rest of the documentation is then a set of details.

## The Nexy architecture

A request crosses five layers: Uvicorn accepts it, middleware decorates it, the router picks a file,
the renderer turns that file into HTML or JSON, and the client layer takes over if the page has
JavaScript. Nexy owns the middle three; Vite and your framework own the client; your application
owns the data, the authentication and the authorisation.

Each layer, and what it refuses to do, is in [Architecture](../architecture.md). For the packages of
Nexy itself, see `ARCHITECTURE.md` at the repository root - it is written for contributors.

## The application lifecycle

`nx dev` does six things before the first request:

1. validates `nexyconfig.py`, and stops on an invalid config;
2. ensures the project's Python packages are importable;
3. resolves the ports, and deletes the stale `__nexy__/nexy.prod` marker;
4. generates the client files and compiles the routes, in parallel;
5. starts Vite and waits until it answers;
6. installs the file watcher, then lets uvicorn import `nexy.modules.routers.app:_server`.

That import assembles the application - middleware, Actions, routers, error handlers - and the
first request is served by that assembly. When you save, the watcher restarts uvicorn; a page that
appeared, disappeared or moved also regenerates the client route list.

## The routing system

A path under `src/routes/` becomes a URL by four rules:

| File | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

The extension never appears; `index` is the route of its folder; a folder in parentheses groups
files without adding a segment.

When two things can answer the same URL, **the first one registered wins**, and Nexy always
registers in this order:

1. the Actions endpoint;
2. static files: `/public`, `/assets`, `/favicon.ico`;
3. a modular `APIRouter` (`useRouter`);
4. file routes, most specific first: static paths, then dynamic paths with the most fixed segments,
   then catch-alls.

Two file routes of equal specificity are registered in alphabetical path order, so `[id].nexy`
answers before `[slug].nexy`. A modular route therefore beats a page with the same path. This is a
precedence order you can rely on, not a tie-break rule to play with: give one URL one file.

## The view system

The extension of a file decides what it is, and the project config decides which extensions are
active.

| Extension | Active when | Compiled by | Served as |
|---|---|---|---|
| `.nexy` | server mode | Nexy: frontmatter becomes Python, the markup becomes Jinja2 | a page |
| `.md` | always | Nexy: GitHub-flavoured Markdown, heading ids, table of contents | a page, inside the nearest layout |
| `.mdx` | always | Vite, with React or Preact | a component route |
| `.tsx` | `useFF` is React, Solid or Preact | Vite and the framework | a component route |
| `.vue` | `useFF` is Vue | Vite and Vue | a component route |
| `.svelte` | `useFF` is Svelte | Vite and Svelte | a component route |
| `.py` | always | Python | an API handler: `GET`, `POST`, ... are the methods |

A file whose extension is not active is skipped with a warning, not served. In client mode, `.nexy`
is rejected before the server starts. See [File conventions](../reference/file-conventions.md).

## The rendering lifecycle

Three questions decide everything a reader notices:

| Question | Answer | Page |
|---|---|---|
| Who produces the HTML? | the server, or the browser for a client route | [Rendering](../rendering/README.md) |
| When is the data read? | on each request, on each regeneration, or in the browser | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| When does JavaScript arrive? | only for an island, or for the whole document | [Islands](../rendering/islands.md), [CSR](../rendering/csr.md) |

In server mode the server renders each page, `revalidate` caches one page per URL, and islands add
JavaScript to one component. In client mode the first document is rendered in Node and navigation
then happens in the browser.

`__nexy__/` holds everything generated: compiled pages, the client entry, the build output. Never
edit it, never commit it; delete it to force a clean build.

## The frontend integration

**Vite does not replace Nexy.** Vite bundles and serves client code. It does not route a request,
render a `.nexy` page, run an Action or own the origin. The browser talks to one origin - Nexy's -
and in development Nexy proxies Vite's endpoints through it, so there is no CORS to configure.

**Nexy does not replace React.** Nexy decides which component renders, when, and with which props;
the framework owns the component model, the reactivity and the ecosystem. A `.nexy` page imports a
component as an island; in client mode a route *is* a component.

For a component route, Python writes only a thin wrapper module that points at the file. The
compilation and the server-side rendering are Vite's job.

## Development and production

| | `nx dev` | `nx build` then `nx start` |
|---|---|---|
| Pages | compiled when you save | compiled once, ahead of time |
| Client code | Vite dev server with hot reload, behind Nexy's own origin | bundle in `__nexy__/client/`, pre-rendered HTML |
| Node.js | runs next to Python | not needed to serve |
| Errors | overlay in the browser, toolbar on every page | status pages without details |
| Origin | one port, `3000` | one port |

What does not change: the same routing rules, the same page files, the same `nexyconfig.py`. A page
that behaves differently between the two is a bug, not a mode.

## Going deeper

- [Project structure](project-structure.md): every folder of a project
- [Rendering](../rendering/README.md): SSR, ISR, CSR and islands
- [Frontend](../guides/frontend.md): Vite, styling and the client build
- [Routing](../routing/README.md): the file-based, modular and custom routers
