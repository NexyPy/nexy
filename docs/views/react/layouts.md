# React layouts

A `layout.tsx` wraps every page below it, in client mode (`useCSR = True`). As in the Next.js App
Router, the root `layout.tsx` defines the whole document: `<!DOCTYPE html>` is added for you, and the layout writes
`<html>`, `<head>` and `<body>` itself.

## Root layout

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>My app</title>
      </head>
      <body>
        <header>My app</header>
        <main>{children}</main>
        <footer>Open source under the MIT license.</footer>
      </body>
    </html>
  );
}
```

`nx new` with React and `useCSR = True` creates this file. The page is passed as `children`; the
layout also receives the route's props as `params`.

## Nested layouts

A `layout.tsx` in a subdirectory wraps the pages below it and renders inside its parent. It writes UI
only, never `<html>`:

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

`dashboard/index.tsx` renders as `<RootLayout><DashboardLayout><Index /></DashboardLayout></RootLayout>`.

## How the document is produced

| Moment | What happens |
|---|---|
| `nx dev` | each request asks the Vite dev server (`/__nexy__/render`) to render the layouts and the page in Node. Dynamic routes receive their real params. |
| `nx build` | every static route is rendered to a complete HTML document. A dynamic route (`[slug].tsx`) is rendered as a **shell**: the layouts around an empty page. |
| `nx start` | Python serves the pre-rendered file and adds the client assets and a small JSON description of the page. No Node process runs. |
| Browser | The framework hydrates the **whole document**. A shell is hydrated first, then the page appears. |

Without a pre-rendered file (for example the dev server is not running) Nexy sends an empty document
and the browser renders everything.

## Navigation

A click on a `Link` swaps the page and keeps the layouts mounted, including `<html>` and `<body>`:
their DOM, state and scroll position stay. A different chain of layouts rebuilds only what
differs.

## Rules

- `layout.tsx` and `layout.nexy` cannot coexist ([modes](../../routing/fbr/modes.md)).
- Only the **root** layout writes `<html>`, `<head>` and `<body>`.
- The root layout of a static route is rendered once, at build time: it cannot depend on the request
  (cookies, headers). Put request-dependent UI in a client component that reads them in the browser.
- A theme script that changes `<html>` before hydration needs `suppressHydrationWarning` on `<html>`,
  as in the example.
- Import components from `src/components/`, not from `src/routes/`.

## Next steps

- [Islands](islands.md): React inside a server-mode page, with `layout.nexy`
- [Actions and navigation](actions-and-navigation.md): the `Link` that keeps layouts mounted
- [Layouts](../../routing/fbr/layouts/README.md): how Nexy resolves a chain of layouts
