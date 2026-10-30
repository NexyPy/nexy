# Preact layouts

A `layout.tsx` wraps every page below it, in client mode (`useCSR = True`). The root `layout.tsx`
defines the whole document: `<!DOCTYPE html>` is added for you, and the layout writes `<html>`,
`<head>` and `<body>` itself.

## Root layout

```tsx filename="src/routes/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html lang="en" class="dark">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>My app</title>
      </head>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

`nx new` with Preact and `useCSR = True` creates this file. The page is passed as `children`; the
layout also receives the route's props as `params`.

## Nested layouts

A `layout.tsx` in a subdirectory wraps the pages below it and renders inside its parent. It writes UI
only, never `<html>`:

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ComponentChildren } from "preact";

export default function DashboardLayout({ children }: { children: ComponentChildren }) {
  return (
    <section>
      <aside>Sidebar</aside>
      {children}
    </section>
  );
}
```

`dashboard/index.tsx` renders as `<RootLayout><DashboardLayout><Index /></DashboardLayout></RootLayout>`.

## How the document is produced

| Moment | What happens |
|---|---|
| `nx dev` | each request asks the Vite dev server (`/__nexy__/render`) to render the layouts and the page in Node. Dynamic routes receive their real params. |
| `nx build` | every static route is rendered to a complete HTML document. A dynamic route (`[slug].tsx`) is rendered as a **shell**: the layouts around an empty page. |
| `nx start` | Python serves the pre-rendered file and adds the client assets and a small JSON description of the page. No Node process runs. |
| Browser | Preact builds the body and swaps it in; `<html>` and `<head>` stay as sent. |

Preact cannot hydrate a whole document: its `hydrate` builds a second `<html>` element and leaves the
handlers unattached. So the browser renders the page body and puts it in place of the one the server
sent, and the server HTML is not reused. See
[how the browser takes over](../../routing/fbr/layouts/README.md#how-the-browser-takes-over-the-document).
In practice:

- Put the title, meta tags, fonts and theme script in the root layout: the server renders them and
  they stay as they are.
- A state-driven class on `<html>`, `<head>` or `<body>` is applied by the server but does not update
  in the browser. Change those elements from a script.

Without a pre-rendered file (for example the dev server is not running) Nexy sends an empty document
and the browser renders everything.

## Navigation

A click on a `Link` updates the page and leaves the layouts mounted: their DOM, state and scroll
position stay. The layouts that differ between two pages are rebuilt.

## Rules

- `layout.tsx` and `layout.nexy` cannot coexist ([modes](../../routing/fbr/modes.md)).
- Only the **root** layout writes `<html>`, `<head>` and `<body>`.
- The root layout of a static route is rendered once, at build time: it cannot depend on the request
  (cookies, headers). Put request-dependent UI in a component that reads it in the browser.
- Import components from `src/components/`, not from `src/routes/`.

## Next steps

- [Islands](islands.md): Preact inside a server-mode page, with `layout.nexy`
- [Actions and navigation](actions-and-navigation.md): the `Link` that keeps layouts mounted
- [Layouts](../../routing/fbr/layouts/README.md): how Nexy resolves a chain of layouts
