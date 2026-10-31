# React

Nexy renders React 19 components on the server, then React hydrates them in the browser. A project
uses React in one of two ways:

| Mode | `nexyconfig.py` | Pages are | React is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](islands.md) inside those pages |
| Client | `useCSR = True` | `.tsx` files | the whole page, with [layouts](layouts.md) and a client router |

## Start a project

```bash
nx new my-app --template web-fbr-react
```

The template is a server-mode project with React islands. Run `nx new my-app` without a template to
answer the prompts instead: the router, the project type, whether to use client-side routing, then
the framework.

## Enable React in an existing project

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` writes this file; Nexy writes `__nexy__/vite.ts` itself, so do not edit it.

| Package | Version `nx new` writes |
|---|---|
| `react`, `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`, `@types/react-dom` | dev dependencies |

## Rules

- **One framework per project.** `useFF` takes exactly one framework; `useFF = [react(), vue()]` stops
  the server at startup.
- **Pages are `.tsx`.** React owns `.tsx` and `.jsx` for components, but only a `.tsx` file under
  `src/routes/` becomes a page.
- **Components live outside `src/routes/`**, usually in `src/components/`, so they are not pages.
- **A server-mode project has no `.tsx` page**, and a client-mode project has no `.nexy` page: Nexy
  refuses to start and names the file. See [modes](../../routing/fbr/modes.md).

## In this section

- [Pages](pages.md): a `.tsx` route, its export, its params, server rendering
- [Layouts](layouts.md): the root `layout.tsx` that owns `<html>`, nested layouts
- [Islands](islands.md): a React component inside a `.nexy` page
- [Actions and navigation](actions-and-navigation.md): call Python, link pages, read the URL

## Next steps

- [Views](../README.md): compare formats
- [Frontend](../../guides/frontend.md): Vite and the client build
