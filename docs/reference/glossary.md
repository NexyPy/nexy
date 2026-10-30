# Glossary

The words these docs use, in one place.

| Term | Meaning |
|---|---|
| Action | A Python function marked `@Action`, served as a `POST` endpoint and callable from the client as a typed function. See [actions](../guides/actions.md). |
| Client mode | `useCSR = True`: the browser renders pages; the server answers data and the first document. See [modes](../routing/fbr/modes.md). |
| Server mode | `useCSR = False` (default): the server renders `.nexy` pages to HTML. |
| SSR | Server-side rendering: the server renders each page to HTML for the request; the default. See [SSR](../rendering/ssr.md). |
| CSR | Client-side rendering: the browser renders pages and handles navigation after the first document. See [CSR](../rendering/csr.md). |
| ISR | Incremental static regeneration: a page cached per path and refreshed in the background after `revalidate` seconds (stale-while-revalidate). See [ISR](../rendering/isr.md). |
| FBR | File-based routing: a file under `src/routes/` is a route. See [routing](../routing/fbr/README.md). |
| Modular router | Routing declared with `@Module` and `@Controller` classes under `src/apps`. See [modular](../routing/modular/README.md). |
| Handler | A function named after an HTTP method (`GET`, `POST`, ...) in a `.py` route file. |
| Page | A route file that renders a view: `.nexy`, or `.tsx`, `.vue`, `.svelte`, `.md`, `.mdx`. |
| Layout | A `layout.*` file that wraps the pages below its folder. See [layouts](../routing/fbr/layouts/README.md). |
| Route group | A folder in parentheses, such as `(shop)/`, that groups routes without adding to the URL. |
| Dependency | A function FastAPI runs before the handler; `dependencies.py` applies one to a whole folder. See [dependencies](../routing/fbr/dependencies/README.md). |
| Guard | A dependency that refuses a request, by raising `HTTPException`. |
| Island | A client component (React, Vue, ...) mounted inside a server-rendered `.nexy` page. See [components](../views/components.md). |
| SSG | Static site generation: pages rendered to HTML at build time and read back at request time. |
| Hydration | The browser attaching a framework to HTML the server already sent. |
| View | The file that produces a page's HTML: an `.nexy` page, Markdown, MDX or a client component. See [views](../views/README.md). |
| Component | A reusable piece a page imports; in server mode it is never a route. See [components](../views/components.md). |
| Props | Values a parent passes to a component; a `.nexy` prop is declared as `name: prop[type]`, with `= default` when optional. |
| Frontmatter | The block between `---` lines at the top of a `.nexy` or `.md` file: Python code, props and settings. |
| Prefetch | Loading the page behind a link before the reader clicks it. See [linking](../routing/fbr/navigation/linking-and-navigating.md). |
| Revalidate | The number of seconds after which an ISR page is rebuilt in the background. See [ISR](../rendering/isr.md). |
| HMR | Hot module replacement: the dev server swaps the modules that changed, without a full reload. See [dev toolbar](../guides/devtools.md). |
| ASGI | The Python interface of a Nexy application, served by Uvicorn and used by FastAPI and Starlette. |
| Document shell | The `<html>`, `<head>` and `<body>` around a page: the nearest layout owns it; without one, Nexy renders a minimal shell. |
| `__nexy__/` | The generated folder: compiled pages, the Vite entry and the action client. Never edit it; it is rebuilt. |
| `nexyconfig.py` | The project configuration, a `NexyConfig` class of `use*` fields. See [config](config.md). |
| Skill | A folder with a `SKILL.md` that teaches a coding agent one part of Nexy. See [coding agents](../guides/ai-agents.md). |

## Where next

- [Documentation index](../README.md): the page for the task at hand
- [File conventions](file-conventions.md): the reserved names these definitions refer to
- [For AI agents](agents.md): the same invariants, written for an agent
