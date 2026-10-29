# How Nexy works

The mental model in one page: what Nexy builds, what Vite builds, and what happens between a file
and a page in your browser.

## A file is a route

A file under `src/routes/` is a page or an endpoint, and its path is its URL. `about.nexy` is
`/about`, `[slug].nexy` is `/blog/<anything>`, `api/users.py` answers `/api/users`. There is no route
table to write. See [File conventions](../reference/file-conventions.md).

## Two builders, one rule

Nexy builds what it owns. Vite builds what belongs to the frontend. The Python side never compiles
what Vite compiles.

| File | Built by | What the server does with it |
|---|---|---|
| `.nexy` | Nexy: frontmatter becomes a Python function, the template becomes Jinja2 | runs the function on each request and renders HTML |
| `.md` | Nexy: GitHub-flavoured Markdown, heading ids, table of contents | renders HTML inside the nearest layout |
| `.tsx`, `.jsx`, `.vue`, `.svelte` | Vite and the framework | serves the pre-rendered HTML, then the framework takes over in the browser |
| `.mdx` | Vite (React or Preact) | same as a framework page |
| `.py` | Python | an API handler: `GET`, `POST`, ... are the methods |

For a framework page Python writes only a thin wrapper module that points at the file. The build and
the server-side rendering are done by Vite and the scripts shipped with Nexy.

## One request

```diagram filename="From a URL to an answer"
Browser
   │  GET /blog/hello
   ▼
Middleware ── sessions, CORS, trusted hosts
   │
   ▼
Router ───── finds src/routes/blog/[slug].nexy
   │         with its layouts, dependencies and error pages
   ├── .nexy or .md ──► Python function ──► HTML
   ├── .py ───────────► API handler ──────► JSON
   └── framework page ► pre-rendered HTML ► HTML
```

1. The browser asks for a URL.
2. Middleware runs first: sessions, CORS, trusted hosts, your own.
3. The router finds the file for the URL, with its layouts, dependencies and error pages.
4. The file runs and answers HTML or JSON.

> [!TIP]
> When a page surprises you, follow this line once with your own URL. The answer is almost always in
> one of the four steps: middleware changed the request, the router picked another file, the page ran
> with unexpected data, or the response was not the one you thought.

## Development and production

| | `nx dev` | `nx build` then `nx start` |
|---|---|---|
| Pages | compiled when you save | compiled once, ahead of time |
| Client code | Vite dev server with hot reload, on an internal port behind Nexy's own | bundle in `__nexy__/client/`, pre-rendered HTML |
| Node.js | runs next to Python | not needed to serve |
| Errors | overlay in the browser, toolbar on every page | status pages without details |
| Origin | one port, `3000` | one port |

In development Nexy proxies Vite's endpoints through its own origin, so the browser only talks to
one port and there is no CORS to configure.

## Server mode or client mode

`useCSR` chooses who owns the page. In server mode (`False`) pages are `.nexy`, `.md` and `.mdx`
files and client components are islands inside them. In client mode (`True`) pages are the files of
your frontend framework and navigation happens in the browser. See
[Server mode and client mode](../routing/fbr/modes.md).

## What is generated

`__nexy__/` holds everything Nexy generates: compiled pages, the client entry, the build output.
Never edit it and never commit it. Delete it to force a clean build.

## Going deeper

- [Project structure](project-structure.md): every folder
- [Rendering](../rendering/README.md): SSR, ISR, CSR and islands
- [Frontend](../guides/frontend.md): Vite, styling and the client build
- The repository's `ARCHITECTURE.md` describes the packages of Nexy itself, for contributors.
