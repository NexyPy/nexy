# SSR (server rendering)

## Definition

SSR is the default: the server renders the page to HTML for each request. Nothing enables it, and
no flag turns it off - a server-mode project renders on every request unless a page declares
`revalidate`.

## How it works

<!-- router:fbr,custom -->
| Route file | What produces the HTML | When |
|---|---|---|
| `.nexy` | the compiled Python module, through Jinja2 | every request |
| `.md` | Markdown, then the nearest layout | every request |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | the framework, rendered in Node | at build when the route has no layout, otherwise in the browser |
| `.py` | nothing: it returns JSON or a `Response` | - |

A Markdown page and a handler, side by side in the same project:

```md filename="src/routes/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

A component route is the one case that needs a second sentence. In production, a component route
**without** a layout is served with the HTML produced at build, and the component hydrates it. With
a layout, or in development, the container is empty and the component renders in the browser - the
page is then a shell that fills itself.

The component route of the table, without a layout, so production serves its HTML from the build:

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| A controller returns | What produces the HTML | When |
|---|---|---|
| `useViews("....nexy")` | the compiled Python module, through Jinja2 | every request |
| a `dict`, a list, a model | nothing: FastAPI answers JSON | - |

A view and a JSON endpoint, side by side in the same module:

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## Rendering lifecycle

<!-- router:fbr,custom -->
1. The request reaches the file-based router. The path is matched, and dynamic segments are cast to
   the types the component declares.

   ```nexy filename="src/routes/orders/[id].nexy"
   ---
   id: prop[int]
   ---
   <h1>Order #{{ id + 1000 }}</h1>
   ```

   `/orders/42` renders `Order #1042`; `/orders/abc` answers `404`.
2. The component runs. One that waits on Node - a client document - runs in a thread pool, so it
   does not stall the event loop.
3. The body is streamed as `text/html`. A component that yields chunks streams them as it makes
   them.
4. The browser receives HTML. Islands hydrate according to their [directive](islands.md).

An error raised while rendering is turned into a page by `errors.nexy` when the project has one: see
[error pages](../routing/fbr/errors/README.md).
<!-- /router -->

<!-- router:modular -->
1. The request reaches the controller. Its path parameters are cast to the types the method
   declares, and passed to the view:

   ```python filename="src/apps/order_controller.py"
   from nexy.decorators import Controller
   from nexy.hooks import useViews


   @Controller("/orders/{id}")
   class OrderController:
       async def get(self, id: int):
           return useViews("src/apps/order_view.nexy", context={"id": id})
   ```

   ```nexy filename="src/apps/order_view.nexy"
   ---
   id: prop[int]
   ---
   <h1>Order #{{ id + 1000 }}</h1>
   ```

   `/orders/42/` renders `Order #1042`; `/orders/abc/` answers `404`.
2. The view runs, and `useViews` returns its HTML as the response.
3. The browser receives HTML. Islands hydrate according to their [directive](islands.md).

An error raised while rendering is answered with the default error page.
<!-- /router -->

## When to use

- The page shows something the reader owns: a session, an account, a cart.
- The data must be fresh on every load.
- The content must be in the HTML for crawlers that do not run JavaScript.
- The page is cheap to render: one query, one template.

The first case, a page that greets the reader from the session. `useSession` reads the session of
`useSession` in `nexyconfig.py`, without which it fails:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## Configuration

<!-- router:fbr,custom -->
None. Two ways out, and they do not have the same grain:

| To leave SSR for | Do this | Grain |
|---|---|---|
| one page, with a cache | `revalidate = 60` in its frontmatter → [ISR](isr.md) | page |
| the whole project, client-routed | `useCSR = True` in `nexyconfig.py` → [CSR](csr.md) | project |

The project-wide switch, in `nexyconfig.py`. Client mode needs a client framework:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
None. Every view a controller returns is rendered on each request: [ISR](isr.md) and
[CSR](csr.md) are modes of the file-based router.
<!-- /router -->

## Example

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` runs this template once, with `slug` set to `hello`. A second request runs it
again: nothing is kept between the two. The query string is not a prop - read it with the hooks in
[navigation](../routing/fbr/navigation/hooks.md).
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` runs this view once, with `slug` set to `hello`. A second request runs it again:
nothing is kept between the two. The query string is not a prop - read it with `useSearchParams`.
<!-- /router -->

## Limitations

- **One render per request.** Two visitors in the same second each pay for the render and for the
  queries behind it.
- **No cache.** There is no shared response cache to warm: with file routes, [ISR](isr.md) adds
  one, per URL.
- **Streaming only helps a component that yields.** A slow query at the top of the page still delays
  the first byte.
- **No static output.** In server mode nothing is frozen at build: there is no SSG mode, and no
  export command. See [Rendering](README.md).
- **Autoescaping is off** in `.nexy` templates. Escape untrusted values with `| e`.

<!-- router:fbr,custom -->
```nexy filename="src/routes/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## Next steps

<!-- router:fbr,custom -->
- [ISR](isr.md): cache this page per URL
<!-- /router -->
- [Islands](islands.md): keep SSR and make one widget interactive
<!-- router:fbr,custom -->
- [CSR](csr.md): hand navigation to the browser
<!-- /router -->
- [Performance](../deployment/performance.md)
