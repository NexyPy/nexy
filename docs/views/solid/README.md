# Solid

Nexy renders Solid 1.9 components on the server, then Solid takes them over in the browser. A
project uses Solid in one of two ways:

| Mode | `nexyconfig.py` | Pages are | Solid is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](islands.md) inside those pages |
| Client | `useCSR = True` | `.tsx` files | the whole page, with [layouts](layouts.md) and a client router |

## Start a project

```bash
nx new my-app --template web-fbr-solid
```

The template is a server-mode project with Solid islands. Run `nx new my-app` without a template to
answer the prompts instead: the router, the project type, whether to use client-side routing, then
the framework.

## Enable Solid in an existing project

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

In client mode write `solid({ ssr: true })`: Solid compiles a component differently for the server
and for the browser, and client mode needs both. `nx new` writes this file; Nexy writes
`__nexy__/vite.ts` itself, so do not edit it.

| Package | Version `nx new` writes |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (dev dependency) |

## Think in signals

A Solid component function runs **once**. What changes later is read through a signal, and only the
expressions that read it update:

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- Call the signal, `count()`, inside the JSX, not in a variable above it.
- Read props as `props.start`. Destructuring `{ start }` reads the value once and loses the updates.
- Solid writes HTML attributes: `class`, `for`, `charset`, not `className`.

## Rules

- **One framework per project.** `useFF` takes exactly one framework; `useFF = [solid(), react()]`
  stops the server at startup. With `useFF = solid()`, every `.tsx` file is Solid.
- **Pages are `.tsx`.** Only a `.tsx` file under `src/routes/` becomes a page; `.jsx` is fine for a
  component.
- **Components live outside `src/routes/`**, usually in `src/components/`, so they are not pages.
- **A server-mode project has no `.tsx` page**, and a client-mode project has no `.nexy` page: Nexy
  refuses to start and names the file. See [modes](../../routing/fbr/modes.md).
- **No `.mdx` with Solid.** MDX compiles to React or Preact; `.md` pages work.

## In this section

- [Pages](pages.md): a `.tsx` route, its export, its params, server rendering
- [Layouts](layouts.md): the root `layout.tsx` that owns `<html>`, nested layouts
- [Islands](islands.md): a Solid component inside a `.nexy` page
- [Actions and navigation](actions-and-navigation.md): call Python, link pages, read the URL

## Next steps

- [Views](../README.md): compare formats
- [Frontend](../../guides/frontend.md): Vite and the client build
