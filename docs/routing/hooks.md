# Hooks

Hooks read the current HTTP request from inside a `.nexy` page.

> **Good to know**: hooks only work while a request is being handled. Calling one anywhere else
> raises `RuntimeError`.

## The hooks

| Hook | Returns |
|---|---|
| `usePathname()` | request path, e.g. `"/blog/post-1"` |
| `useSearchParams()` | query string as `dict[str, str]`, first value per key |
| `useQuery()` | dynamic path parameters, e.g. `{"slug": "post-1"}` |
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

## Notes

- `useRouter()` here is the request hook. It is not the `useRouter` config field that mounts an
  `APIRouter`.
- `useSession()` needs `useSession = {...}` in `nexyconfig.py`; without it the dict is empty.
- `useViews("about.tsx", {"title": "About"})` returns HTML: a `.nexy` view is rendered by its
  compiled module, a `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` view becomes a client mount container.

## Next steps

- [Pages](pages.md): dynamic segments and layouts
- [Config](../config.md): enable sessions and locales
- [.nexy files](../views/nexyfile.md): where hooks are usually called
