# Preact

Nexy renders Preact 10 components on the server, then Preact takes them over in the browser. A
project uses Preact in one of two ways:

| Mode | `nexyconfig.py` | Pages are | Preact is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](islands.md) inside those pages |
| Client | `useCSR = True` | `.tsx` files | the whole page, with [layouts](layouts.md) and a client router |

## Start a project

```bash
nx new my-app --template web-fbr-preact
```

The template is a server-mode project with Preact islands. Run `nx new my-app` without a template to
answer the prompts instead: the router, the project type, whether to use client-side routing, then
the framework.

## Enable Preact in an existing project

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` writes this file; Nexy writes `__nexy__/vite.ts` itself, so do not edit it.

| Package | Version `nx new` writes |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (dev dependency) |
| `preact-render-to-string` | `^6.7.0` (dev dependency, renders on the server) |

## Write Preact

A Preact component is a React-style function. The differences that matter here:

```tsx filename="src/components/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- Hooks come from `preact/hooks`, types such as `ComponentChildren` from `preact`.
- Write HTML attributes: `class`, `for`, `charset`. `Link` reads its classes from `class`.

## Rules

- **One framework per project.** `useFF` takes exactly one framework; `useFF = [preact(), react()]`
  stops the server at startup. With `useFF = preact()`, every `.tsx` file is Preact.
- **Pages are `.tsx`.** Only a `.tsx` file under `src/routes/` becomes a page; `.jsx` is fine for a
  component.
- **Components live outside `src/routes/`**, usually in `src/components/`, so they are not pages.
- **A server-mode project has no `.tsx` page**, and a client-mode project has no `.nexy` page: Nexy
  refuses to start and names the file. See [modes](../../routing/fbr/modes.md).
- **An `.mdx` page imports from `"preact"`.** Nexy compiles an `.mdx` file with Preact only when it
  sees that import, for example `import { h } from "preact"`, and with React otherwise. See [Markdown and MDX](../nexy/markdown.md).

## In this section

- [Pages](pages.md): a `.tsx` route, its export, its params, server rendering
- [Layouts](layouts.md): the root `layout.tsx` that owns `<html>`, nested layouts
- [Islands](islands.md): a Preact component inside a `.nexy` page
- [Actions and navigation](actions-and-navigation.md): call Python, link pages, read the URL

## Next steps

- [Views](../README.md): compare formats
- [Frontend](../../guides/frontend.md): Vite and the client build
