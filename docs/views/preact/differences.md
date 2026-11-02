# Preact

Nexy renders Preact 10 components on the server, then Preact takes them over in the browser. Pages,
layouts, islands and actions are the same in every framework: this page covers setup, then the parts
that differ from the [shared contracts](../frontend/pages.md).

| Mode | `nexyconfig.py` | Pages are | Preact is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](../../rendering/islands.md) inside those pages |
| Client | `useCSR = True` | `.tsx` files | the whole page, with [layouts](../frontend/layouts.md) and a client router |

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
  sees that import, for example `import { h } from "preact"`, and with React otherwise. See
  [Markdown and MDX](../nexy/markdown.md).

## Pages

In client mode (`useCSR = True`), a page is a `.tsx` file.

### Page component

A page is the default export of the file. If no default export exists, Nexy picks the first named
export.

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Dynamic segments

URL parameters are available via the `useParams` hook:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## Layouts

### Implementation

The root layout defines the document shell. Nested layouts wrap the content.

```tsx filename="src/routes/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## Islands

In server mode, a Preact component imported into a `.nexy` file is an island.

### Importing

Import components in the frontmatter of the `.nexy` file:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### Hydration directives

Use the `directive` prop to control when the island hydrates:

- `client:load` (default): immediately
- `client:idle`: when the browser is idle
- `client:visible`: when it scrolls into view
- `client:media`: when the media query matches

## Actions and navigation

### Calling actions

Use the `useAction` hook to manage the state of an action call:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### Navigation

Use the `Link` component for client-side transitions. Note that Preact uses `class` instead of
`className`:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

For programmatic navigation, use the `useRouter` hook:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL access

- `usePathname()`: current path
- `useParams()`: dynamic segments
- `useSearchParams()`: query string
- `useLocation()`: full location object

## Next steps

- [Views](../README.md): compare the formats a page can use
- [Frontend](../../guides/frontend.md): Vite and the client build
