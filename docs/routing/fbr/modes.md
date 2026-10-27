# Server mode and client mode

A Nexy project is either **server-rendered** or **client-routed**, like a Next.js project is either
pages rendered on the server or a client app. `useCSR` in `nexyconfig.py` chooses.

## Server mode (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- Pages are `.nexy`, `.md` or `.mdx` files under `src/routes/`.
- The root `layout.nexy` owns `<!DOCTYPE html>`, `<html>`, `<head>` and `<body>`.
- Client components (React, Vue, Svelte, Solid or Preact) are allowed as **islands**: you import one
  from a `.nexy` page and it hydrates in the browser. See [Islands](../../rendering/islands.md).
- A client component is never a route. Keep them in `src/components/`.
- One client framework at a time.

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## Client mode (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- Pages are the files of your client framework: `.tsx` for React, `.vue`, `.svelte`.
- The root layout of any framework (`layout.tsx`, `layout.vue`, `layout.svelte`) owns `<!DOCTYPE html>`, `<html>`, `<head>` and `<body>`, like the
  root layout of the Next.js App Router. Nexy renders it in Node for the first response and the
  framework hydrates the whole document. See [layout.tsx](layouts/layout.tsx.md).
- `.py` files are API handlers served by FastAPI, next to the client routes.
- There is no `.nexy` file at all, and no `layout.nexy`.
- Navigation between pages happens in the browser.

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## What is rejected

Nexy checks the project before `nx dev`, `nx start` and `nx build` and stops with the list of files:

| Mode | Rejected | Message |
|---|---|---|
| server | `.tsx`, `.jsx`, `.vue` or `.svelte` under `src/routes/` | move components to `src/components/`, or set `useCSR = True` |
| client | any `.nexy` file under `src/routes/` | write them as framework components, or set `useCSR = False` |
| both | more than one frontend framework in `useFF` | `useFF must configure exactly one frontend framework` |
| client | `useRouter` (modular router) | `useCSR requires file-based routing` |
| client | no `useFF` | `useCSR requires a client framework` |

Files and folders starting with `_` or `.` are ignored by this check.

## Which one

- **Content, marketing, docs, SEO-first sites**: server mode with islands.
- **Dashboards and apps with rich client navigation**: client mode.
- **A Python API with a client app on top**: client mode, with `.py` handlers next to the pages.

## Next steps

- [Layouts](layouts/README.md)
- [Rendering](../../rendering/README.md)
- [Config](../../reference/config.md)
