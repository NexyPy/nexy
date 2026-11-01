# Solid

Nexy renders Solid 1.9 components on the server, then Solid takes them over in the browser. Pages,
layouts, islands and actions are the same in every framework: this page covers setup, then the parts
that differ from the [shared contracts](../frontend/pages.md).

| Mode | `nexyconfig.py` | Pages are | Solid is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](../frontend/islands.md) inside those pages |
| Client | `useCSR = True` | `.tsx` files | the whole page, with [layouts](../frontend/layouts.md) and a client router |

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

URL parameters are available via the `useParams` hook, which returns an accessor:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## Layouts

### Implementation

The root layout defines the document shell. Nested layouts wrap the content.

```tsx filename="src/routes/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

Do not destructure `props.children`, as Solid reads it lazily.

## Islands

In server mode, a Solid component imported into a `.nexy` file is an island.

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

Use the `useAction` hook to manage the state of an action call. In Solid, this returns accessors (call
them as functions).

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
```

### Navigation

Use the `Link` component for client-side transitions:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

For programmatic navigation, use the `useRouter` hook:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL access

All location hooks return accessors:

- `usePathname()`: current path
- `useParams()`: dynamic segments
- `useSearchParams()`: query string
- `useLocation()`: full location object

## Next steps

- [Views](../README.md): compare the formats a page can use
- [Frontend](../../guides/frontend.md): Vite and the client build
