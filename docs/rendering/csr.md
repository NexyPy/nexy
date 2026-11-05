# CSR (client-side rendering)

## Definition

CSR hands navigation to the browser: after the first document, moving between pages no longer asks
the server for HTML. In Nexy it is a **project** decision, not a page one - `useCSR = True` turns the
whole application client-routed.

## How it works

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

The project then changes shape:

| | Server mode (`False`) | Client mode (`True`) |
|---|---|---|
| Routes | `.nexy`, `.md`, `.mdx` | `.tsx`, `.jsx`, `.vue`, `.svelte` |
| Document | `layout.nexy` | the root `layout.tsx` / `.vue` / `.svelte` owns `<html>`, `<head>`, `<body>` |
| Client components | islands inside a page | the pages themselves |
| `.nexy` under `src/routes/` | the page format | rejected before `nx dev`, `nx start` and `nx build` |
| Navigation | a full request per link | the client router |

`.md` and `.mdx` stay valid: Nexy renders them on the server inside the client layout, and the
client router takes over from there. `.py` handlers sit next to the routes and are served by FastAPI.

## Rendering lifecycle

1. The request reaches the file-based router, which finds the matching route and its layouts.
2. The root layout renders the **whole document** in Node - the first response already carries the
   real `<html>`, not an empty shell.
3. Nexy injects the client assets and a JSON description of the page before `</body>`.
4. The browser hydrates that document. Nested layouts keep their state from then on.
5. A link to another route is handled by the client router: no document request, the page is
   rendered in the browser.

In development the document is rendered on demand by the Vite dev server. In production it is
rendered once at build: a static route gets its document, a dynamic route gets one per declared
static param, or a shell - the layouts around an empty page - when it declares none.

## When to use

- Dashboards, editors, anything that behaves like an application.
- A Python API with a client application on top.
- A page where every interaction is local and a round trip would be felt.

## Configuration

| Setting | Value |
|---|---|
| `useFF` | required: `useCSR` without a client framework is rejected |
| `useCSR` | `True` |
| `useRouter` | must stay off: the modular router is rejected in client mode |

Files and folders starting with `_` or `.` are ignored by these checks.

## Example

```tsx filename="src/routes/layout.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head><title>My app</title></head>
      <body>{children}</body>
    </html>
  )
}
```

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Home</h1>
}
```

## Limitations

- **The whole project.** You cannot mix one CSR page into a server-mode project: pick the mode for
  the application, then use [islands](islands.md) for the interactive parts of a server-mode page.
- **No `.nexy` routes.** Anything you wrote in `.nexy` has to become a framework component.
- **Server data goes through endpoints.** A client route cannot read the database at render time; it
  calls a `.py` handler or an [Action](../guides/actions.md).
- **A dynamic route needs a declared static param, or it starts from a shell.** Export
  `getStaticParams()` from the page - the Next.js names `getStaticPaths` and `generateStaticParams`
  are also accepted - to have one document per value. Without it, the shell carries the layouts and
  not the page: the page appears once the browser has run.
- **CSR is not a blank page, and not a SPA either.** The first document is rendered by the server; it
  is the navigation that happens in the browser.

## Next steps

- [Server mode and client mode](../routing/fbr/modes.md): the checks and the rejected files
- [Layouts](../routing/fbr/layouts/README.md): which file owns the document
- [SSR](ssr.md): the default, page by page
- [Frontend](../guides/frontend.md): the dev server and the client build
