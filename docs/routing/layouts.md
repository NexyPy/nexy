# Layouts

A layout wraps every page below its directory and survives navigation between them. Nexy follows
the Next.js model: the **root layout owns the HTML document**, nested layouts add UI.

## The root layout

`src/routes/layout.nexy` is created by `nx new` for every web project, whichever client framework
or rendering mode you pick. It is the only place that writes the document tags:

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="{{ locale }}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` and `<body>` live here and nowhere else. Pages never repeat
  them.
- `<Vite />` injects the client scripts and styles once, in the `<head>`.
- `{{ children | safe }}` is where the page (or the next nested layout) renders.

> **Good to know**: a project without any layout still serves a valid document. Nexy falls back to
> a minimal shell with `<!DOCTYPE html>`, the viewport meta and the Vite tags. Add a
> `layout.nexy` as soon as you need a title, fonts or navigation.

## Nested layouts

Put a `layout.nexy` in a directory to wrap that subtree. It renders inside its parent layout:

```text
src/routes/
├─ layout.nexy          document: html, head, body
├─ index.nexy
└─ blog/
   ├─ layout.nexy       blog navigation
   └─ [slug].nexy       renders inside blog/layout.nexy, inside layout.nexy
```

The nested layout does not repeat the document tags:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

## Client-framework layouts (React, Preact)

With a React or Preact route, a `layout.tsx` (or `.jsx`) wraps the pages below it, as in Next.js.
The layout receives the page as `children`:

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <section>
      <aside>Sidebar</aside>
      {children}
    </section>
  );
}
```

Every `layout.tsx` between `src/routes/` and the page is composed, outermost first:
`<RootLayout><DashboardLayout><Page /></DashboardLayout></RootLayout>`. During client navigation the
layouts keep their state; only the page changes.

Rules:

- A framework layout never writes `<html>`, `<head>` or `<body>`. The document stays in
  `layout.nexy` (or the built-in shell).
- Pages that sit under a framework layout are mounted on the client. They have no server-rendered
  HTML snapshot, so the first paint waits for the client bundle.
- Vue, Svelte and Solid pages are wrapped by `layout.nexy` only; framework layouts are not composed
  for them yet.

## Client routing (`useCSR`)

`nx new` with client routing still scaffolds `layout.nexy`: the document is server-owned, the
pages are framework components. See [CSR](fbr/csr.md).

## Modular router

The modular router renders views you pick yourself, so you compose the layout explicitly:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

`useViews` returns an object that renders as its markup, so passing it as `children` is safe.

## Next steps

- [Pages](pages.md): dynamic segments and error pages
- [CSR](fbr/csr.md): client-side rendering
- [React](../views/react.md): React setup
