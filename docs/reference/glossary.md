# Glossary

The words these docs use, one line each, in alphabetical order. A term that needs more than a line
has a page: follow the link. For how the notions fit together, read
[Core concepts](../getting-started/core-concepts.md).

## Terms

| Term | In one line |
|---|---|
| Action | a Python function marked `@Action`, served as a `POST` and callable from the client ([actions](../guides/actions.md)) |
| ASGI | the interface Uvicorn speaks, implemented by FastAPI and Starlette |
| Client mode | `useCSR = True`: framework files are the routes and the browser navigates ([modes](../routing/fbr/modes.md)) |
| Component | a reusable UI building block used to compose a view ([views](../views/README.md)) |
| CSR | client-side rendering: the browser renders pages after the first document ([CSR](../rendering/csr.md)) |
| Dependency | a function FastAPI runs before a handler, per route or per folder ([dependencies](../routing/fbr/dependencies/README.md)) |
| Document shell | the `<html>`, `<head>` and `<body>` around a page, owned by the nearest layout or by Nexy ([layouts](../routing/fbr/layouts/README.md)) |
| Endpoint | the unique combination of a URL and an HTTP method ([views](../views/README.md)) |
| FBR | file-based routing: a file under `src/routes/` is a route ([routing](../routing/fbr/README.md)) |
| Frontmatter | the Python block between the two `---` lines of a `.nexy` or `.md` file ([.nexy files](../views/nexy/README.md)) |
| Guard | a dependency that refuses a request by raising `HTTPException` ([guards](../routing/modular/guards-and-metadata.md)) |
| Handler | a Python function that handles an HTTP request for a specific method ([views](../views/README.md)) |
| HMR | hot module replacement: the dev server swaps the modules that changed, without a full reload ([frontend](../guides/frontend.md)) |
| Hydration | the browser attaching a framework to HTML the server already sent ([islands](../rendering/islands.md)) |
| Island | a client component mounted inside a server-rendered page ([islands](../rendering/islands.md)) |
| ISR | incremental static regeneration: one cached page per path, refreshed in the background ([ISR](../rendering/isr.md)) |
| Layout | a `layout.*` file that wraps the pages below its folder ([layouts](../routing/fbr/layouts/README.md)) |
| Modular router | routes declared with `@Module` and `@Controller` under `src/apps/` ([modular](../routing/modular/README.md)) |
| Page | an URL-addressable resource defined by a file under `src/routes/` ([views](../views/README.md)) |
| Prefetch | loading the page behind a link before the reader clicks it ([linking](../routing/fbr/navigation/linking-and-navigating.md)) |
| Props | the values a parent passes to a component ([.nexy files](../views/nexy/README.md)) |
| Revalidate | the number of seconds after which an ISR page is rebuilt in the background ([ISR](../rendering/isr.md)) |
| Route | a URL pattern, produced by the path of a route file ([routing](../routing/README.md)) |
| Route group | a folder in parentheses that groups routes without adding a segment ([dynamic routes](../routing/fbr/pages/dynamic-routes.md)) |
| Route handler | the `GET`, `POST`, … function of a `.py` route file ([handlers](../routing/fbr/handlers/README.md)) |
| Server mode | `useCSR = False`, the default: the server renders `.nexy` and `.md` pages ([modes](../routing/fbr/modes.md)) |
| Skill | a folder with a `SKILL.md` that teaches a coding agent one part of Nexy ([coding agents](../guides/ai-agents.md)) |
| SSG | static site generation; **not a Nexy mode**: the HTML built ahead of time is always read back by the server ([rendering](../rendering/README.md)) |
| SSR | server-side rendering: the server renders each page for its request, and it is the default ([SSR](../rendering/ssr.md)) |
| View | the process of producing the response body for a page ([views](../views/README.md)) |

## Files and folders

| Name | In one line |
|---|---|
| `__nexy__/` | generated output: compiled pages, the client entry and the action client; never edited, never committed |
| `nexyconfig.py` | the project configuration, a class of `use*` fields ([config](config.md)) |
| `public/` | files served at the root, such as `public/logo.svg` → `/logo.svg` ([file conventions](file-conventions.md)) |
| `src/apps/` | controllers and modules of the modular router ([modular](../routing/modular/README.md)) |
| `src/components/` | components imported by pages; never routes ([file conventions](file-conventions.md)) |
| `src/routes/` | the routes of the application ([file conventions](file-conventions.md)) |

## Next steps

- [Core concepts](../getting-started/core-concepts.md): the model these words belong to
- [Documentation index](../README.md): the page for the task at hand
- [File conventions](file-conventions.md): the reserved names behind these definitions
- [For AI agents](../guides/ai-agents.md): the same invariants, written for an agent
