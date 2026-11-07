# React

Nexy renders React 19 components on the server, then React hydrates them in the browser. Pages,
layouts, islands and actions are the same in every framework: this page covers setup, then the parts
that differ from the [shared contracts](../frontend/pages.md).

<!-- router:fbr,custom -->
| Mode | `nexyconfig.py` | Pages are | React is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](../../rendering/islands.md) inside those pages |
| Client | `useCSR = True` | `.tsx` files | the whole page, with [layouts](../frontend/layouts.md) and a client router |
<!-- /router -->

<!-- router:modular -->
With the modular router, React components are [islands](../../rendering/islands.md) inside
the `.nexy` views a controller returns: there is no page file and no client router.
<!-- /router -->

## Start a project

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-react
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-react
```
<!-- /router -->

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
<!-- router:fbr,custom -->
- **Pages are `.tsx`.** React owns `.tsx` and `.jsx` for components, but only a `.tsx` file under
  `src/routes/` becomes a page.
- **Components live outside `src/routes/`**, usually in `src/components/`, so they are not pages.
- **A server-mode project has no `.tsx` page**, and a client-mode project has no `.nexy` page: Nexy
  refuses to start and names the file. See [modes](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Components live in `src/components/`**, and a view imports them as islands.
<!-- /router -->

<!-- router:fbr,custom -->
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

The root layout defines the document shell. Nested layouts wrap the content below them.

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```
<!-- /router -->

## Islands

In server mode, a React component imported into a `.nexy` file is an island.

### Importing

Import components in the frontmatter of the `.nexy` file:

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

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

- `usePathname()`: current path
- `useParams()`: dynamic segments
- `useSearchParams()`: query string
- `useLocation()`: full location object

## Next steps

- [Views](../README.md): compare the formats a page can use
- [Frontend](../../guides/frontend.md): Vite and the client build
