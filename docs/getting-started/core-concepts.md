# Core concepts

The mental model, before the API: four levels of reading, then the notions that come back on every
page. Each notion gets one line here and a link to the page that goes deeper.

## How to read these docs

| Level | The question it answers | Start with |
|---|---|---|
| Application architecture | which layer answers a request, and what it refuses to do | [Architecture](../architecture.md) |
| Application structure | where the code lives, and what a file becomes | [Project structure](project-structure.md) |
| Presentation and rendering | what the reader sees, and who produces the HTML | [Views](../views/README.md), [Rendering](../rendering/README.md) |
| Application interaction | what the reader does, and what runs in response | [Actions](../guides/actions.md) |

The levels are read in that order once. After that, a page you need is a lookup, not a course.

## Application architecture

Three ways to decide which code answers a URL. They are alternatives, not layers:

- **File-based routing (FBR)**: a file under `src/routes/` is a route. The default.
- **Modular router**: controllers and modules under `src/apps/`, declared with decorators, for a
  NestJS-style codebase.
- **Custom router**: an existing FastAPI `APIRouter` included in the application.

Choosing one of the three is one decision. Choosing a frontend framework is another, separate one:
see [Choose a router](../routing/README.md) and [Views](../views/README.md).

## Application structure

Five notions that a reader coming from Next.js usually merges into one. They are not the same thing,
and the difference explains most "why is my page not rendering" questions.

| Notion | What it is | What it is not |
|---|---|---|
| **Route** | a URL pattern, produced by the path of a file | a file: one file can answer several URLs (`[slug]`) |
| **Page** | a route file that renders a view: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | an endpoint: it answers a document, not data |
| **View** | what produces the body of a page: Jinja2 and Python, Markdown, or a client component | a route: the same view can serve several pages |
| **Component** | a reusable piece a page imports | a route: in server mode a component is never served on its own |
| **Route handler** | the function of a `.py` route file, named after the HTTP method (`GET`, `POST`, …) | a page: it returns JSON, a file or a `Response` |
| **Endpoint** | the pair (URL, method) that a handler answers | a handler: one file can answer several endpoints |

In one sentence: **a page is a route file, a view is what renders it, a component is what a page
reuses, a handler answers an endpoint.**

Two more words that come back everywhere:

- **Layout**: a `layout.*` file that wraps the pages below its folder; the root one owns the HTML
  document. See [Layouts](../routing/fbr/layouts/README.md).
- **Dependency**: a function that runs before a handler, applied per route or per folder. See
  [Dependencies](../routing/fbr/dependencies/README.md).

## Presentation and rendering

Two independent decisions, often confused:

- **The format** decides which file renders the page: [Views](../views/README.md).
- **The mode** decides who produces the HTML and when: [Rendering](../rendering/README.md).

| Notion | One line |
|---|---|
| Server mode | the server renders `.nexy` and `.md` pages; components are islands ([modes](../routing/fbr/modes.md)) |
| Client mode | `useCSR = True`: framework files are the routes, and navigation happens in the browser |
| SSR, ISR, CSR, islands | four rendering modes, decided per page except CSR, which is per project ([rendering](../rendering/README.md)) |
| Hydration | the browser attaching a framework to HTML the server already sent ([islands](../rendering/islands.md)) |
| Props | the values a parent passes to a component, declared `name: prop[type]` in a `.nexy` file ([.nexy files](../views/nexy/README.md)) |

## Application interaction

| Notion | One line |
|---|---|
| Action | a Python function marked `@Action`, served as a `POST`, callable from a form or as a typed function ([actions](../guides/actions.md)) |
| Form | an HTML form that posts to an Action, with validation errors coming back to the page ([actions](../guides/actions.md)) |
| Navigation | links that prefetch, and hooks that read the path, the query, the cookies and the session ([hooks](../routing/fbr/navigation/hooks.md)) |
| Data fetching | done by the page or the handler that needs it; Nexy ships no client data layer ([handlers](../routing/fbr/handlers/README.md)) |

## What Nexy does not do

Authentication, authorisation, database, internationalisation, background jobs, email, payments and
search are **your application's responsibility**, not the framework's. Nexy gives the extension
points and says where to plug each one: see [the boundaries](../architecture.md#boundaries).

The reason is not minimalism for its own sake: a framework that picks your ORM or your auth library
has decided something only your application can decide.

## Next steps

- [Architecture](../architecture.md): the layers, and who builds what
- [Project structure](project-structure.md): every folder and file of a project
- [Glossary](../reference/glossary.md): the same words, in one alphabetical index
- [How Nexy works](how-nexy-works.md): one request, step by step
