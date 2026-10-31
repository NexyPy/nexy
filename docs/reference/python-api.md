# Python API

Every name Nexy exports to your Python code, by module. A test checks this page against the code in
both directions: a name listed here must exist, and a name the code exports must be listed here.

## `nexy`

Components for `.nexy` templates and the request hooks.

| Name | What it is |
|---|---|
| `Audio`, `Video` | native `<audio>` and `<video>` players, see [components](../views/nexy/components.md) |
| `Image` | an `<img>` that loads lazily by default |
| `Link` | a client-side `<a>` with optional prefetch |
| `Import` | import a client component into a `.nexy` page |
| `Template` | render Jinja2 and Markdown templates |
| `Vite` | the Vite client tag every page needs |
| `Form` | a placeholder with no behaviour: use a plain `<form>` with an [action](../guides/actions.md) |
| `usePathname` | the path of the current request |
| `useSearchParams` | the query string as a dict |
| `useParams` | the dynamic path parameters as a dict, like `useParams()` on the client |
| `useQuery` | the original name of `useParams`, kept for existing pages (it does not read the query string) |
| `useRequest` | the current request, for what the other hooks do not cover |
| `useHeaders` | the request headers as a dict with lower-case names |
| `useUrl` | the full URL: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | whether a link points at the current page or one of its parents, for a navigation bar |
| `useRouter` | `path`, `base_url` and `url_for` of the current request |
| `useSession` | the session dict, empty when sessions are off |
| `useCookies` | the request cookies as a dict |
| `useToc` | the table of contents of the current page, as HTML |
| `useViews` | render a view file such as `about.tsx` from a handler |
| `setMetadata`, `useMetadata` | name the title and head tags of a page, and write them in the layout |
| `redirect`, `permanentRedirect` | send the visitor elsewhere (307, 308) and stop the request |
| `notFound`, `forbidden`, `unauthorized` | answer 404, 403 or 401 from anywhere |

The hooks work inside a request only: see [hooks](../routing/fbr/navigation/hooks.md).

## `nexy.http`

The HTTP vocabulary of a handler. Import from here rather than from FastAPI, so your handlers depend
on Nexy's contract.

| Name | What it is |
|---|---|
| `Request`, `Response` | the incoming request and an outgoing response |
| `HTTPException` | stop the handler with a status and a `detail` |
| `status` | named status codes, such as `status.HTTP_404_NOT_FOUND` |
| `Depends` | run a function first and pass its result in |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | where a parameter comes from |
| `Form`, `File`, `UploadFile` | form fields and uploads (need `python-multipart`) |
| `BackgroundTasks` | work that runs after the answer is sent |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | answers with a fixed content type |
| `RedirectResponse` | an HTTP redirect |
| `redirect`, `permanentRedirect` | raise a redirect (307, 308) from a page, a handler, a controller or a guard |
| `notFound`, `forbidden`, `unauthorized` | raise a 404, 403 or 401 from the same places |
| `FileResponse`, `StreamingResponse` | answer with a file or a stream |

## `nexy.decorators`

| Name | What it is |
|---|---|
| `Action` | turn a function into a `POST` endpoint, see [actions](../guides/actions.md) |
| `revalidate` | tell the browser which pages an action made stale |
| `Module`, `Controller` | declare a module and a controller in the [modular router](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [dependency injection](../routing/modular/dependency-injection.md) and its lifetimes |
| `UseGuard`, `Middleware` | guard or wrap one handler, see [guards](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | name a route and describe it for OpenAPI |
| `UseResponse`, `ResponseMeta` | describe the answer of a route |
| `HTTP_METHODS` | the HTTP methods a handler file may define |
| `ACTIONS_STORE` | the registry of actions, for tooling and tests |

## `nexy.testing`

| Name | What it is |
|---|---|
| `render` | the HTML of a `.nexy` component for given props, without a server, see [testing](../guides/testing.md) |

## Where next

- [Config](config.md): the `use*` fields behind these names
- [Exceptions and errors](exceptions.md): what each failure answers
- [Documentation index](../README.md): the page for what you are building
