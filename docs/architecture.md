# Architecture

## Definition

Nexy is five layers, and each one has a job the others do not do. Knowing the boundary answers most
"why does it work like that" questions: a slow page is a renderer question, a wrong page is a router
question, a page that never appears is a client question.

This page is for people writing an application. The packages of Nexy itself, and the mechanisms
behind them, are described in `ARCHITECTURE.md` at the repository root, for contributors.

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

The rule behind the table: **Nexy builds what it owns, and never compiles what Vite compiles.** For
a component route, Python writes a thin wrapper module that points at the file.

## Where a request is decided

1. Middleware runs, and may change the request or stop it.
2. The router picks one file, and the layouts around it.
3. The renderer runs that file with the data it reads itself.
4. The response goes back, and the client layer takes over if the page has JavaScript.

Each step, with the exact precedence between routers and the order of `nx dev`, is in
[How Nexy works](getting-started/how-nexy-works.md). This page does not repeat it.

## Development and production

The same five layers, assembled twice:

| Layer | `nx dev` | `nx build` then `nx start` |
|---|---|---|
| Compiler | runs when you save | runs once, ahead of time |
| Vite | dev server, hot reload, proxied through Nexy's origin | bundle written to `__nexy__/client/`, no dev server |
| Node | renders client documents on demand | renders them at build, not while serving |
| Watcher | restarts uvicorn on change | absent |
| Origin | one port | one port |

What changes is *when* work happens, not *who* does it. A page that behaves differently between the
two is a bug in the page, not a property of the mode.

## Boundaries

Nexy stops at the edge of your application, on purpose:

| Concern | What Nexy provides | What you write |
|---|---|---|
| Authentication | session middleware, `AuthenticationMiddleware` when enabled | the login, the user lookup, the cookie policy |
| Authorisation | `dependencies.py`, guards, per-folder inheritance | the rule itself |
| Database | nothing: no ORM, no migrations | the model layer ([Databases](guides/databases.md)) |
| Internationalisation | nothing for your pages; only the CLI is translated | the library and the messages ([i18n](guides/i18n.md)) |
| Background jobs | nothing: no queue, no scheduler | a worker process |
| Email, payments, search | nothing | the service you choose |

The reason is the same for all six: a framework that picks your ORM or your auth library decides
things only your application can decide. The cost is explicit: nothing is wired for you, and the
guide pages above say where to plug each one in.

## Next steps

- [How Nexy works](getting-started/how-nexy-works.md): one request, step by step
- [Project structure](getting-started/project-structure.md): where each layer lives in a project
- [Routing](routing/README.md): the three routers, and how to choose
- [Rendering](rendering/README.md): where the HTML comes from
