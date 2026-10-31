# Solid layouts

A `layout.tsx` wraps every page below it, in client mode (`useCSR = True`). The root `layout.tsx`
defines the whole document: `<!DOCTYPE html>` is added for you, and the layout writes `<html>`,
`<head>` and `<body>` itself.

## Root layout

```tsx filename="src/routes/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html lang="en" class="dark">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>My app</title>
      </head>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

`nx new` with Solid and `useCSR = True` creates this file. The page is passed as `props.children`;
do not destructure it, Solid reads it lazily. The layout also receives the route's props as
`props.params`.

## Nested layouts

A `layout.tsx` in a subdirectory wraps the pages below it and renders inside its parent. It writes UI
only, never `<html>`:

```tsx filename="src/routes/dashboard/layout.tsx"
import type { JSX } from "solid-js";

export default function DashboardLayout(props: { children: JSX.Element }) {
  return (
    <section>
      <aside>Sidebar</aside>
      {props.children}
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
| Browser | Solid hydrates the **whole document**. A shell is hydrated first, then the page appears. |

Solid compiles the layouts twice, once for the server and once for the browser, which is why
`vite.config.ts` has `solid({ ssr: true })` in client mode.

## Navigation

A click on a `Link` swaps the page and keeps the layouts mounted, including `<html>` and `<body>`:
their DOM, signals and scroll position stay. Only the page changes in place: a navigation to a page
with a **different chain of layouts** (for example from `/` to `/dashboard`) loads that page
normally, with a full request.

## Solid needs the server render

Solid hydrates the server document and cannot build it in the browser alone. When Nexy has no
rendered document to send (the Vite dev server is not running and nothing was built), the browser
logs `Solid needs the server-rendered document` instead of rendering. React, Preact, Vue and Svelte
render in the browser in that case.

## Rules

- `layout.tsx` and `layout.nexy` cannot coexist ([modes](../../routing/fbr/modes.md)).
- Only the **root** layout writes `<html>`, `<head>` and `<body>`.
- The root layout of a static route is rendered once, at build time: it cannot depend on the request
  (cookies, headers). Put request-dependent UI in a component that reads it in the browser.
- Import components from `src/components/`, not from `src/routes/`.

## Next steps

- [Islands](islands.md): Solid inside a server-mode page, with `layout.nexy`
- [Actions and navigation](actions-and-navigation.md): the `Link` that keeps layouts mounted
- [Layouts](../../routing/fbr/layouts/README.md): how Nexy resolves a chain of layouts
