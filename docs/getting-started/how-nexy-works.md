# How Nexy works

What happens between a file you write and the page in the browser: the layers a request crosses, who
builds what, and what Nexy leaves to your application. You do not need this page to start; it
answers the "why does it work like that" questions later.

## The layers

```diagram filename="One request, five layers"
Browser
   │
   ▼
Uvicorn ───── ASGI transport
   │
   ▼
Middleware ── sessions, CORS, gzip, trusted hosts, your own
   │
   ▼
Router ────── FBR | Modular | Custom ── picks the file that answers
   │
   ▼
Renderer ──── HTML (Jinja2, Markdown, Node) or JSON
   │
   ▼
Response
```

| Layer | Responsibility | Does not |
|---|---|---|
| Uvicorn | accept the connection, speak ASGI | know what a page is |
| Middleware | decorate the request: session, CORS, gzip, trusted hosts, HTTPS redirect, yours | choose a route |
| Router | match the URL to a file, with its layouts, dependencies and error pages | produce content |
| Renderer | run the page and turn its result into HTML or JSON | fetch your data |
| Client | Vite and your framework: bundles, hydration, client navigation | answer a server request |

## Who builds what

| Actor | Owns | Does not own |
|---|---|---|
| Nexy | routing, server rendering, Actions, `.nexy` compilation, one origin | components, reactivity, data |
| Vite | client bundles, the dev server, hot reload | routing, server rendering, Actions |
| Your framework | components, reactivity, the ecosystem | routing, the document (Nexy asks its layout for it) |
| Your application | data, authentication, authorisation, business rules | transport, rendering |

The rule behind the table: **Nexy builds what it owns, and never compiles what Vite compiles.**

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

`nx dev` checks `nexyconfig.py`, compiles the pages, starts Vite when the project has a frontend
framework, and restarts the server when you save. `nx build` does the same work once, ahead of
time, and `nx start` serves the result.

| | `nx dev` | `nx build` then `nx start` |
|---|---|---|
| Pages | compiled when you save | compiled once, ahead of time |
| Client code | Vite dev server with hot reload, behind Nexy's own origin | bundle in `__nexy__/client/`, pre-rendered HTML |
| Node.js | runs next to Python | not needed to serve |
| Errors | overlay in the browser, toolbar on every page | status pages without details |
| Origin | one port, `3000` | one port |

What does not change: the same routing rules, the same page files, the same `nexyconfig.py`. A page
that behaves differently between the two is a bug, not a mode.

## What Nexy leaves to you

Nexy stops at the edge of your application, on purpose:

| Concern | What Nexy provides | What you write |
|---|---|---|
| Authentication | session middleware, `AuthenticationMiddleware` when enabled | the login, the user lookup, the cookie policy |
| Authorisation | `dependencies.py`, guards, per-folder inheritance | the rule itself |
| Database | no ORM of its own; `nx new` can scaffold SQLModel, SQLAlchemy or Tortoise, `nx migrate` runs Alembic or Aerich | the models and the queries ([Databases](../guides/databases.md)) |
| Internationalisation | nothing for your pages; only the CLI is translated | the library and the messages ([i18n](../guides/i18n.md)) |
| Background jobs | nothing: no queue, no scheduler | a worker process |
| Email, payments, search | nothing | the service you choose |

The reason is the same for all six: a framework that picks your ORM or your auth library decides
things only your application can decide. The cost is explicit: nothing is wired for you, and the
guides linked in the table say where to plug each one in.

## Next steps

- [Project structure](project-structure.md): where each part lives in a project
- [Routing](../routing/README.md): the file-based, modular and custom routers
- [Rendering](../rendering/README.md): SSR, ISR, CSR and islands
- [Frontend](../guides/frontend.md): Vite, styling and the client build
