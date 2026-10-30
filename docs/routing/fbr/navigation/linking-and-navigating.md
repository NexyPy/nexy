# Linking and navigating

With client routing (`useCSR = True`), a link between two pages swaps the page in the browser instead
of reloading the document. The layouts keep their state.

## Plain links already work

Every `<a href>` to a page of your project navigates on the client, with no component and no marker:

```html
<a href="/about">About</a>
```

A link is left to the browser, and loads the page normally, when:

- a modifier key is held, or the button is not the main one;
- it has `target` (other than `_self`), `download`, `rel="external"` or `data-nexy-reload`;
- the `href` is another origin, a `mailto:` or `tel:` link, or only a `#fragment`;
- the path matches no client route, so the server answers it.

## `Link`

`Link` is the same anchor with what a plain one cannot do: its `href` is checked against your routes,
it warms the target page, and it knows when it points at the current page. Nexy generates the `Link`
of your framework in `__nexy__/src` when you run `nx dev` or `nx build`.

| Framework | Import |
|---|---|
| React, Preact, Solid, Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| Prop | Meaning |
|---|---|
| `href` | A route of the project (a typo is a type error), optionally with `?query` or `#fragment`, or an external URL. |
| `replace` | Replace the history entry instead of adding one. |
| `scroll` | `false` keeps the scroll position after navigating. Default: `true`. |
| `prefetch` | `'intent'` (default) loads the page on hover, focus or touch; `'viewport'` when the link scrolls into view; `false` never. |
| `activeClassName` | Added to the class while the link points at the current page or a page below it (`activeClass` in Vue and Svelte). |
| `exact` | Active only on the exact page. |

The link that points at the current page also gets `aria-current="page"`.

## Hooks

The location is available in every framework, in the idiom of that framework. During the first,
server-side render the hooks answer with the URL of the request, so the page hydrates without a
mismatch.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Path | `usePathname()` | `usePathname()` returns an accessor | `usePathname()` returns a ref | `$pathname` store |
| Route params | `useParams()` | `useParams()` accessor | `useParams()` ref | `$params` store |
| Query | `useSearchParams()` | `useSearchParams()` accessor | `useSearchParams()` ref | `$searchParams` store |
| Everything | `useLocation()` | `useLocation()` accessor | `useLocation()` ref | `$location` store |
| Navigate | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

The query is a `URLSearchParams`. `useRouter()` and `router` give `push(href)`, `replace(href)`,
`back()`, `forward()`, `refresh()` and `prefetch(href)`; `push` and `replace` accept
`{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## `Image`

`Image` renders an `<img>` that is lazy by default and does not shift the layout when its size is
known.

| Framework | Import |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` is required; use `alt=""` for a decorative image. Nexy warns once when it is missing.
- With both `width` and `height`, the attributes give the browser the aspect ratio and the image
  stays fluid (`height: auto; max-width: 100%`).
- `priority` loads the image now at high priority, for the one that is visible on arrival.
- `fill` makes the image cover its positioned parent, ignoring `width` and `height`.
- `sizes` and `srcSet` pass through. Nexy does not resize or convert images.

## Link from a `.nexy` page

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` renders
`<a href="/about" data-nexy-link="true">`. Every attribute and the `href` are HTML-escaped.

## What the router does

On a navigation, the router:

1. matches the path against the client routes (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. imports and renders the page and its [layouts](../layouts/README.md) **first**, and only then
   moves the URL with `history.pushState`, so the address bar never shows a page that failed;
3. dispatches a `nexy:navigated` event on `document`;
4. scrolls to the top, or to the `#fragment` target.

A newer navigation cancels an older one that is still rendering. If a page cannot render, the browser
asks the server for it instead. The back and forward buttons render the page of that entry and
restore its scroll position.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

The router starts only in a project with client routes, so a server-rendered project keeps the
browser's own back button and scroll restoration.

## Next steps

- [Layouts](../layouts/README.md)
- [CSR](../../../rendering/csr.md)
- [Components](../../../views/nexy/components.md)
