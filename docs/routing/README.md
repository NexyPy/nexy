# Routing

Nexy has two native routers. You can pick one per feature; they can coexist in the same application.

**Not sure? Use file-based routing.** It covers pages and API endpoints with no setup. Add the modular router when a backend needs controllers, injected services or guards.

| You are building | Use |
|---|---|
| Pages, content, a site with a few endpoints | File-based |
| A large API with services shared across routes | Modular |
| Both: pages for people, a structured API for machines | File-based and modular together |

<!-- router:fbr,custom -->
```diagram filename="The file-based router, at a glance"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```
<!-- /router -->

<!-- router:modular -->
```diagram filename="The modular router, at a glance"
@Controller()             class AppController   →  /
@Controller("/about")     class AboutController →  /about/
@Controller("/api/users") class UserController  →  /api/users/  (get, post, …)
@Module()                 class AppModule       →  lists the controllers
useRouter = AppModule     nexyconfig.py         →  mounts the module
```
<!-- /router -->

| Router | Source | Enabled by |
|---|---|---|
| [File-based (FBR)](fbr/README.md) | every file under `src/routes/` | the directory exists |
| [Modular](modular/README.md) | controllers and modules | `useRouter = AppModule` in `nexyconfig.py` |

FBR is scanned whenever `src/routes/` exists, even with a modular router mounted.

## Coexistence and priorities

You can combine FBR, Modular, and custom integration. Nexy registers these routes in the order they are discovered. If two routers define the same URL path, the first one registered wins. 

*Note: Nexy does not currently provide a diagnostic for URL collisions; the first route to claim a path simply shadows the others.*

<!-- router:fbr,custom -->
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
<!-- /router -->

## Modular routing

Controllers, modules and dependency injection, in the style of NestJS. See
[Modular routing](modular/README.md) and [Nexy and NestJS](modular/vs-nestjs.md).

<!-- router:modular -->
| Section | What it covers |
|---|---|
| [modular](modular/README.md) | `@Controller`, `@Module`, imports and exports |
| [modular/dependency-injection](modular/dependency-injection.md) | `@Injectable`, scopes and the container |
| [modular/guards-and-metadata](modular/guards-and-metadata.md) | `@UseGuard`, `@UseResponse` and the OpenAPI metadata |

A controller returns a `.nexy` view with `useViews`, and passes it to its layout by hand: there is
no `layout.nexy` applied by folder.
<!-- /router -->

## Custom Integration

You can also integrate an existing FastAPI router into your Nexy project. See [Custom routing integration](custom/README.md).

## Next steps

<!-- router:fbr,custom -->
- [File-based routing](fbr/README.md)
<!-- /router -->
<!-- router:modular -->
- [Modular routing](modular/README.md)
<!-- /router -->
- [Rendering](../rendering/README.md)
- [Views](../views/README.md): what goes inside the files
