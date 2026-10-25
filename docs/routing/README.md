# Routing

Nexy has two routers. Pick one per feature; they can coexist in the same application.

| Router | Source | Enabled by |
|---|---|---|
| [File-based (FBR)](fbr/README.md) | every file under `src/routes/` | the directory exists |
| [Modular](modular/README.md) | controllers and modules | `useRouter = AppModule` in `nexyconfig.py` |

FBR is scanned whenever `src/routes/` exists, even with a modular router mounted.

## File-based routing

A route is a file. The URL is its path under `src/routes/`, minus the extension. Like Next.js, a
project is in one of two modes, chosen with `useCSR`:

| | `useCSR = False` (default) | `useCSR = True` |
|---|---|---|
| Pages | `.nexy`, `.md`, `.mdx` | files of your client framework |
| Root layout | `layout.nexy` | `layout.tsx` (React) |
| Client components | allowed, as islands inside pages | the pages themselves |
| API routes | `.py` | `.py` |

See [Server mode and client mode](fbr/modes.md).

| Section | What it covers |
|---|---|
| [fbr/pages](fbr/pages/README.md) | pages, [dynamic routes](fbr/pages/dynamic-routes.md) and route groups |
| [fbr/layouts](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` route handlers, [validation and errors](fbr/handlers/validation-and-errors.md) |
| [fbr/dependencies](fbr/dependencies/README.md) | `dependencies.py` and guards, inherited by directory |
| [fbr/middleware](fbr/middleware/README.md) | `middleware.py`, inherited by directory |
| [fbr/errors](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON errors |
| [fbr/navigation](fbr/navigation/linking-and-navigating.md) | linking, client navigation, [hooks](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | WebSocket handlers |
| [fbr/inheritance](fbr/inheritance.md) | how layouts, dependencies and error pages inherit |

## Modular routing

Controllers, modules and dependency injection, in the style of NestJS. See
[Modular routing](modular/README.md) and [Nexy and NestJS](modular/vs-nestjs.md).

## Next steps

- [File-based routing](fbr/README.md)
- [Rendering](../rendering/README.md)
- [Views](../views/README.md): what goes inside the files
