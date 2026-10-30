# Hooks

Hooks read the current HTTP request from inside a `.nexy` page, an API handler or a modular
controller. Their names match the hooks of the client router (`@nexy/client`) where they do the same
thing.

> [!NOTE]
> hooks only work while a request is being handled. Calling one anywhere else
> raises `RuntimeError`.

## The hooks

| Hook | Returns |
|---|---|
| `usePathname()` | request path, e.g. `"/blog/post-1"` |
| `useSearchParams()` | query string as `dict[str, str]`, first value per key |
| `useParams()` | dynamic path parameters, e.g. `{"slug": "post-1"}` |
| `useQuery()` | the original name of `useParams()`, kept for existing pages |
| `useRequest()` | the Starlette request, for what the other hooks do not cover |
| `useHeaders()` | the request headers as `dict[str, str]`, names in lower case |
| `useUrl()` | the full URL: `.scheme`, `.hostname`, `.port`, `.path`, `.query` |
| `useIsActive(href, exact=False)` | whether `href` is the current page or one of its parents |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | all cookies as `dict[str, str]` |
| `useSession()` | the session dict, `{}` when sessions are not enabled |
| `useToc(depth_range="2-6")` | table of contents HTML for the current page, `""` when none |
| `useViews(path, context=None)` | renders another view and returns an `HTMLResponse` |

## Read the request

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## An active link in a navigation bar

`useIsActive` follows the same rule as on the client: the query string, the fragment and a trailing
slash are ignored, a link to a parent is active on its children unless `exact` is set, and `/` is
only active on `/`.

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## Notes

- `useQuery()` returns the **path** parameters, not the query string, which is why `useParams()`
  exists. The query string is `useSearchParams()`.
- `useRouter()` here is the request hook. It is not the `useRouter` config field that mounts an
  `APIRouter`.
- `useSession()` needs `useSession = {...}` in `nexyconfig.py`; without it the dict is empty.
- `useViews("about.tsx", {"title": "About"})` returns HTML: a `.nexy` view is rendered by its
  compiled module, a `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` view becomes a client mount container.

## Next steps

- [Pages](../pages/README.md): dynamic segments and layouts
- [Recipes](../../../guides/recipes.md): a tested sign-in flow built on `useSession()`
- [Config](../../../reference/config.md): enable sessions and locales
- [.nexy files](../../../views/nexyfile.md): where hooks are usually called
