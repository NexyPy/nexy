# Glossary

The words these docs use, in one place.

| Term | Meaning |
|---|---|
| Action | A Python function marked `@Action`, served as a `POST` endpoint and callable from the client as a typed function. See [actions](../guides/actions.md). |
| Client mode | `useCSR = True`: the browser renders pages; the server answers data and the first document. See [modes](../routing/fbr/modes.md). |
| Server mode | `useCSR = False` (default): the server renders `.nexy` pages to HTML. |
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
| `__nexy__/` | The generated folder: compiled pages, the Vite entry and the action client. Never edit it; it is rebuilt. |
| `nexyconfig.py` | The project configuration, a `NexyConfig` class of `use*` fields. See [config](config.md). |
| Skill | A folder with a `SKILL.md` that teaches a coding agent one part of Nexy. See [coding agents](../guides/ai-agents.md). |
