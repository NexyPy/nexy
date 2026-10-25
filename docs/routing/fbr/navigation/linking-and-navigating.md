# Linking and navigating

With client routing, links between framework pages swap the page in the browser instead of
reloading the document.

## Link from a `.nexy` page

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` renders
`<a href="/about" data-nexy-link="true">`. Every attribute and the `href` are HTML-escaped.

## Link from a React component

`nx dev` and `nx build` generate a typed `Link` in `__nexy__/src/Link.tsx`. Its `href` is limited to
the routes of your project, so a broken link is a type error:

```tsx
import { Link } from "@nexy/Link.tsx";

export default function Nav() {
  return <Link href="/dashboard">Dashboard</Link>;
}
```

## Any other anchor

An `<a data-nexy-link href="/blog">` is handled by the client router in any framework or in plain
HTML.

## What the router does

On a click on a `data-nexy-link` anchor, the router:

1. ignores it when a modifier key is held, when `target="_blank"` is set, or when the `href` is
   external (`http...`), an anchor (`#...`) or `mailto:`;
2. matches the path against the client routes (`.tsx`, `.jsx`, `.vue`, `.svelte`);
3. imports the page and its [framework layouts](../layouts/README.md), renders the page,
   then updates the URL with `history.pushState`;
4. dispatches a `nexy:navigated` event on `document`.

A path that matches no client route falls back to a normal navigation.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

The browser's back and forward buttons use the same path.

## Prefetching

By default a link prefetches its target when the pointer enters it or when it is touched: the page
module and its layouts are imported ahead of the click. Pass `prefetch=False` to `Link` (or
`prefetch={false}` in React) to turn it off.

## Next steps

- [Layouts](../layouts/README.md)
- [CSR](../../../rendering/csr.md)
- [Components](../../../views/components.md)
